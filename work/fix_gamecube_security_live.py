"""Replace only mastering bars/circles in the live model; retain current hub."""
import json,struct,math
from pathlib import Path
import numpy as np
from gamecube_security_pattern import security_bars
root=Path(__file__).resolve().parents[1]/'outputs';path=root/'gamecube-disc.glb'
raw=path.read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);binary=raw[28+n:];payload=bytearray(binary)
def read(index):
 a=g['accessors'][index];v=g['bufferViews'][a['bufferView']];w=int(a['type'][-1]);return np.frombuffer(binary,dtype='<f4',count=a['count']*w,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,w)
def acc(a):
 a=np.asarray(a,dtype='<f4')
 while len(payload)%4:payload.append(0)
 g['bufferViews'].append({'buffer':0,'byteOffset':len(payload),'byteLength':a.nbytes});payload.extend(a.tobytes());g['accessors'].append({'bufferView':len(g['bufferViews'])-1,'componentType':5126,'count':len(a),'type':'VEC'+str(a.shape[1]),'min':a.min(axis=0).tolist(),'max':a.max(axis=0).tolist()});return len(g['accessors'])-1
removedRings=removedBars=0
for mesh in g['meshes']:
 for prim in list(mesh['primitives']):
  name=g['materials'][prim['material']]['name'];attrs={k:read(v) for k,v in prim['attributes'].items()};p=attrs['POSITION'].reshape(-1,3,3);r=np.hypot(p[:,:,0],p[:,:,2]);drop=np.zeros(len(p),dtype=bool)
  if name=='GAMECUBE_POLISHED_HUB':
   drop=(r.min(axis=1)>.0173)&(r.max(axis=1)<.0182);removedRings+=int(drop.sum())
  if name=='GAMECUBE_SILVER_DATA_UNDERSIDE':
   drop=(r.min(axis=1)>.0209)&(r.max(axis=1)<.0221)&((np.abs(p[:,:,1]-.00072)<1e-7).all(axis=1)|(np.abs(p[:,:,1]+.000615)<1e-7).all(axis=1));removedBars+=int(drop.sum())
  if drop.all():mesh['primitives'].remove(prim)
  elif drop.any():prim['attributes']={k:acc(a.reshape(len(p),3,-1)[~drop].reshape(-1,a.shape[1])) for k,a in attrs.items()}
meshMap={i:j for j,i in enumerate(i for i,m in enumerate(g['meshes']) if m['primitives'])};g['meshes']=[m for m in g['meshes'] if m['primitives']]
oldNodes=g['nodes'];nodeMap={i:j for j,i in enumerate(i for i,n in enumerate(oldNodes) if n.get('mesh') in meshMap)};g['nodes']=[dict(n,mesh=meshMap[n['mesh']]) for n in oldNodes if n.get('mesh') in meshMap]
for scene in g['scenes']:scene['nodes']=[nodeMap[i] for i in scene['nodes'] if i in nodeMap]
def annulus_triangles(ri,ro,y,a,b,front):
 points=[];N=max(1,math.ceil((b-a)/.35))
 for i in range(N):
  t0=math.radians(a+(b-a)*i/N);t1=math.radians(a+(b-a)*(i+1)/N)
  quad=[(ri*math.cos(t0),y,ri*math.sin(t0)),(ro*math.cos(t0),y,ro*math.sin(t0)),(ro*math.cos(t1),y,ro*math.sin(t1)),(ri*math.cos(t1),y,ri*math.sin(t1))]
  order=[0,2,1,0,3,2] if front else [0,1,2,0,2,3]
  points.extend(quad[k] for k in order)
 return points
def addmesh(name,points,material):
 p=np.array(points,dtype='<f4');norm=np.zeros_like(p);norm[:,1]=np.where(p[:,1]>0,1,-1);uv=np.column_stack((.5-p[:,0]/.08,.5-p[:,2]/.08));t=np.tile([1,0,0,1],(len(p),1));attrs={k:acc(a) for k,a in [('POSITION',p),('NORMAL',norm),('TEXCOORD_0',uv),('TANGENT',t)]};g['meshes'].append({'name':name,'primitives':[{'material':material,'attributes':attrs}]});g['nodes'].append({'name':name,'mesh':len(g['meshes'])-1,'rotation':[-math.sqrt(.5),0,0,math.sqrt(.5)],'translation':[0,.06,0]});g['scenes'][0]['nodes'].append(len(g['nodes'])-1)
silver=next(i for i,m in enumerate(g['materials']) if m['name']=='GAMECUBE_SILVER_DATA_UNDERSIDE')
points=[]
for front,y in [(True,.00072),(False,-.000615)]:
 for a,b in security_bars():points.extend(annulus_triangles(.021,.02205,y,a,b,front))
addmesh('Irregular_security_bars',points,silver)
g['materials'].append({'name':'GAMECUBE_SINGLE_SECURITY_GROOVE','pbrMetallicRoughness':{'baseColorFactor':[.22,.23,.24,1],'metallicFactor':.35,'roughnessFactor':.23}})
points=annulus_triangles(.01775,.01778,.000712,0,360,True)+annulus_triangles(.01775,.01778,-.000612,0,360,False)
addmesh('One_fine_security_circle',points,len(g['materials'])-1)
g['extras']['securityRevision']=2;g['extras']['securityBarCount']=len(security_bars());g['extras']['securityCircleCountPerSide']=1
g['buffers'][0]['byteLength']=len(payload);j=json.dumps(g,separators=(',',':')).encode();j+=b' '*((-len(j))%4)
path.write_bytes(struct.pack('<III',0x46546c67,2,28+len(j)+len(payload))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(payload),0x004e4942)+payload)
assert removedRings and removedBars
print('Replaced',removedRings,'old ring triangles and',removedBars,'bar triangles; hub geometry retained.',len(security_bars()),'irregular bars per side.')
