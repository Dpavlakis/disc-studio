"""Expose a proper reflective front when the artwork layer is hidden."""
from pathlib import Path
import json,struct,copy,math
import numpy as np
from build_modern_playstation import load,ROOT
from refine_original_xbox_mastering import fingerprint
TARGETS=['ps3-silver-disc','ps4-silver-disc','xbox-original-disc','xbox360-silver-disc','xbox360-test']
def front_name(g):return next(m['name'] for m in g['meshes'] if ('Exposed_Silver_Between_Artwork' in m['name']) or m['name']=='Closed_Outer_Laminate_Edge')
def protected_front(g,b):
 doc=copy.deepcopy(g);target=front_name(g);doc['meshes']=[m for m in doc['meshes'] if m['name']!=target];return fingerprint(doc,b)
def update(path):
 g,blob=load(path);extra=g.setdefault('extras',{})
 if extra.get('bareFrontSurfaceVersion')==1:return
 before=protected_front(g,blob);baseline=ROOT/'work'/(path.stem+'-bare-front-baseline.json')
 if not baseline.exists():baseline.write_text(json.dumps(before,indent=2))
 og,_=load(ROOT/'outputs/xbox-original-disc.glb');mirror=copy.deepcopy(next(m for m in og['materials'] if m['name']=='ORIGINAL_XBOX_TEST_PLAIN_REFLECTIVE_SILVER'))
 if path.name.startswith(('ps3-','ps4-')):
  for m in g['materials']:
   if m['name'] in ['PS2_FRONT_DATA_BACKING','PS2_FRONT_MATRIX_BACKING']:
    name=path.stem[:3].upper()+'_PLAIN_MIRROR_FRONT_'+('DATA' if 'DATA' in m['name'] else 'HUB');m.clear();m.update(copy.deepcopy(mirror));m['name']=name
 else:
  target=next(m for m in g['meshes'] if m['name']==front_name(g));material=copy.deepcopy(mirror);material['name']='BARE_FRONT_XBOX_MIRROR_SURFACE';mi=len(g['materials']);g['materials'].append(material)
  # Below artwork at +0.61 mm; above the internal cap at +0.40 mm.
  # Preserve the front centre foil and raised bezel inside 16.7 mm.
  pos=[];norm=[];uv=[];tan=[]
  for i in range(1440):
   a=i*math.tau/1440;b=(i+1)*math.tau/1440;corners=[(r*math.sin(t),.0006,r*math.cos(t)) for r,t in [(.0167,a),(.0594,a),(.0594,b),(.0167,b)]]
   for k in [0,1,2,0,2,3]:
    x,y,z=corners[k];pos.append((x,y,z));norm.append((0,1,0));uv.append((.5-x/.12,.5-z/.12));tan.append((1,0,0,1))
  def acc(data,kind):
   arr=np.asarray(data,dtype='<f4');blob.extend(b'\0'*((-len(blob))%4));vi=len(g['bufferViews']);g['bufferViews'].append({'buffer':0,'byteOffset':len(blob),'byteLength':arr.nbytes});blob.extend(arr.tobytes());ai=len(g['accessors']);g['accessors'].append({'bufferView':vi,'componentType':5126,'count':len(arr),'type':kind,'min':arr.min(axis=0).tolist(),'max':arr.max(axis=0).tolist()});return ai
  target['primitives']=[{'material':mi,'attributes':{key:acc(arr,kind) for key,arr,kind in [('POSITION',pos,'VEC3'),('NORMAL',norm,'VEC3'),('TEXCOORD_0',uv,'VEC2'),('TANGENT',tan,'VEC4')]}}]
 extra['bareFrontSurfaceVersion']=1;extra['bareFrontSurfaceFix']='Plain reflective front below artwork; no PS2 watermark; approved rear and centre retained'
 assert protected_front(g,blob)==before
 g['buffers'][0]['byteLength']=len(blob);j=json.dumps(g,separators=(',',':')).encode();j+=b' '*((-len(j))%4);blob.extend(b'\0'*((-len(blob))%4));path.write_bytes(struct.pack('<III',0x46546c67,2,28+len(j)+len(blob))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(blob),0x004e4942)+blob)
 print(path.name+': bare front repaired; approved centre, rear, artwork and assets preserved.')
if __name__=='__main__':
 for name in TARGETS:update(ROOT/'outputs'/(name+'.glb'))
