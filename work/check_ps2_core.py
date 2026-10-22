"""Check the solid PS2 backing against rays into the formerly open core."""
import hashlib,json,struct
from pathlib import Path
import numpy as np
from solid_ps2_core import close_ps2_core

root=Path(__file__).resolve().parents[1]/'outputs'
for path in root.glob('ps2-*.glb'):
 raw=path.read_bytes();size=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+size]);binary=raw[28+size:]
 assert len(g['meshes'])==17
 mesh=next(m for m in g['meshes'] if m['name']=='Closed_Outer_Laminate_Edge');primitive=mesh['primitives'][0]
 material=g['materials'][primitive['material']]
 assert material.get('alphaMode','OPAQUE')=='OPAQUE'
 assert 'KHR_materials_transmission' not in material.get('extensions',{})
 # The shared clear hub retains its transmission material.
 assert g['materials'][2]['extensions']['KHR_materials_transmission']['transmissionFactor']>.9
 def read(index):
  a=g['accessors'][index];v=g['bufferViews'][a['bufferView']];width={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
  return np.frombuffer(binary,dtype={5126:'<f4',5125:'<u4'}[a['componentType']],count=a['count']*width,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,width)
 p=read(primitive['attributes']['POSITION']);normal=read(primitive['attributes']['NORMAL']);tri=np.concatenate([read(pr['indices']).reshape(-1,3) for pr in mesh['primitives']])
 for pr in mesh['primitives']:
  mat=g['materials'][pr['material']]
  assert mat.get('alphaMode','OPAQUE')=='OPAQUE'
  if mat['name']=='PS2_FRONT_DATA_BACKING':
   for key in ('normalTexture','extensions'):
    assert mat[key]==g['materials'][1][key]
   assert mat['pbrMetallicRoughness']==g['materials'][1]['pbrMetallicRoughness']
  if mat['name']=='PS2_FRONT_MATRIX_BACKING':
   assert mat['pbrMetallicRoughness']==g['materials'][9]['pbrMetallicRoughness']
 for detail in g['meshes']:
  name=detail['name']
  if not (name.startswith('05_Moulded_Ring_') or name.startswith(('06_','09_','10_','11_','12_','13_'))):continue
  originals=[pr for pr in detail['primitives'] if not pr.get('extras',{}).get('ps2MirroredRear')]
  reflected=[pr for pr in detail['primitives'] if pr.get('extras',{}).get('ps2MirroredRear')]
  assert len(originals)==len(reflected)>0,name
  for source,mirror in zip(originals,reflected):
   before=read(source['attributes']['POSITION']);after=read(mirror['attributes']['POSITION'])
   assert np.allclose(after[:,[0,2]],before[:,[0,2]])
   assert np.allclose(after[:,1],-before[:,1]-(0 if name.startswith('05_') else .00025))
   assert np.array_equal(read(source['attributes']['TEXCOORD_0']),read(mirror['attributes']['TEXCOORD_0']))
   assert source['material']==mirror['material']
   if not name.startswith('05_'):assert after[:,1].max()<.00061
 triangles=p[tri];a,b,c=triangles[:,0],triangles[:,1],triangles[:,2];e1,e2=b-a,c-a
 cross=np.cross(e1,e2);assert np.all(np.sum(cross*normal[tri[:,0]],axis=1)>0)
 def first_hit(origin,direction):
  origin=np.array(origin);direction=np.array(direction);direction=direction/np.linalg.norm(direction)
  h=np.cross(direction,e2);det=np.sum(e1*h,axis=1);mask=np.abs(det)>1e-14
  inv=np.divide(1.,det,out=np.zeros_like(det),where=mask);s=origin-a;u=inv*np.sum(s*h,axis=1);q=np.cross(s,e1);v=inv*np.sum(direction*q,axis=1);t=inv*np.sum(e2*q,axis=1)
  hits=mask&(u>=-1e-7)&(v>=-1e-7)&(u+v<=1.0000001)&(t>1e-8)
  assert hits.any(),(path.name,origin,direction)
  return t[hits].min()
 # Front-facing and shallow rays now hit a solid surface without artwork.
 for radius in (.012,.025,.04,.058):
  for direction in ((0,1,0),(1,.02,0),(-1,.02,0),(0,.02,1)):
   assert first_hit((radius,0,0),direction)<.13
 # The central hole remains open through the entire model core.
 radius=np.linalg.norm(p[:,[0,2]],axis=1);assert radius.min()>=.011399
 digest=hashlib.sha256(raw).digest();close_ps2_core(path);assert hashlib.sha256(path.read_bytes()).digest()==digest
 print(path.name+': opaque label backing, inner/outer walls, outward normals and shallow-angle ray checks passed; clear hub preserved.')
