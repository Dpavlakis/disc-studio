"""Remove unreachable GLB buffer data without changing live geometry or images."""
from pathlib import Path
import json,struct,hashlib,copy

def compact(path):
 raw=path.read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);binary=raw[28+n:];before=len(raw)
 assert not g.get('animations') and not g.get('skins'), 'Animated assets need a separate remapping pass'
 used=set()
 for mesh in g['meshes']:
  for p in mesh['primitives']:
   used.update(p['attributes'].values())
   if 'indices' in p:used.add(p['indices'])
   for target in p.get('targets',[]):used.update(target.values())
 amap={old:new for new,old in enumerate(sorted(used))};views={g['accessors'][i]['bufferView'] for i in used}
 assert all('sparse' not in g['accessors'][i] for i in used)
 views.update(i['bufferView'] for i in g.get('images',[]) if 'bufferView' in i)
 vmap={old:new for new,old in enumerate(sorted(views))};blob=bytearray();newviews=[];digests=[]
 for old in sorted(views):
  view=copy.deepcopy(g['bufferViews'][old]);assert view['buffer']==0
  offset=view.get('byteOffset',0);data=binary[offset:offset+view['byteLength']];digests.append(hashlib.sha256(data).digest());blob.extend(b'\0'*((-len(blob))%4));view['byteOffset']=len(blob);blob.extend(data);newviews.append(view)
 for mesh in g['meshes']:
  for p in mesh['primitives']:
   p['attributes']={k:amap[v] for k,v in p['attributes'].items()}
   if 'indices' in p:p['indices']=amap[p['indices']]
   for target in p.get('targets',[]):
    for key,value in target.items():target[key]=amap[value]
 accessors=[g['accessors'][i] for i in sorted(used)]
 for a in accessors:a['bufferView']=vmap[a['bufferView']]
 for i in g.get('images',[]):
  if 'bufferView' in i:i['bufferView']=vmap[i['bufferView']]
 g['accessors']=accessors;g['bufferViews']=newviews;g['buffers'][0]['byteLength']=len(blob)
 for v,digest in zip(newviews,digests):assert hashlib.sha256(blob[v['byteOffset']:v['byteOffset']+v['byteLength']]).digest()==digest
 j=json.dumps(g,separators=(',',':')).encode();j+=b' '*((-len(j))%4);blob.extend(b'\0'*((-len(blob))%4));result=struct.pack('<III',0x46546c67,2,28+len(j)+len(blob))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(blob),0x004e4942)+blob
 if raw!=result:path.write_bytes(result)
 print(path.name,round(before/1024**2,1),'->',round(len(result)/1024**2,1),'MiB; live buffers verified')
if __name__=='__main__':
 for path in (Path(__file__).resolve().parents[1]/'outputs').glob('*.glb'):compact(path)
