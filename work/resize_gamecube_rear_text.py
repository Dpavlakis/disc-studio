"""Reference-sized rear mastering text, without altering front print geometry."""
from pathlib import Path
import copy,json,struct,math,random
import numpy as np
from original_xbox_vectors import text_paths,bounds
from shapely.geometry import Polygon,GeometryCollection
from shapely.ops import triangulate

def resize(path):
 raw=path.read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);blob=bytearray(raw[28+n:])
 if g.get('extras',{}).get('rearMasteringTypographyVersion')==3:return
 def read(i):
  a=g['accessors'][i];v=g['bufferViews'][a['bufferView']];w={'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];return np.frombuffer(blob,dtype='<f4',count=a['count']*w,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,w).copy()
 def acc(data,kind):
  a=np.asarray(data,dtype='<f4');blob.extend(b'\0'*((-len(blob))%4));vi=len(g['bufferViews']);g['bufferViews'].append({'buffer':0,'byteOffset':len(blob),'byteLength':a.nbytes});blob.extend(a.tobytes());i=len(g['accessors']);g['accessors'].append({'bufferView':vi,'componentType':5126,'count':len(a),'type':kind,'min':a.min(axis=0).tolist(),'max':a.max(axis=0).tolist()});return i
 measured=json.loads((Path(__file__).parent/'gamecube_reference_measurements.json').read_text())
 # Sample the measured width/gap distribution, preserving a repeatable model.
 rng=random.Random(measured['randomSeed']);cursor,stop=measured['barcodeArcDeg'];bars=[]
 while cursor<stop:
  width=rng.choice(measured['barcodeWidthsDeg'])*rng.uniform(.94,1.06);end=min(stop,cursor+width)
  if end-cursor>.18:bars.append((cursor,end))
  cursor=end+rng.choice(measured['barcodeGapsDeg'])*rng.uniform(.94,1.06)
 radius=measured['barcodeRadiusMm']/1000;half=measured['barcodeHeightMm']/2000
 mesh=next(m for m in g['meshes'] if m['name']=='Irregular_security_bars')
 for primitive in mesh['primitives']:
  attrs={k:read(v) for k,v in primitive['attributes'].items()};front=(attrs['POSITION'].reshape(-1,3,3)[:,:,1]>0).all(axis=1);newattrs={key:[] for key in attrs}
  for a,b in bars:
   steps=max(1,math.ceil((b-a)/.3))
   for i in range(steps):
    t0=math.radians(a+(b-a)*i/steps);t1=math.radians(a+(b-a)*(i+1)/steps)
    corners=[(r*math.sin(t),-.000615,r*math.cos(t)) for r,t in [(radius-half,t0),(radius+half,t0),(radius+half,t1),(radius-half,t1)]]
    for triangle in [(0,1,2),(0,2,3)]:
     points=np.array([corners[k] for k in triangle])
     if np.cross(points[1]-points[0],points[2]-points[0])[1]>0:triangle=triangle[::-1]
     for k in triangle:
      x,y,z=corners[k];values={'POSITION':(x,y,z),'NORMAL':(0,-1,0),'TEXCOORD_0':(.5-x/.08,.5-z/.08),'TANGENT':(1,0,0,1),'COLOR_0':(1,1,1,1)}
      for key in attrs:newattrs[key].append(values[key])
  primitive['attributes']={key:acc(np.concatenate((arr.reshape(len(front),3,-1)[front].reshape(-1,arr.shape[1]),np.asarray(newattrs[key],dtype='<f4'))),'VEC'+str(arr.shape[1])) for key,arr in attrs.items()}
 unit=bounds(text_paths('C:/Windows/Fonts/OCRAEXT.TTF','DOL',1.0));size=measured['matrixGlyphHeightMm']/(unit[3]-unit[1])
 labels=[(value,measured['matrixWordAnglesDeg'][value],size) for value in ['DOL-GSSE-0-00 USA S0','IFPI LL08','C04K1402','M1S1']]
 pos=[];norm=[];uv=[];tan=[];sizes=[]
 for value,angle,size in labels:
  outlines=text_paths('C:/Windows/Fonts/OCRAEXT.TTF',value,size);x0,y0,x1,y1=bounds(outlines);shape=GeometryCollection();radius=21.05
  sizes.append({'text':value,'fontSizeMm':size,'glyphHeightMm':y1-y0,'radiusMm':radius,'angleDeg':angle,'representative':True})
  for outline in outlines:
   points=[]
   for x,y in outline:
    a=math.radians(angle)+(x-(x0+x1)/2)/radius;r=radius-(y-(y0+y1)/2);points.append((r*math.sin(a),r*math.cos(a)))
   if len(points)>2:shape=shape.symmetric_difference(Polygon(points).buffer(0))
  for tri in triangulate(shape):
   if not shape.covers(tri):continue
   for x,z in list(tri.exterior.coords)[:3]:
    pos.append((x/1000,-.00066,z/1000));norm.append((0,-1,0));uv.append((.5-x/80,.5-z/80));tan.append((1,0,0,1))
 material=copy.deepcopy(next(m for m in g['materials'] if m['name']=='GAMECUBE_SILVER_MASTERING_LETTERING'));material['name']='GAMECUBE_REAR_VECTOR_MASTERING_TEXT';material['alphaMode']='OPAQUE';material['pbrMetallicRoughness']={'baseColorFactor':[.55,.56,.53,1],'metallicFactor':.85,'roughnessFactor':.14};material['extensions']={'KHR_materials_clearcoat':{'clearcoatFactor':.2,'clearcoatRoughnessFactor':.06}};mi=len(g['materials']);g['materials'].append(material)
 primitive={'material':mi,'attributes':{k:acc(a,t) for k,a,t in [('POSITION',pos,'VEC3'),('NORMAL',norm,'VEC3'),('TEXCOORD_0',uv,'VEC2'),('TANGENT',tan,'VEC4')]}}
 next(m for m in g['meshes'] if m['name']=='GAMECUBE_SILVER_MASTERING_LETTERING')['primitives']=[primitive]
 g.setdefault('extras',{})['rearMasteringTypographyVersion']=3;g['extras']['rearMasteringTypography']=sizes;g['extras']['rearBarcodeMeasured']={'radiusMm':measured['barcodeRadiusMm'],'heightMm':measured['barcodeHeightMm'],'arcDeg':measured['barcodeArcDeg'],'count':len(bars),'widthGapSource':'photo polar sample','variation':measured['randomVariationFraction'],'seed':measured['randomSeed']}
 g['buffers'][0]['byteLength']=len(blob);j=json.dumps(g,separators=(',',':')).encode();j+=b' '*((-len(j))%4);blob.extend(b'\0'*((-len(blob))%4));path.write_bytes(struct.pack('<III',0x46546c67,2,28+len(j)+len(blob))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(blob),0x004e4942)+blob)
 print('Rear OCR mastering text resized to reference proportions and placed above the polished seam.')
if __name__=='__main__':resize(Path(__file__).resolve().parents[1]/'outputs/gamecube-disc.glb')
