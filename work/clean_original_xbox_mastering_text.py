"""Clean native mastering lettering fitted to the clearer original Xbox reference."""
from pathlib import Path
import json,struct,math
import numpy as np
from original_xbox_vectors import text_paths,bounds
from shapely.geometry import Polygon,GeometryCollection
from shapely import constrained_delaunay_triangles
from refine_original_xbox_mastering import fingerprint
ROOT=Path(__file__).resolve().parents[1]
def update(path):
 raw=path.read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);blob=bytearray(raw[28+n:]);extra=g.setdefault('extras',{})
 if extra.get('originalXboxCleanMasteringTextVersion')==5:return
 before=fingerprint(g,blob);band=next(m for m in g['meshes'] if m['name']=='10_Original_Xbox_Back_Mastering_Band');material=band['primitives'][1]['material']
 font='C:/Windows/Fonts/arial.ttf';radius=19.25
 # Separate baseline codes, tiny suffixes and raised larger stamp. Do not flatten
 # the different physical glyph sizes into one uniform string.
 labels=[('DS01234-MS-L1',-42,.78,19.25),('DS01234-MS-L0',-12,.78,18.6)]
 for value,angle,height,r in labels.copy():
  unit=bounds(text_paths(font,value,1));arc=math.degrees((unit[2]-unit[0])*height/(unit[3]-unit[1])/r)
  labels.append(('01',angle+arc/2+2.8,.36,r))
 labels.extend([('01',1,.56,20.0),('1',35,.55,19.25)])
 pos=[];norm=[];uv=[];tan=[];metadata=[];area=0;triangle_area=0
 for value,angle,height,radius in labels:
  unit=bounds(text_paths(font,value,1));size=height/(unit[3]-unit[1]);outlines=text_paths(font,value,size);x0,y0,x1,y1=bounds(outlines);shape=GeometryCollection()
  metadata.append({'text':value,'radiusMm':radius,'glyphHeightMm':y1-y0,'arcDeg':math.degrees((x1-x0)/radius),'angleDeg':angle,'representative':True})
  for outline in outlines:
   points=[]
   for x,y in outline:
    a=math.radians(angle)+(x-(x0+x1)/2)/radius;r=radius-(y-(y0+y1)/2);points.append((r*math.sin(a),r*math.cos(a)))
   if len(points)>2:shape=shape.symmetric_difference(Polygon(points).buffer(0))
  triangles=constrained_delaunay_triangles(shape)
  area+=shape.area;triangle_area+=sum(t.area for t in triangles.geoms)
  assert abs(sum(t.area for t in triangles.geoms)-shape.area)<1e-8, 'Missing letter fill'
  for triangle in triangles.geoms:
   points=np.array(list(triangle.exterior.coords)[:3])
   if np.cross(np.array([points[1,0]-points[0,0],0,points[1,1]-points[0,1]]),np.array([points[2,0]-points[0,0],0,points[2,1]-points[0,1]]))[1]>0:points=points[::-1]
   for x,z in points:pos.append((x/1000,-.00076,z/1000));norm.append((0,-1,0));uv.append((.5-x/120,.5-z/120));tan.append((1,0,0,1))
 def acc(data,kind):
  a=np.asarray(data,dtype='<f4');blob.extend(b'\0'*((-len(blob))%4));vi=len(g['bufferViews']);g['bufferViews'].append({'buffer':0,'byteOffset':len(blob),'byteLength':a.nbytes});blob.extend(a.tobytes());i=len(g['accessors']);g['accessors'].append({'bufferView':vi,'componentType':5126,'count':len(a),'type':kind,'min':a.min(axis=0).tolist(),'max':a.max(axis=0).tolist()});return i
 band['primitives'][1]={'material':material,'attributes':{k:acc(a,t) for k,a,t in [('POSITION',pos,'VEC3'),('NORMAL',norm,'VEC3'),('TEXCOORD_0',uv,'VEC2'),('TANGENT',tan,'VEC4')]}}
 extra['originalXboxCleanMasteringTextVersion']=5;extra['originalXboxTextAreaMm2']=area;extra['originalXboxTextTriangleAreaMm2']=triangle_area;extra['originalXboxMasteringTypography']=metadata;extra['originalXboxMatrixSource']='Clean Arial vector outlines; representative identifiers; proportion reference codex-clipboard-3f880a95-274f-44b3-8634-34034308be4a.png'
 assert before==fingerprint(g,blob)
 g['buffers'][0]['byteLength']=len(blob);j=json.dumps(g,separators=(',',':')).encode();j+=b' '*((-len(j))%4);blob.extend(b'\0'*((-len(blob))%4));path.write_bytes(struct.pack('<III',0x46546c67,2,28+len(j)+len(blob))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(blob),0x004e4942)+blob)
 print('Replaced photo tracing with clean native lettering; temporary black band and approved centre preserved.')
if __name__=='__main__':update(ROOT/'outputs/xbox-original-disc.glb')
