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
 # Eight samples per groove; 128 periods per repeat, eight repeats per disc.
 # The tangent-space normal alters reflections only, never vertex depth.
 phase = np.arange(1024) * (2*np.pi/8)
 slope = .62*np.cos(phase)
 pixels = np.zeros((1024, 64, 3), dtype=np.uint8)
 pixels[:,:,0] = 128
 pixels[:,:,1] = np.rint(127.5+127.5*slope[:,None]).astype('uint8')
 pixels[:,:,2] = np.rint(127.5+127.5*np.sqrt(1-slope[:,None]**2)).astype('uint8')
 rough = np.zeros_like(pixels); rough[:,:,0] = 255
 rough[:,:,1] = np.rint(245+10*np.sin(phase)[:,None]).astype('uint8')
 # Blue = zero metalness. Green times .52 = .479 to .52 roughness.
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
 assert current.pop('normalTexture') == {'index':normal, 'scale':.075, 'extensions':transform}
 pbr = current['pbrMetallicRoughness']
 assert pbr.pop('metallicRoughnessTexture') == {'index':rough, 'extensions':transform}
 assert pbr['roughnessFactor'] == .52 and pbr['metallicFactor'] == 0
 pbr['roughnessFactor'] = original['pbrMetallicRoughness']['roughnessFactor']
 extensions = current['extensions']; assert extensions.pop('KHR_materials_anisotropy') == {'anisotropyStrength':.18, 'anisotropyRotation':0}
 if not extensions and 'extensions' not in original:current.pop('extensions')
 assert current == original, 'Unexpected artwork/material change outside printed surface finish'
 return original

def update(path):
 g, blob = load(path)
 if g.get('extras', {}).get('printedInkFinish', {}).get('version') == 1:return
 originals = {str(i):copy.deepcopy(m) for i,m in enumerate(g['materials']) if m['name'] in NAMES}
 if not originals:return
 before = bytes(blob); image_count = len(g['images']); textures=[]
 sampler = len(g.setdefault('samplers', []))
 g['samplers'].append({'magFilter':9729, 'minFilter':9987, 'wrapS':10497, 'wrapT':10497})
 for name, data in maps():
  (ROOT/'outputs'/name).write_bytes(data)
  blob.extend(b'\0'*((-len(blob))%4)); view=len(g['bufferViews'])
  g['bufferViews'].append({'buffer':0, 'byteOffset':len(blob), 'byteLength':len(data)})
  blob.extend(data); image=len(g['images']); g['images'].append({'name':name, 'bufferView':view, 'mimeType':'image/png'})
  textures.append(len(g['textures'])); g['textures'].append({'source':image, 'sampler':sampler})
 for key in originals:
  m=g['materials'][int(key)]; p=m['pbrMetallicRoughness']; p['metallicFactor']=0; p['roughnessFactor']=.52
  p['metallicRoughnessTexture']={'index':textures[1], 'extensions':{'KHR_texture_transform':{'scale':[8,8]}}}
  m['normalTexture']={'index':textures[0], 'scale':.075, 'extensions':{'KHR_texture_transform':{'scale':[8,8]}}}
  m.setdefault('extensions', {})['KHR_materials_anisotropy']={'anisotropyStrength':.18, 'anisotropyRotation':0}
 for ext in ['KHR_texture_transform', 'KHR_materials_anisotropy']:
  if ext not in g.setdefault('extensionsUsed', []):g['extensionsUsed'].append(ext)
 g.setdefault('extras', {})['printedInkFinish']={'version':1, 'originalMaterials':originals, 'images':list(range(image_count,len(g['images']))), 'textures':textures, 'originalBufferBytes':len(before), 'originalBufferSha256':hashlib.sha256(before).hexdigest(), 'groovesAcrossDisc':1024}
 for key in originals:surface_reference(g,int(key))
 assert bytes(blob[:len(before)])==before
 g['buffers'][0]['byteLength']=len(blob); j=json.dumps(g,separators=(',',':')).encode(); j+=b' '*((-len(j))%4); blob.extend(b'\0'*((-len(blob))%4))
 path.write_bytes(struct.pack('<III',0x46546c67,2,28+len(j)+len(blob))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(blob),0x004e4942)+blob)
 print(path.name+': satin printed ink, fine parallel normal map; original artwork/geometry bytes preserved.')

if __name__=='__main__':
 for path in (ROOT/'outputs').glob('*.glb'):update(path)
