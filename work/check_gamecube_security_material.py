import copy
import numpy as np
from embed_default_labels import ROOT,load
g,b=load(ROOT/'outputs/gamecube-disc.glb')
data=next(m for m in g['materials'] if m['name']=='GAMECUBE_SILVER_DATA_UNDERSIDE')
names={'SUBTLE_FRONT_Irregular_security_bars','GAMECUBE_REAR_VECTOR_MASTERING_TEXT','GAMECUBE_FRONT_THROUGH_MASTERING_TEXT'}
for m in g['materials']:
 if m['name'] not in names:continue
 response=copy.deepcopy(m);response['name']=data['name'];assert response==data
for mesh in g['meshes']:
 for p in mesh['primitives']:
  if g['materials'][p['material']]['name'] not in names:continue
  if 'COLOR_0' in p['attributes']:
   a=g['accessors'][p['attributes']['COLOR_0']];v=g['bufferViews'][a['bufferView']]
   colors=np.frombuffer(b,dtype='<f4',count=a['count']*4,offset=v.get('byteOffset',0)).reshape(-1,4)
   assert np.all(colors[:,3]==1), 'Security marks must retain full disc opacity.'
clear=next(m for m in g['materials'] if m['name']=='GAMECUBE_REAR_MOULDED_CLEAR_LETTERING')
assert clear['extensions']['KHR_materials_transmission']['transmissionFactor']==.93
print('GameCube ring text and both sides of the security dashes match the disc response at full strength; clear hub moulding preserved.')
