"""Soften front GameCube security markings while preserving the read side and rim."""
from pathlib import Path
import copy,json,struct
import numpy as np

def soften(path):
 raw=path.read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);blob=bytearray(raw[28+n:])
 if g.get('extras',{}).get('subtleFrontSecurityVersion')==1:return
 profiles={'GAMECUBE_DARK_FACE_SUBSTRATE':.16,'Irregular_security_bars':.30,'One_fine_security_circle':.12,'GAMECUBE_ANGLE_DEPENDENT_FINE_ETCH':.12}
 for mesh in g['meshes']:
  if mesh['name'] not in profiles:continue
  for primitive in mesh['primitives']:
   ai=primitive['attributes']['POSITION'];a=g['accessors'][ai];v=g['bufferViews'][a['bufferView']];assert a['componentType']==5126 and 'byteStride' not in v
   pos=np.frombuffer(blob,dtype='<f4',count=a['count']*3,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,3).copy()
   colors=np.ones((len(pos),4),dtype='<f4');front=pos[:,1]>0
   if mesh['name']=='GAMECUBE_DARK_FACE_SUBSTRATE':front&=np.hypot(pos[:,0],pos[:,2])<.023
   colors[front,3]=profiles[mesh['name']]
   # Separate bar material: the main silver data surface remains untouched.
   material=copy.deepcopy(g['materials'][primitive['material']]);material['name']='SUBTLE_FRONT_'+mesh['name'];material['alphaMode']='BLEND';material.pop('alphaCutoff',None)
   primitive['material']=len(g['materials']);g['materials'].append(material)
   blob.extend(b'\0'*((-len(blob))%4));vi=len(g['bufferViews']);g['bufferViews'].append({'buffer':0,'byteOffset':len(blob),'byteLength':colors.nbytes});blob.extend(colors.tobytes());ai=len(g['accessors']);g['accessors'].append({'bufferView':vi,'componentType':5126,'type':'VEC4','count':len(colors),'min':colors.min(axis=0).tolist(),'max':colors.max(axis=0).tolist()});primitive['attributes']['COLOR_0']=ai
 for material in g['materials']:
  if material['name']=='GAMECUBE_SECURITY_LETTERING_AND_FAINT_EDGE':material['pbrMetallicRoughness']['baseColorFactor'][3]=.22
 g.setdefault('extras',{})['subtleFrontSecurityVersion']=1;g['buffers'][0]['byteLength']=len(blob);j=json.dumps(g,separators=(',',':')).encode();j+=b' '*((-len(j))%4);blob.extend(b'\0'*((-len(blob))%4));path.write_bytes(struct.pack('<III',0x46546c67,2,28+len(j)+len(blob))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(blob),0x004e4942)+blob)
 print('GameCube front security softened; rear foil and black perimeter retained.')
if __name__=='__main__':soften(Path(__file__).resolve().parents[1]/'outputs/gamecube-disc.glb')
