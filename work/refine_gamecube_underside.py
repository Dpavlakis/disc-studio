"""Reference-based rear mastering band and moulded clear-hub lettering."""
from pathlib import Path
import json,struct,math,copy
import numpy as np
from original_xbox_vectors import text_paths,bounds
from shapely.geometry import Polygon,GeometryCollection
from shapely.ops import triangulate


def refine(path):
 raw=path.read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);blob=bytearray(raw[28+n:]);original=json.dumps(g,sort_keys=True)
 # This material is exclusive to the reverse mastering annulus.
 backing=next(m for m in g['materials'] if m['name']=='GAMECUBE_SILVER_SECURITY_BACKING')
 xboxraw=(Path(__file__).resolve().parents[1]/'outputs/xbox-original-disc.glb').read_bytes();xn=struct.unpack_from('<I',xboxraw,12)[0];xbox=json.loads(xboxraw[20:20+xn]);mirror=next(m for m in xbox['materials'] if m['name']=='ORIGINAL_XBOX_TEST_PLAIN_REFLECTIVE_SILVER')
 backing['pbrMetallicRoughness']=copy.deepcopy(mirror['pbrMetallicRoughness']);backing['extensions']=copy.deepcopy(mirror['extensions']);backing.pop('normalTexture',None)
 g.setdefault('extras',{})['rearBandFinish']='Original Xbox plain reflective silver: neutral .82, full metal, .045 roughness'

 reliefname='GAMECUBE_REAR_MOULDED_CLEAR_LETTERING'
 relief=next((m for m in g['materials'] if m['name']==reliefname),None)
 if relief is None:
  relief=copy.deepcopy(next(m for m in g['materials'] if m['name']=='GAMECUBE_CLEAR_POLYCARBONATE'));relief['name']=reliefname;g['materials'].append(relief)
 # Reapply after general clear-plastic finishing, keeping the mould faces
 # slightly frosted so their shallow relief catches an oblique light.
 relief['alphaMode']='OPAQUE';relief['pbrMetallicRoughness']={'baseColorFactor':[1,1,1,1],'metallicFactor':0,'roughnessFactor':.10}
 relief['extensions']={'KHR_materials_transmission':{'transmissionFactor':.93},'KHR_materials_ior':{'ior':1.58},'KHR_materials_volume':{'thicknessFactor':.00004,'attenuationColor':[1,1,1]},'KHR_materials_clearcoat':{'clearcoatFactor':.4,'clearcoatRoughnessFactor':.06}}
 if g.get('extras',{}).get('rearReferenceVersion')!=3:
  # Replace the previous rear additions rather than stacking another copy.
  for mesh in g['meshes']:
   mesh['primitives']=[p for p in mesh['primitives'] if g['materials'][p['material']]['name'] not in {reliefname,'GAMECUBE_REAR_POLISHED_SECURITY_BOUNDARY'}]
  def read(index):
   a=g['accessors'][index];v=g['bufferViews'][a['bufferView']];w={'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
   return np.frombuffer(blob,dtype='<f4',count=a['count']*w,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,w).copy()
  def acc(data,kind):
   a=np.asarray(data,dtype='<f4');blob.extend(b'\0'*((-len(blob))%4));vi=len(g['bufferViews']);g['bufferViews'].append({'buffer':0,'byteOffset':len(blob),'byteLength':a.nbytes});blob.extend(a.tobytes());ai=len(g['accessors']);g['accessors'].append({'bufferView':vi,'componentType':5126,'count':len(a),'type':kind,'min':a.min(axis=0).tolist(),'max':a.max(axis=0).tolist()});return ai
  def primitive(pos,norm,uv,tan,material):
   return {'attributes':{k:acc(a,t) for k,a,t in [('POSITION',pos,'VEC3'),('NORMAL',norm,'VEC3'),('TEXCOORD_0',uv,'VEC2'),('TANGENT',tan,'VEC4')]},'material':material}
  # Retain the approved front groove; relocate only the rear boundary to
  # the outside of the broad dark annulus, as in the supplied close-up.
  mesh=next(m for m in g['meshes'] if m['name']=='One_fine_security_circle')
  for p in mesh['primitives']:
   assert 'indices' not in p
   arrays={k:read(v) for k,v in p['attributes'].items()};keep=arrays['POSITION'].reshape(-1,3,3)[:,:,1].min(axis=1)>0
   p['attributes']={k:acc(a.reshape(len(keep),3,-1)[keep].reshape(-1,a.shape[1]),'VEC'+str(a.shape[1])) for k,a in arrays.items()}
  # Rounded chrome-like seam: two closely spaced highlight edges rather
  # than the former isolated circle deep inside the mastering surface.
  ringmat=copy.deepcopy(next(m for m in g['materials'] if m['name']=='GAMECUBE_POLISHED_HUB'));ringmat['name']='GAMECUBE_REAR_POLISHED_SECURITY_BOUNDARY';ringmat['pbrMetallicRoughness'].update(baseColorFactor=[.5,.53,.55,1],metallicFactor=1,roughnessFactor=.065);ringmat['extensions']={'KHR_materials_clearcoat':{'clearcoatFactor':.6,'clearcoatRoughnessFactor':.035}};ri=next((i for i,m in enumerate(g['materials']) if m['name']==ringmat['name']),len(g['materials']));g['materials'].append(ringmat) if ri==len(g['materials']) else g['materials'].__setitem__(ri,ringmat)
  pos=[];norm=[];uv=[];tan=[]
  for radius,halfwidth,height in [(19.96,.075,.045),(20.23,.035,.022)]:
   profile=[(radius-halfwidth,-.6),(radius-halfwidth*.45,-.6-height*.8),(radius,-.6-height),(radius+halfwidth*.45,-.6-height*.8),(radius+halfwidth,-.6)]
   for (ra,ya),(rb,yb) in zip(profile,profile[1:]):
    dr=rb-ra;dy=yb-ya;length=math.hypot(dr,dy)
    for i in range(1024):
     corners=[]
     for r,y,k in [(ra,ya,i),(rb,yb,i),(rb,yb,i+1),(ra,ya,i+1)]:
      a=k*math.tau/1024;c=math.cos(a);s=math.sin(a);corners.append(((r*c/1000,y/1000,r*s/1000),(dy/length*c,-dr/length,dy/length*s),(.5-r*c/80,.5-r*s/80),(-s,0,c,1)))
     for tri in [(0,1,2),(0,2,3)]:
      v=[np.array(corners[k][0]) for k in tri]
      if np.dot(np.cross(v[1]-v[0],v[2]-v[0]),corners[tri[0]][1])<0:tri=tri[::-1]
      for k in tri:
       p,no,u,t=corners[k];pos.append(p);norm.append(no);uv.append(u);tan.append(t)
  next(m for m in g['meshes'] if m['name']=='GAMECUBE_SILVER_SECURITY_BACKING')['primitives'].append(primitive(pos,norm,uv,tan,ri))
  # Text is small physical relief made from the same clear polymer, not ink.
  pos=[];norm=[];uv=[];tan=[]
  def vertex(x,y,z,no):
   pos.append((x/1000,y/1000,z/1000));norm.append(no);uv.append((.5-x/80,.5-z/80));tan.append((1,0,0,1))
  measured=json.loads((Path(__file__).parent/'gamecube_reference_measurements.json').read_text());radius=measured['hubTextRadiusMm'];unitpaths=text_paths('C:/Windows/Fonts/arial.ttf','MADE IN USA',1.0);ub=bounds(unitpaths);font_size=measured['hubGlyphHeightMm']/(ub[3]-ub[1])
  codes=[('MADE IN USA',0),('IFPI 4A12',90),('B006C8',180),('NINTENDO',270)]
  for value,angle in codes:
   paths=text_paths('C:/Windows/Fonts/arial.ttf',value,font_size);x0,y0,x1,y1=bounds(paths);shape=GeometryCollection()
   for outline in paths:
    points=[]
    for x,y in outline:
     a=math.radians(angle)+(x-(x0+x1)/2)/radius;r=radius-(y-(y0+y1)/2);points.append((r*math.sin(a),r*math.cos(a)))
    if len(points)>2:shape=shape.symmetric_difference(Polygon(points).buffer(0))
   for tri in triangulate(shape):
    if shape.covers(tri):
     for x,z in list(tri.exterior.coords)[:3]:vertex(x,-.640,z,(0,-1,0))
   polys=list(shape.geoms) if shape.geom_type=='MultiPolygon' else [shape]
   for poly in polys:
    if poly.geom_type!='Polygon':continue
    for ring in [poly.exterior,*poly.interiors]:
     for (x,z),(xx,zz) in zip(list(ring.coords),list(ring.coords)[1:]):
      length=math.hypot(xx-x,zz-z)
      if not length:continue
      no=((zz-z)/length,0,-(xx-x)/length)
      corners=[(x,-.600,z),(xx,-.600,zz),(xx,-.640,zz),(x,-.640,z)]
      for tri in [(0,1,2),(0,2,3)]:
       vertices=[np.array(corners[k]) for k in tri]
       if np.dot(np.cross(vertices[1]-vertices[0],vertices[2]-vertices[0]),no)<0:tri=tri[::-1]
       for k in tri:vertex(*corners[k],no)
  reliefindex=next(i for i,m in enumerate(g['materials']) if m['name']==reliefname)
  next(m for m in g['meshes'] if m['name']=='GAMECUBE_CLEAR_POLYCARBONATE')['primitives'].append(primitive(pos,norm,uv,tan,reliefindex))
  g.setdefault('extras',{})['rearReferenceVersion']=3;g['extras']['rearHubRelief']={'heightMm':.040,'radiusMm':radius,'fontSizeMm':font_size,'measuredGlyphHeightMm':measured['hubGlyphHeightMm'],'values':[c[0] for c in codes],'manufacturingCodesRepresentative':True};g['extras']['rearBoundaryRadiiMm']=[19.96,20.23]
 if original==json.dumps(g,sort_keys=True):return
 g['buffers'][0]['byteLength']=len(blob);j=json.dumps(g,separators=(',',':')).encode();j+=b' '*((-len(j))%4);blob.extend(b'\0'*((-len(blob))%4));path.write_bytes(struct.pack('<III',0x46546c67,2,28+len(j)+len(blob))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(blob),0x004e4942)+blob)
 print('Refined reverse mirror-silver mastering annulus, polished boundary and clear-polymer moulded letters.')
if __name__=='__main__':refine(Path(__file__).resolve().parents[1]/'outputs/gamecube-disc.glb')
