"""Give GameCube matrix text and dashes the existing disc material response."""
import copy,json,struct
import numpy as np
from embed_default_labels import ROOT,load

def update(path):
 g,raw=load(path)
 if g.get('extras',{}).get('gamecubeDiscMatchedSecurityVersion')==1:return
 blob=bytearray(raw);data=next(m for m in g['materials'] if m['name']=='GAMECUBE_SILVER_DATA_UNDERSIDE')
 targets={'SUBTLE_FRONT_Irregular_security_bars','GAMECUBE_REAR_VECTOR_MASTERING_TEXT','GAMECUBE_FRONT_THROUGH_MASTERING_TEXT'}
 def read(p,key):
  a=g['accessors'][p['attributes'][key]];v=g['bufferViews'][a['bufferView']];w={'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
  return np.frombuffer(blob,dtype='<f4',count=a['count']*w,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,w).copy()
 def acc(a,kind):
  a=np.asarray(a,dtype='<f4');blob.extend(b'\0'*((-len(blob))%4));vi=len(g['bufferViews']);g['bufferViews'].append({'buffer':0,'byteOffset':len(blob),'byteLength':a.nbytes});blob.extend(a.tobytes())
  ai=len(g['accessors']);g['accessors'].append({'bufferView':vi,'componentType':5126,'count':len(a),'type':kind,'min':a.min(axis=0).tolist(),'max':a.max(axis=0).tolist()});return ai
 base=next(m for m in g['meshes'] if m['name']=='GAMECUBE_SILVER_DATA_UNDERSIDE')['primitives'][0]
 pos=read(base,'POSITION');uv=read(base,'TEXCOORD_0');normal=read(base,'NORMAL');rear=normal[:,1]<-.9
 projection=np.linalg.lstsq(np.column_stack((pos[rear,0],pos[rear,2],np.ones(rear.sum()))),uv[rear],rcond=None)[0]
 assert np.max(np.abs(np.column_stack((pos[rear,0],pos[rear,2],np.ones(rear.sum())))@projection-uv[rear]))<1e-5
 for i,m in enumerate(g['materials']):
  if m['name'] in targets:
   matched=copy.deepcopy(data);matched['name']=m['name'];g['materials'][i]=matched
 for mesh in g['meshes']:
  for p in mesh['primitives']:
   if g['materials'][p['material']]['name'] not in targets:continue
   pos=read(p,'POSITION');p['attributes']['TEXCOORD_0']=acc(np.column_stack((pos[:,0],pos[:,2],np.ones(len(pos))))@projection,'VEC2')
   if 'COLOR_0' in p['attributes']:
    colors=read(p,'COLOR_0');colors[:,3]=1;p['attributes']['COLOR_0']=acc(colors,'VEC4')
 g.setdefault('extras',{})['gamecubeDiscMatchedSecurityVersion']=1
 g['buffers'][0]['byteLength']=len(blob);j=json.dumps(g,separators=(',',':')).encode();j+=b' '*((-len(j))%4);blob.extend(b'\0'*((-len(blob))%4))
 path.write_bytes(struct.pack('<III',0x46546c67,2,28+len(j)+len(blob))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(blob),0x004e4942)+blob)
 print('GameCube security dashes and ring text now use the disc finish; clear moulded hub lettering retained.')
if __name__=='__main__':update(ROOT/'outputs/gamecube-disc.glb')
