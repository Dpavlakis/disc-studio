"""Centre the spindle and close the opaque laminate beneath existing finishes."""
from pathlib import Path
import json,struct,math,copy
import numpy as np

def repair(path):
 raw=path.read_bytes();size=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+size]);blob=bytearray(raw[28+size:]);original=json.dumps(g,sort_keys=True)
 if not g.get('extras',{}).get('spindleCentered'):
  for scene in g['scenes']:
   for index in scene['nodes']:
    node=g['nodes'][index];t=node.setdefault('translation',[0,0,0]);t[1]=round(t[1]-.06,10)
  g.setdefault('extras',{})['spindleCentered']=True
 if not any(m['name']=='SOLID_DISC_LAMINATE_BODY' for m in g['meshes']):
  gc=path.name=='gamecube-disc.glb';inner=.0115 if gc else .022
  outer=.03915 if gc else .0584 if path.name.startswith('xbox') else .0594
  source=next(m for m in g['materials'] if m['name'] in {'GAMECUBE_SILVER_DATA_UNDERSIDE','BLACK_DATA_REFLECTIVE','BLUE_DATA_REFLECTIVE','GOLD_DATA_REFLECTIVE','SILVER_DATA_REFLECTIVE','ORIGINAL_XBOX_DATA_REFLECTIVE','XBOX360_DATA_REFLECTIVE'})
  mat=copy.deepcopy(source);mat['name']='SOLID_DISC_LAMINATE_BODY';mat['alphaMode']='OPAQUE';mat['doubleSided']=True
  mat['pbrMetallicRoughness'].pop('baseColorTexture',None);mat['pbrMetallicRoughness']['roughnessFactor']=.18;mat['pbrMetallicRoughness'].pop('normalTexture',None)
  mat.pop('normalTexture',None);mat.pop('occlusionTexture',None);mat.pop('emissiveTexture',None);mat.pop('extensions',None)
  mi=len(g['materials']);g['materials'].append(mat)
  pos=[];norm=[];uv=[];tangent=[]
  # A closed annular volume, slightly inset beneath the original face finishes.
  profiles=[((inner,-.0004),(outer,-.0004)),((outer,-.0004),(outer,.0004)),((outer,.0004),(inner,.0004)),((inner,.0004),(inner,-.0004))]
  for (ra,ya),(rb,yb) in profiles:
   dr=rb-ra;dy=yb-ya;length=math.hypot(dr,dy)
   for i in range(512):
    corners=[]
    for r,y,k in [(ra,ya,i),(rb,yb,i),(rb,yb,i+1),(ra,ya,i+1)]:
     a=k*math.tau/512;c=math.cos(a);s=math.sin(a);corners.append(((r*c,y,r*s),(dy/length*c,-dr/length,dy/length*s),(.5-r*c/(outer*2),.5-r*s/(outer*2)),(-s,0,c,1)))
    for tri in [(0,1,2),(0,2,3)]:
     a,b,c=[np.array(corners[j][0]) for j in tri]
     if np.dot(np.cross(b-a,c-a),corners[tri[0]][1])<0:tri=tri[::-1]
     for j in tri:
      p,n,u,t=corners[j];pos.append(p);norm.append(n);uv.append(u);tangent.append(t)
  def acc(data,kind):
   arr=np.asarray(data,dtype='<f4');blob.extend(b'\0'*((-len(blob))%4));vi=len(g['bufferViews']);g['bufferViews'].append({'buffer':0,'byteOffset':len(blob),'byteLength':arr.nbytes});blob.extend(arr.tobytes());ai=len(g['accessors']);g['accessors'].append({'bufferView':vi,'componentType':5126,'count':len(arr),'type':kind,'min':arr.min(axis=0).tolist(),'max':arr.max(axis=0).tolist()});return ai
  attrs={k:acc(v,t) for k,v,t in [('POSITION',pos,'VEC3'),('NORMAL',norm,'VEC3'),('TEXCOORD_0',uv,'VEC2'),('TANGENT',tangent,'VEC4')]}
  g['meshes'].append({'name':'SOLID_DISC_LAMINATE_BODY','primitives':[{'attributes':attrs,'material':mi}]});g['nodes'].append({'name':'SOLID_DISC_LAMINATE_BODY','mesh':len(g['meshes'])-1,'rotation':[-math.sqrt(.5),0,0,math.sqrt(.5)],'translation':[0,0,0]});g['scenes'][0]['nodes'].append(len(g['nodes'])-1)
 # Keep the closure inside the shallowest existing foil faces. The GameCube
 # front foil is at +0.56 mm, so the previous +0.595 mm cap covered it.
 # The internal closure needs no face textures, normal maps or anisotropy.
 core=next(m for m in g['meshes'] if m['name']=='SOLID_DISC_LAMINATE_BODY')
 if core.get('extras',{}).get('internalCoreVersion')!=2:
  for primitive in core['primitives']:
   accessor=g['accessors'][primitive['attributes']['POSITION']];view=g['bufferViews'][accessor['bufferView']]
   assert accessor['componentType']==5126 and 'byteStride' not in view
   values=np.frombuffer(blob,dtype='<f4',count=accessor['count']*3,offset=view.get('byteOffset',0)+accessor.get('byteOffset',0)).reshape((-1,3))
   values[:,1]=np.where(values[:,1]<0,-.0004,.0004)
   accessor['min']=values.min(axis=0).tolist();accessor['max']=values.max(axis=0).tolist()
   material=g['materials'][primitive['material']]
   material['pbrMetallicRoughness']={
    'baseColorFactor':material['pbrMetallicRoughness'].get('baseColorFactor',[.68,.68,.68,1]),
    'metallicFactor':.65,'roughnessFactor':.18}
   for key in ['normalTexture','occlusionTexture','emissiveTexture','extensions']:material.pop(key,None)
   material['alphaMode']='OPAQUE';material['doubleSided']=True
  core.setdefault('extras',{})['internalCoreVersion']=2
 if original==json.dumps(g,sort_keys=True):return
 g['buffers'][0]['byteLength']=len(blob);j=json.dumps(g,separators=(',',':')).encode();j+=b' '*((-len(j))%4);blob.extend(b'\0'*((-len(blob))%4));path.write_bytes(struct.pack('<III',0x46546c67,2,28+len(j)+len(blob))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(blob),0x004e4942)+blob)
 print(path.name,'spindle centred; solid laminate closed')

if __name__=='__main__':
 for path in (Path(__file__).resolve().parents[1]/'outputs').glob('*.glb'):repair(path)
