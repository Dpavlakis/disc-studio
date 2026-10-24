"""Replace embedded placeholder cover images; preserve geometry and optics."""
from pathlib import Path
import json,struct,copy,hashlib
ROOT=Path(__file__).resolve().parents[1]
SYSTEMS={'ps1-black-disc':'ps1','ps2-blue-disc':'ps2','ps2-silver-disc':'ps2','ps2-gold-disc':'ps2','ps3-silver-disc':'ps3','ps4-silver-disc':'ps4','xbox-original-disc':'xbox','xbox-original-disc-matched':'xbox','xbox360-silver-disc':'x360','xbox360-test':'x360','xbox360-disc-matched':'x360','gamecube-disc':'gc'}

def load(path):
 raw=path.read_bytes();n=struct.unpack_from('<I',raw,12)[0]
 return json.loads(raw[20:20+n]),raw[28+n:]

def geometry(g,b):
 result={}
 for i,a in enumerate(g['accessors']):
  v=g['bufferViews'][a['bufferView']];o=v.get('byteOffset',0)
  result[i]=hashlib.sha256(b[o:o+v['byteLength']]).hexdigest()
 return result

def update(path):
 g,b=load(path);before=geometry(g,b);meshes=copy.deepcopy(g['meshes'])
 payloads=[b[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']] for v in g['bufferViews']]
 changed_images=[];changed=False
 for m in g['materials']:
  if m['name'] not in {'TOP_ART_REPLACE_THIS_TEXTURE','TOP_PERMANENT_PS2_BRANDING'}:continue
  p=m['pbrMetallicRoughness'];key='ps2-branding' if m['name']=='TOP_PERMANENT_PS2_BRANDING' else SYSTEMS[path.stem]
  data=(ROOT/'outputs/default-labels'/(key+'.png')).read_bytes()
  if 'baseColorTexture' not in p:
   image=len(g['images']);view=len(g['bufferViews']);texture=len(g['textures'])
   g['bufferViews'].append({'buffer':0,'byteOffset':0,'byteLength':len(data)});payloads.append(data)
   g['images'].append({'bufferView':view,'mimeType':'image/png'});g['textures'].append({'source':image,'sampler':g['textures'][0].get('sampler',0)})
   p['baseColorTexture']={'index':texture};changed=True
  else:
   image=g['textures'][p['baseColorTexture']['index']]['source'];view=g['images'][image]['bufferView']
   if payloads[view]!=data:payloads[view]=data;changed=True;changed_images.append(image)
  if path.stem=='gamecube-disc':
   if p.get('baseColorFactor')!=[1,1,1,.94] or m.get('alphaMode')!='BLEND':changed=True
   p['baseColorFactor']=[1,1,1,.94];m['alphaMode']='BLEND'
 # GameCube's extra branding belongs to uploaded art, not the new starter cover.
 if path.stem=='gamecube-disc':
  for m in g['materials']:
   if m['name'] in {'GAMECUBE_LABEL_PANEL','GAMECUBE_LABEL_FOIL'}:
    factor=m['pbrMetallicRoughness']['baseColorFactor']
    if factor[3]!=0:factor[3]=0;changed=True
 if not changed:return []
 # Repack the existing views, replacing image bytes rather than retaining an
 # old label elsewhere in the binary. Accessor indices and contents stay intact.
 blob=bytearray()
 for view,data in zip(g['bufferViews'],payloads):
  blob.extend(b'\0'*((-len(blob))%4));view['byteOffset']=len(blob);view['byteLength']=len(data);blob.extend(data)
 g.setdefault('extras',{})['approvedDefaultCoverVersion']=1
 g['buffers'][0]['byteLength']=len(blob);blob.extend(b'\0'*((-len(blob))%4))
 assert geometry(g,blob)==before and g['meshes']==meshes
 j=json.dumps(g,separators=(',',':')).encode();j+=b' '*((-len(j))%4)
 path.write_bytes(struct.pack('<III',0x46546c67,2,28+len(j)+len(blob))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(blob),0x004e4942)+blob)
 print(path.name+': embedded cover replaced; geometry bytes verified unchanged.')
 return changed_images

if __name__=='__main__':
 for name in SYSTEMS:update(ROOT/'outputs'/(name+'.glb'))
