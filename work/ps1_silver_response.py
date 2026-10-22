"""Transfer the approved Xbox optical material to the PS1 silver face only."""
import copy,json,struct
from pathlib import Path

def apply_xbox_silver_response(g,blob,root):
 raw=(Path(root)/'xbox-original-disc.glb').read_bytes();size=struct.unpack_from('<I',raw,12)[0]
 source=json.loads(raw[20:20+size]);binary=raw[28+size:]
 optical=copy.deepcopy(source['materials'][1]);optical['name']='PS1_FRONT_MASTERING_FOIL';optical['doubleSided']=False
 def texture(index):
  original=source['textures'][index];image=source['images'][original['source']]
  name='PS1_XBOX_OPTICAL_'+str(index)
  existing=next((i for i,item in enumerate(g['images']) if item.get('name')==name),None)
  if existing is not None:return next(i for i,item in enumerate(g['textures']) if item['source']==existing)
  view=source['bufferViews'][image['bufferView']];start=view.get('byteOffset',0);payload=binary[start:start+view['byteLength']]
  while len(blob)%4:blob.append(0)
  g['bufferViews'].append({'buffer':0,'byteOffset':len(blob),'byteLength':len(payload)});blob.extend(payload)
  g['images'].append({'name':name,'bufferView':len(g['bufferViews'])-1,'mimeType':image['mimeType']})
  sampler=len(g['samplers']);g['samplers'].append(copy.deepcopy(source['samplers'][original.get('sampler',0)]))
  g['textures'].append({'source':len(g['images'])-1,'sampler':sampler});return len(g['textures'])-1
 def remap(value):
  if isinstance(value,dict):
   for key,item in value.items():
    if key.endswith('Texture') and isinstance(item,dict) and 'index' in item:item['index']=texture(item['index'])
    else:remap(item)
  elif isinstance(value,list):
   for item in value:remap(item)
 remap(optical)
 target=next(i for i,m in enumerate(g['materials']) if m['name']=='PS1_FRONT_MASTERING_FOIL')
 g['materials'][target]=optical
