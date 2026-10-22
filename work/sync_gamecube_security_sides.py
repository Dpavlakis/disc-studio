"""Derive front see-through mastering details from the actual approved rear geometry."""
from pathlib import Path
import json,struct,copy
import numpy as np

def synchronize(path):
 raw=path.read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);blob=bytearray(raw[28+n:])
 if g.get('extras',{}).get('matchedFrontRearSecurityVersion')==1:return
 def read(i):
  a=g['accessors'][i];v=g['bufferViews'][a['bufferView']];w={'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];return np.frombuffer(blob,dtype='<f4',count=a['count']*w,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,w).copy()
 def acc(data):
  a=np.asarray(data,dtype='<f4');blob.extend(b'\0'*((-len(blob))%4));vi=len(g['bufferViews']);g['bufferViews'].append({'buffer':0,'byteOffset':len(blob),'byteLength':a.nbytes});blob.extend(a.tobytes());i=len(g['accessors']);g['accessors'].append({'bufferView':vi,'componentType':5126,'count':len(a),'type':'VEC'+str(a.shape[1]),'min':a.min(axis=0).tolist(),'max':a.max(axis=0).tolist()});return i
 def arrays(p):return {key:read(i) for key,i in p['attributes'].items()}
 def mirror(a,offset=0):
  result={k:v.copy() for k,v in a.items()};result['POSITION'][:,1]=-result['POSITION'][:,1]+offset;result['NORMAL'][:,1]*=-1
  if 'TANGENT' in result:result['TANGENT'][:,1]*=-1;result['TANGENT'][:,3]*=-1
  # Reflection changes handedness; reverse triangle winding. X and Z stay
  # physically aligned, so opposite camera sides naturally reverse the text.
  return {k:v.reshape(-1,3,v.shape[1])[:,[0,2,1],:].reshape(-1,v.shape[1]) for k,v in result.items()}
 def prim(a,mi):return {'material':mi,'attributes':{k:acc(v) for k,v in a.items()}}
 def source(name):return next(p for m in g['meshes'] for p in m['primitives'] if g['materials'][p['material']]['name']==name)
 def subtle(mi,name,alpha):
  material=copy.deepcopy(g['materials'][mi]);material['name']=name;material['alphaMode']='BLEND';material['pbrMetallicRoughness'].setdefault('baseColorFactor',[1,1,1,1])[3]=alpha;g['materials'].append(material);return len(g['materials'])-1
 # The front and reverse now share exactly the same random sequence/placement.
 bars=next(m for m in g['meshes'] if m['name']=='Irregular_security_bars')
 for p in bars['primitives']:
  a=arrays(p);mask=(a['POSITION'].reshape(-1,3,3)[:,:,1]<0).all(axis=1);rear={k:v.reshape(len(mask),3,-1)[mask].reshape(-1,v.shape[1]) for k,v in a.items()};front=mirror(rear,.000105);front['COLOR_0'][:,3]=.30;p['attributes']={k:acc(np.concatenate((rear[k],front[k]))) for k in rear}
 # Native glyphs replace the old, independently arranged front texture.
 rear=source('GAMECUBE_REAR_VECTOR_MASTERING_TEXT');mi=subtle(rear['material'],'GAMECUBE_FRONT_THROUGH_MASTERING_TEXT',.22);next(m for m in g['meshes'] if m['name']=='GAMECUBE_SECURITY_LETTERING_AND_FAINT_EDGE')['primitives']=[prim(mirror(arrays(rear),.0001),mi)]
 rear=source('GAMECUBE_REAR_POLISHED_SECURITY_BOUNDARY');mi=subtle(rear['material'],'GAMECUBE_FRONT_THROUGH_SECURITY_BOUNDARY',.12);next(m for m in g['meshes'] if m['name']=='One_fine_security_circle')['primitives']=[prim(mirror(arrays(rear),.0001),mi)]
 clear=next(m for m in g['meshes'] if m['name']=='GAMECUBE_CLEAR_POLYCARBONATE');old=clear['primitives'][0];a=arrays(old);tri=a['POSITION'].reshape(-1,3,3);r=np.hypot(tri[:,:,0],tri[:,:,2]);legacy=(r.min(axis=1)>.0086)&(r.max(axis=1)<.0095)&(tri[:,:,1].max(axis=1)>.0006005)&(tri[:,:,1].min(axis=1)>0)&(tri[:,:,1].max(axis=1)<.00063)
 old['attributes']={k:acc(v.reshape(len(legacy),3,-1)[~legacy].reshape(-1,v.shape[1])) for k,v in a.items()}
 rear=source('GAMECUBE_REAR_MOULDED_CLEAR_LETTERING');clear['primitives'].append(prim(mirror(arrays(rear)),rear['material']))
 g.setdefault('extras',{})['matchedFrontRearSecurityVersion']=1;g['extras']['legacyFrontMouldTrianglesRemoved']=int(legacy.sum());g['extras']['frontThroughSecurity']='Derived by reflecting rear Y and winding; same X/Z footprints, glyph sizes, spacing and barcode sequence. Front opacity retained.'
 g['buffers'][0]['byteLength']=len(blob);j=json.dumps(g,separators=(',',':')).encode();j+=b' '*((-len(j))%4);blob.extend(b'\0'*((-len(blob))%4));path.write_bytes(struct.pack('<III',0x46546c67,2,28+len(j)+len(blob))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(blob),0x004e4942)+blob)
 print('Front now shows mirrored rear glyphs, polished boundaries, mould lettering and identical bar sequence.')
if __name__=='__main__':synchronize(Path(__file__).resolve().parents[1]/'outputs/gamecube-disc.glb')
