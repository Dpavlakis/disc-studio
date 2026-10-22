"""Reference-proportioned Xbox 360 mastering sectors; centre assets stay frozen."""
from pathlib import Path
import json,struct,copy,math,random
import numpy as np
from original_xbox_vectors import text_paths,bounds
from shapely.geometry import Polygon,GeometryCollection
from shapely import constrained_delaunay_triangles
from refine_original_xbox_mastering import fingerprint
ROOT=Path(__file__).resolve().parents[1]
ALLOWED={'10_Xbox360_Back_Mastering_Band','12_Xbox360_Mastering_Barcode_Outer_Track','13_Xbox360_Mastering_Barcode_Inner_Track','14_Xbox360_Mastering_Barcode_Middle_Group','14b_Xbox360_Mastering_Inscriptions'}
def read(path):
 raw=path.read_bytes();n=struct.unpack_from('<I',raw,12)[0];return json.loads(raw[20:20+n]),bytearray(raw[28+n:])
def protected(g,b):
 doc=copy.deepcopy(g);doc['meshes']=[m for m in doc['meshes'] if m['name'] not in ALLOWED];return fingerprint(doc,b)
def update(path):
 g,blob=read(path);extra=g.setdefault('extras',{})
 if extra.get('xbox360MasteringReferenceVersion')==1:return
 before=protected(g,blob);baseline=ROOT/'work'/(path.stem+'-mastering-baseline.json')
 if not baseline.exists():baseline.write_text(json.dumps(before,indent=2))
 measure=json.loads((ROOT/'work/xbox360_security_measurements.json').read_text());og,_=read(ROOT/'outputs/xbox-original-disc.glb');mirror=copy.deepcopy(next(m for m in og['materials'] if m['name']=='ORIGINAL_XBOX_TEST_PLAIN_REFLECTIVE_SILVER'))
 def material(name,roughness):
  m=copy.deepcopy(mirror);m['name']=name;m['pbrMetallicRoughness']['roughnessFactor']=roughness;i=len(g['materials']);g['materials'].append(m);return i
 bandmat=material('XBOX360_REFERENCE_MIRROR_MASTERING_BAND',.045);barmat=material('XBOX360_REFERENCE_REFLECTIVE_SECURITY_TAGS',.16);textmat=material('XBOX360_REFERENCE_VECTOR_MASTERING_TEXT',.18)
 def acc(data,kind):
  a=np.asarray(data,dtype='<f4');blob.extend(b'\0'*((-len(blob))%4));vi=len(g['bufferViews']);g['bufferViews'].append({'buffer':0,'byteOffset':len(blob),'byteLength':a.nbytes});blob.extend(a.tobytes());i=len(g['accessors']);g['accessors'].append({'bufferView':vi,'componentType':5126,'type':kind,'count':len(a),'min':a.min(axis=0).tolist(),'max':a.max(axis=0).tolist()});return i
 def primitive(points,mat):
  p=np.asarray(points);norm=np.tile([0,-1,0],(len(p),1));uv=np.column_stack((.5-p[:,0]/.12,.5-p[:,2]/.12));tan=np.tile([1,0,0,1],(len(p),1));return {'material':mat,'attributes':{k:acc(a,t) for k,a,t in [('POSITION',p,'VEC3'),('NORMAL',norm,'VEC3'),('TEXCOORD_0',uv,'VEC2'),('TANGENT',tan,'VEC4')]}}
 def annulus(ri,ro,y,runs,mat):
  points=[]
  for start,end in runs:
   steps=max(1,math.ceil((end-start)/.25))
   for i in range(steps):
    a=math.radians(start+(end-start)*i/steps);b=math.radians(start+(end-start)*(i+1)/steps);corners=[(r*math.sin(t)/1000,y,r*math.cos(t)/1000) for r,t in [(ri,a),(ro,a),(ro,b),(ri,b)]]
    points.extend(corners[k] for k in [0,2,1,0,3,2])
  return primitive(points,mat)
 def replace(name,p):next(m for m in g['meshes'] if m['name']==name)['primitives']=[p]
 replace('10_Xbox360_Back_Mastering_Band',annulus(measure['bandInnerRadiusMm'],measure['bandOuterRadiusMm'],-.00066,[(0,360)],bandmat))
 tracks=[];specs=[]
 for i,key in enumerate(['outer','inner']):
  cursor,end=measure[key+'ArcDeg'];rng=random.Random(measure['seed']+i);runs=[]
  while cursor<end:
   width=max(.3,rng.choice(measure['barcodeWidthSamplesDeg'])*rng.uniform(.95,1.05));stop=min(end,cursor+width)
   if stop-cursor>=.28:runs.append((cursor,stop))
   cursor=stop+max(.45,rng.choice(measure['barcodeGapSamplesDeg'])*rng.uniform(.95,1.05))
  specs.append(('12_Xbox360_Mastering_Barcode_Outer_Track' if key=='outer' else '13_Xbox360_Mastering_Barcode_Inner_Track',measure[key+'TrackRadiusMm'],measure[key+'TrackHeightMm'],runs))
 # Reuse the former middle-fragment part for one proper outer-row tag.
 last=specs[0][3].pop();specs.append(('14_Xbox360_Mastering_Barcode_Middle_Group',specs[0][1],specs[0][2],[last]))
 for name,radius,height,runs in specs:
  replace(name,annulus(radius-height/2,radius+height/2,-.00072,runs,barmat));tracks.append({'name':name,'radiusMm':radius,'heightMm':height,'runsDeg':runs})
 # Representative mastering code and small suffix. The user's excluded 60/14
 # punched stamps are deliberately absent.
 labels=[('4000DS01-L1',64,.70,19.55),('01',84,.32,19.55),('IFPI L023',309,.46,18.55)]
 points=[];metadata=[];area=0;filled=0
 for value,angle,height,radius in labels:
  unit=bounds(text_paths('C:/Windows/Fonts/arial.ttf',value,1));outlines=text_paths('C:/Windows/Fonts/arial.ttf',value,height/(unit[3]-unit[1]));x0,y0,x1,y1=bounds(outlines);shape=GeometryCollection()
  metadata.append({'text':value,'angleDeg':angle,'radiusMm':radius,'glyphHeightMm':y1-y0,'arcDeg':math.degrees((x1-x0)/radius),'representative':True})
  for outline in outlines:
   mapped=[]
   for x,y in outline:
    a=math.radians(angle)+(x-(x0+x1)/2)/radius;r=radius-(y-(y0+y1)/2);mapped.append((r*math.sin(a),r*math.cos(a)))
   if len(mapped)>2:shape=shape.symmetric_difference(Polygon(mapped).buffer(0))
  triangles=constrained_delaunay_triangles(shape);area+=shape.area;filled+=sum(t.area for t in triangles.geoms)
  for t in triangles.geoms:
   p=np.array([(x/1000,-.00076,z/1000) for x,z in list(t.exterior.coords)[:3]])
   if np.cross(p[1]-p[0],p[2]-p[0])[1]>0:p=p[::-1]
   points.extend(p.tolist())
 assert abs(area-filled)<1e-8
 replace('14b_Xbox360_Mastering_Inscriptions',primitive(points,textmat))
 extra['xbox360MasteringReferenceVersion']=1;extra['xbox360MasteringTracks']=tracks;extra['xbox360MasteringTypography']=metadata;extra['xbox360MasteringLetterAreaMm2']=area;extra['xbox360MasteringTriangleAreaMm2']=filled;extra['xbox360ExcludedPunchedStamps']=['60','14'];extra['xbox360ReferenceSource']=measure['reference']
 assert protected(g,blob)==before,'Approved centre changed'
 g['buffers'][0]['byteLength']=len(blob);j=json.dumps(g,separators=(',',':')).encode();j+=b' '*((-len(j))%4);blob.extend(b'\0'*((-len(blob))%4));path.write_bytes(struct.pack('<III',0x46546c67,2,28+len(j)+len(blob))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(blob),0x004e4942)+blob)
 print(path.name+': rebuilt mastering sectors and clean text; holographic centre/assets preserved.')
if __name__=='__main__':
 for name in ['xbox360-silver-disc.glb','xbox360-test.glb']:update(ROOT/'outputs'/name)
