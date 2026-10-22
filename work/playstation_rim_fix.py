"""Separate opaque rim bands so they meet without nearly coplanar overlap."""
from pathlib import Path
import json,struct,math
import numpy as np

def repair_playstation_rim(path):
 path=Path(path);raw=path.read_bytes();jn=struct.unpack_from('<I',raw,12)[0]
 g=json.loads(raw[20:20+jn]);bn=struct.unpack_from('<I',raw,20+jn)[0]
 data_mesh=next(m for m in g['meshes'] if m['name']=='02_Blue_Data_Underside')
 if data_mesh.get('extras',{}).get('rimSeparationVersion')==1:return
 blob=bytearray(raw[28+jn:28+jn+bn])
 def accessor(values,kind,integer=False):
  a=np.asarray(values,dtype='<u4' if integer else '<f4')
  while len(blob)%4:blob.append(0)
  g['bufferViews'].append({'buffer':0,'byteOffset':len(blob),'byteLength':a.nbytes});blob.extend(a.tobytes())
  obj={'bufferView':len(g['bufferViews'])-1,'componentType':5125 if integer else 5126,'count':len(a),'type':kind}
  if not integer:obj.update(min=a.min(axis=0).tolist(),max=a.max(axis=0).tolist())
  g['accessors'].append(obj);return len(g['accessors'])-1
 def replace_surface(mesh,profiles,uv_data=False):
  p=[];norm=[];uv=[];tangent=[];indices=[]
  # Match the dark perimeter ring's exact angular sampling.
  resolution=2048
  for (ra,ya),(rb,yb) in profiles:
   dr=rb-ra;dy=yb-ya;length=math.hypot(dr,dy);base=len(p)
   for i in range(resolution+1):
    a=i*math.tau/resolution;c=math.cos(a);s=math.sin(a)
    for r,y in ((ra,ya),(rb,yb)):
     p.append((r*c,y,r*s));norm.append((dy/length*c,-dr/length,dy/length*s))
     uv.append((.5+r*c/.12,.5-r*s/.12) if uv_data else (0,0));tangent.append((-s,0,c,1))
   for i in range(resolution):
    k=base+2*i
    for a,b,c in ((k,k+1,k+3),(k,k+3,k+2)):
     cross=np.cross(np.asarray(p[b])-p[a],np.asarray(p[c])-p[a])
     indices.extend((a,b,c) if np.dot(cross,norm[a])>0 else (a,c,b))
  primitive=mesh['primitives'][0]
  primitive['attributes']={'POSITION':accessor(p,'VEC3'),'NORMAL':accessor(norm,'VEC3'),'TEXCOORD_0':accessor(uv,'VEC2'),'TANGENT':accessor(tangent,'VEC4')}
  primitive['indices']=accessor(indices,'SCALAR',True)
  mesh.setdefault('extras',{})['rimSeparationVersion']=1
 # The 59.0–59.3 mm band is already a closed opaque ring. No foil plane
 # should run underneath it only five micrometers from its visible face.
 replace_surface(data_mesh,[((.022,-.0006),(.0590,-.0006)),((.0593,-.0006),(.0594,-.0006))],True)
 cap=next((m for m in g['meshes'] if m['name']=='Closed_Outer_Laminate_Edge'),None)
 if cap:
  replace_surface(cap,[((.0594,-.0006),(.0594,.0006)),((.0590,.000599),(.0587,.000599)),((.0594,.000599),(.0593,.000599))])
 g['buffers'][0]['byteLength']=len(blob);js=json.dumps(g,separators=(',',':')).encode();js+=b' '*((-len(js))%4);blob+=b'\0'*((-len(blob))%4)
 path.write_bytes(struct.pack('<III',0x46546c67,2,28+len(js)+len(blob))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(blob),0x004e4942)+blob)
 print('Separated front/back rim surfaces:',path.name)

if __name__=='__main__':
 root=Path(__file__).resolve().parents[1]/'outputs'
 for name in ('ps1-black-disc.glb','ps2-blue-disc.glb','ps2-silver-disc.glb','ps2-gold-disc.glb'):repair_playstation_rim(root/name)
