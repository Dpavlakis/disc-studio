"""Publish the reviewed construction to the local studio model set."""
from pathlib import Path
import json,struct,math
import numpy as np
root=Path(__file__).resolve().parents[1]/'outputs'
raw=(root/'previews/gamecube-disc-preview.glb').read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);binary=raw[28+n:]
# Batch the hundreds of small mastering bars by material to avoid hundreds
# of independent draw calls in the live viewer.
payload=bytearray(binary);groups={}
for mesh in g['meshes']:
 for primitive in mesh['primitives']:
  group=groups.setdefault(primitive['material'],{})
  for key,index in primitive['attributes'].items():
   a=g['accessors'][index];v=g['bufferViews'][a['bufferView']];width={'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
   array=np.frombuffer(binary,dtype='<f4',count=a['count']*width,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,width)
   group.setdefault(key,[]).append(array)
meshes=[]
for material,attributes in groups.items():
 attrs={}
 for key,arrays in attributes.items():
  a=np.concatenate(arrays);data=a.tobytes()
  while len(payload)%4:payload.append(0)
  g['bufferViews'].append({'buffer':0,'byteOffset':len(payload),'byteLength':len(data)});payload.extend(data)
  attrs[key]=len(g['accessors']);g['accessors'].append({'bufferView':len(g['bufferViews'])-1,'componentType':5126,'count':len(a),'type':'VEC'+str(a.shape[1]),'min':a.min(axis=0).tolist(),'max':a.max(axis=0).tolist()})
 meshes.append({'name':g['materials'][material]['name'],'primitives':[{'material':material,'attributes':attrs}]})
g['meshes']=meshes;g['nodes']=[{'name':m['name'],'mesh':i} for i,m in enumerate(meshes)];g['scenes']=[{'nodes':list(range(len(meshes)))}]
binary=payload;g['buffers'][0]['byteLength']=len(binary)
# Discard the superseded unbatched geometry instead of embedding it twice.
used=sorted({a for mesh in meshes for primitive in mesh['primitives'] for a in primitive['attributes'].values()})
accessorMap={old:i for i,old in enumerate(used)};g['accessors']=[g['accessors'][i] for i in used]
for mesh in meshes:
 for primitive in mesh['primitives']:primitive['attributes']={k:accessorMap[v] for k,v in primitive['attributes'].items()}
usedViews=sorted({a['bufferView'] for a in g['accessors']}|{i['bufferView'] for i in g['images']})
compact=bytearray();views=[];viewMap={}
for old in usedViews:
 v=g['bufferViews'][old]
 while len(compact)%4:compact.append(0)
 viewMap[old]=len(views);views.append({'buffer':0,'byteOffset':len(compact),'byteLength':v['byteLength']});compact.extend(binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']])
for a in g['accessors']:a['bufferView']=viewMap[a['bufferView']]
for image in g['images']:image['bufferView']=viewMap[image['bufferView']]
g['bufferViews']=views;binary=compact;g['buffers'][0]['byteLength']=len(binary)
for node in g['nodes']:
 node['rotation']=[-math.sqrt(.5),0,0,math.sqrt(.5)];node['translation']=[0,.06,0]
g['extras']['previewOnly']=False
g['extras']['artworkInkOpacity']=.94
from clear_plastic_finish import apply_clear_plastic_finish
apply_clear_plastic_finish(g)
j=json.dumps(g,separators=(',',':')).encode();j+=b' '*((-len(j))%4)
(root/'gamecube-disc.glb').write_bytes(struct.pack('<III',0x46546c67,2,28+len(j)+len(binary))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(binary),0x004e4942)+binary)
print('Released upright GameCube model at its physical 80 mm diameter.')
