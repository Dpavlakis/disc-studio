"""Close the solid disc laminate inside the clear outer bevel."""
from pathlib import Path
import json,struct,math,copy
import numpy as np

def cap_outer_edge(path):
 path=Path(path);raw=path.read_bytes();jn=struct.unpack_from('<I',raw,12)[0]
 g=json.loads(raw[20:20+jn]);bn=struct.unpack_from('<I',raw,20+jn)[0]
 if any(m.get('name')=='Closed_Outer_Laminate_Edge' for m in g['meshes']):return
 blob=bytearray(raw[28+jn:28+jn+bn])
 def accessor(values,kind,integer=False):
  a=np.asarray(values,dtype='<u4' if integer else '<f4')
  while len(blob)%4:blob.append(0)
  g['bufferViews'].append({'buffer':0,'byteOffset':len(blob),'byteLength':a.nbytes});blob.extend(a.tobytes())
  obj={'bufferView':len(g['bufferViews'])-1,'componentType':5125 if integer else 5126,'count':len(a),'type':kind}
  if not integer:obj.update(min=a.min(axis=0).tolist(),max=a.max(axis=0).tolist())
  g['accessors'].append(obj);return len(g['accessors'])-1
 xbox=path.name.startswith('xbox360-')
 color=[.68,.68,.68,1] if xbox else g['materials'][1]['pbrMetallicRoughness']['baseColorFactor']
 core_mat=len(g['materials']);g['materials'].append({'name':'SOLID_LAMINATE_EDGE','pbrMetallicRoughness':{'baseColorFactor':color,'metallicFactor':.65,'roughnessFactor':.18}})
 # Separate material for the outer plastic: changing it cannot affect the hub.
 edge=copy.deepcopy(g['materials'][2]);edge['name']='CLEAR_CLOSED_OUTER_RIM';edge['doubleSided']=True
 edge['pbrMetallicRoughness'].update(baseColorFactor=[.96,.97,1,.42],roughnessFactor=.08)
 edge.setdefault('extensions',{})['KHR_materials_transmission']={'transmissionFactor':.8}
 edge_mat=len(g['materials']);g['materials'].append(edge)
 for mesh in g['meshes']:
  if 'Outer_Bevel' in mesh['name']:
   for p in mesh['primitives']:p['material']=edge_mat
 pos=[];norm=[];uv=[];tan=[];indices=[]
 profiles=[((.0594,-.0006),(.0594,.0006))]
 if not xbox:profiles.append(((.0594,.000599),(.0587,.000599)))
 for (ra,ya),(rb,yb) in profiles:
  dr=rb-ra;dy=yb-ya;length=math.hypot(dr,dy);base=len(pos)
  for i in range(513):
   angle=i*math.tau/512;c=math.cos(angle);s=math.sin(angle)
   for r,y in ((ra,ya),(rb,yb)):
    pos.append((r*c,y,r*s));norm.append((dy/length*c,-dr/length,dy/length*s));uv.append((0,0));tan.append((-s,0,c,1))
  for i in range(512):
   k=base+2*i
   for a,b,c in ((k,k+1,k+3),(k,k+3,k+2)):
    face=np.cross(np.asarray(pos[b])-pos[a],np.asarray(pos[c])-pos[a])
    indices.extend((a,b,c) if np.dot(face,norm[a])>0 else (a,c,b))
 attrs={'POSITION':accessor(pos,'VEC3'),'NORMAL':accessor(norm,'VEC3'),'TEXCOORD_0':accessor(uv,'VEC2'),'TANGENT':accessor(tan,'VEC4')}
 g['meshes'].append({'name':'Closed_Outer_Laminate_Edge','primitives':[{'attributes':attrs,'indices':accessor(indices,'SCALAR',True),'material':core_mat}]})
 g['nodes'].append({'name':'Closed_Outer_Laminate_Edge','mesh':len(g['meshes'])-1,'rotation':[-math.sqrt(.5),0,0,math.sqrt(.5)],'translation':[0,.06,0]});g['scenes'][0]['nodes'].append(len(g['nodes'])-1)
 g['buffers'][0]['byteLength']=len(blob);js=json.dumps(g,separators=(',',':')).encode();js+=b' '*((-len(js))%4);blob+=b'\0'*((-len(blob))%4)
 result=struct.pack('<III',0x46546c67,2,28+len(js)+len(blob))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(blob),0x004e4942)+blob
 path.write_bytes(result)
 print('Closed outer laminate and clear rim:',path.name)

if __name__=='__main__':
 root=Path(__file__).resolve().parents[1]/'outputs'
 for name in ('ps2-blue-disc.glb','ps2-silver-disc.glb','ps2-gold-disc.glb','xbox360-test.glb'):cap_outer_edge(root/name)
