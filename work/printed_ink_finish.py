"""Add a tileable satin ink response without altering artwork or geometry."""
from pathlib import Path
import copy, io, json, struct, hashlib
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
NAMES = {'TOP_ART_REPLACE_THIS_TEXTURE', 'TOP_PERMANENT_PS2_BRANDING'}

def load(path):
 raw = path.read_bytes(); n = struct.unpack_from('<I', raw, 12)[0]
 return json.loads(raw[20:20+n]), bytearray(raw[28+n:])

def maps():
 # A diagonal, tileable screen of rounded ink dots, not one-dimensional lines.
 # 64 cells per repeat; the diagonal screen resolves to about 724 dots/disc.
 y,x=np.indices((1024,1024),dtype=float)
 u=((x+y)/16+.5)%1-.5; v=((x-y)/16+.5)%1-.5
 ink=np.exp(-(u*u+v*v)/.035)
 nx=5*ink*(u+v); ny=5*ink*(u-v)
 length=np.sqrt(1+nx*nx+ny*ny)
 pixels=np.rint(127.5+127.5*np.stack((nx/length,ny/length,1/length),axis=-1)).astype('uint8')
 rough=np.zeros_like(pixels);rough[:,:,0]=255
 rough[:,:,1]=np.rint(249-10*ink).astype('uint8')
 # Blue = zero metalness. The dot tips have slightly smoother ink response.
 result = []
 for name, data in [('printed-ink-normal.png', pixels), ('printed-ink-roughness.png', rough)]:
  out = io.BytesIO(); Image.fromarray(data).save(out, format='PNG')
  result.append((name, out.getvalue()))
 return result

def surface_reference(g, index):
 """Verify the allowed surface-only delta, then return its original for optical checks."""
 entry = g.get('extras', {}).get('printedInkFinish', {}).get('originalMaterials', {}).get(str(index))
 if entry is None:return g['materials'][index]
 current = copy.deepcopy(g['materials'][index]); original = entry
 assert current['name'] in NAMES
 finish = g['extras']['printedInkFinish']; normal, rough = finish['textures']
 transform = {'KHR_texture_transform': {'scale': [8, 8]}}
 assert current.pop('normalTexture') == {'index':normal, 'scale':.05, 'extensions':transform}
 pbr = current['pbrMetallicRoughness']
 assert pbr.pop('metallicRoughnessTexture') == {'index':rough, 'extensions':transform}
 assert pbr['roughnessFactor'] == .52 and pbr['metallicFactor'] == 0
 pbr['roughnessFactor'] = original['pbrMetallicRoughness']['roughnessFactor']
 extensions = current['extensions']; assert extensions.pop('KHR_materials_anisotropy') == {'anisotropyStrength':0, 'anisotropyRotation':0}
 if not extensions and 'extensions' not in original:current.pop('extensions')
 assert current == original, 'Unexpected artwork/material change outside printed surface finish'
 return original

def update(path):
 g, blob = load(path)
 previous=g.get('extras',{}).get('printedInkFinish')
 if previous and previous.get('version')==2:return
 originals=previous['originalMaterials'] if previous else {str(i):copy.deepcopy(m) for i,m in enumerate(g['materials']) if m['name'] in NAMES}
 if not originals:return
 before=bytes(blob)
 if previous:
  textures=previous['textures'];images=previous['images']
 else:
  textures=[];images=[];sampler=len(g.setdefault('samplers',[]))
  g['samplers'].append({'magFilter':9729,'minFilter':9987,'wrapS':10497,'wrapT':10497})
 for n,(name,data) in enumerate(maps()):
  (ROOT/'outputs'/name).write_bytes(data)
  blob.extend(b'\0'*((-len(blob))%4));view=len(g['bufferViews'])
  g['bufferViews'].append({'buffer':0,'byteOffset':len(blob),'byteLength':len(data)});blob.extend(data)
  if previous:
   # Keep texture indices and the original buffer intact during migration.
   g['images'][images[n]]={'name':name,'bufferView':view,'mimeType':'image/png'}
  else:
   images.append(len(g['images']));g['images'].append({'name':name,'bufferView':view,'mimeType':'image/png'})
   textures.append(len(g['textures']));g['textures'].append({'source':images[-1],'sampler':sampler})
 for key in originals:
  m=g['materials'][int(key)];p=m['pbrMetallicRoughness'];p['metallicFactor']=0;p['roughnessFactor']=.52
  p['metallicRoughnessTexture']={'index':textures[1],'extensions':{'KHR_texture_transform':{'scale':[8,8]}}}
  m['normalTexture']={'index':textures[0],'scale':.05,'extensions':{'KHR_texture_transform':{'scale':[8,8]}}}
  m.setdefault('extensions',{})['KHR_materials_anisotropy']={'anisotropyStrength':0,'anisotropyRotation':0}
 for ext in ['KHR_texture_transform','KHR_materials_anisotropy']:
  if ext not in g.setdefault('extensionsUsed',[]):g['extensionsUsed'].append(ext)
 g.setdefault('extras',{})['printedInkFinish']={'version':2,'pattern':'diagonal halftone dots','originalMaterials':originals,'images':images,'textures':textures,'originalBufferBytes':previous['originalBufferBytes'] if previous else len(before),'originalBufferSha256':previous['originalBufferSha256'] if previous else hashlib.sha256(before).hexdigest(),'dotsAcrossDiscApprox':724}
 for key in originals:surface_reference(g,int(key))
 assert bytes(blob[:len(before)])==before
 g['buffers'][0]['byteLength']=len(blob);j=json.dumps(g,separators=(',',':')).encode();j+=b' '*((-len(j))%4);blob.extend(b'\0'*((-len(blob))%4))
 path.write_bytes(struct.pack('<III',0x46546c67,2,28+len(j)+len(blob))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(blob),0x004e4942)+blob)
 print(path.name+': fine diagonal halftone dots; original artwork/geometry bytes preserved.')

if __name__=='__main__':
 for path in (ROOT/'outputs').glob('*.glb'):update(path)
