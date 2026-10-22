"""Separate front backing from ink without moving the artwork or rear details."""
from pathlib import Path
import json,struct
import numpy as np
from build_modern_playstation import load,ROOT
TARGETS=['ps2-blue-disc','ps2-silver-disc','ps2-gold-disc','ps3-silver-disc','ps4-silver-disc','xbox-original-disc','xbox360-silver-disc','xbox360-test']
def update(path):
 g,blob=load(path)
 if g.get('extras',{}).get('artworkDepthSeparationVersion')==1:return
 mesh=next(m for m in g['meshes'] if ('Exposed_Silver_Between_Artwork' in m['name']) or m['name']=='Closed_Outer_Laminate_Edge') if path.stem.startswith('xbox') else next(m for m in g['meshes'] if m['name']=='Closed_Outer_Laminate_Edge')
 remap={};changed=0
 for p in mesh['primitives']:
  ai=p['attributes']['POSITION']
  if ai in remap:p['attributes']['POSITION']=remap[ai];continue
  a=g['accessors'][ai];v=g['bufferViews'][a['bufferView']];arr=np.frombuffer(blob,dtype='<f4',count=a['count']*3,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,3).copy();mask=np.isclose(arr[:,1],.0006,atol=1e-9)
  if not mask.any():remap[ai]=ai;continue
  arr[mask,1]=.00048;changed+=int(mask.sum());blob.extend(b'\0'*((-len(blob))%4));vi=len(g['bufferViews']);g['bufferViews'].append({'buffer':0,'byteOffset':len(blob),'byteLength':arr.nbytes});blob.extend(arr.tobytes());new=dict(a);new.update(bufferView=vi,min=arr.min(axis=0).tolist(),max=arr.max(axis=0).tolist());new.pop('byteOffset',None);ni=len(g['accessors']);g['accessors'].append(new);remap[ai]=ni;p['attributes']['POSITION']=ni
 g.setdefault('extras',{})['artworkDepthSeparationVersion']=1;g['extras']['artworkBackingYMetres']=.00048
 g['buffers'][0]['byteLength']=len(blob);j=json.dumps(g,separators=(',',':')).encode();j+=b' '*((-len(j))%4);blob.extend(b'\0'*((-len(blob))%4));path.write_bytes(struct.pack('<III',0x46546c67,2,28+len(j)+len(blob))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(blob),0x004e4942)+blob)
 print(path.name+': backing inset; ink plane and approved rear geometry unchanged; '+str(changed)+' vertices separated.')
if __name__=='__main__':
 for name in TARGETS:update(ROOT/'outputs'/(name+'.glb'))
