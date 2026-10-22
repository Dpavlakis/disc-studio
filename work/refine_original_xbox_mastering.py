"""Refine only the original Xbox rear mastering band; preserve the approved centre."""
from pathlib import Path
import json,struct,copy,random,math,hashlib,ast
import numpy as np
from PIL import Image
from original_xbox_vectors import OutlinePen
from shapely.geometry import Polygon,GeometryCollection
from shapely.ops import triangulate
from fontTools.svgLib.path import parse_path
ROOT=Path(__file__).resolve().parents[1]
ALLOWED={'10_Original_Xbox_Back_Mastering_Band','12_Original_Xbox_Mastering_Barcode_Outer_Track','13_Original_Xbox_Mastering_Barcode_Inner_Track','14_Original_Xbox_Mastering_Barcode_Middle_Group'}

def fingerprint(g,b):
 result={}
 for mesh in g['meshes']:
  if mesh['name'] in ALLOWED:continue
  h=hashlib.sha256()
  for p in mesh['primitives']:
   h.update(json.dumps(g['materials'][p['material']],sort_keys=True).encode())
   for key,index in sorted({**p['attributes'],**({'INDICES':p['indices']} if 'indices' in p else {})}.items()):
    a=g['accessors'][index];v=g['bufferViews'][a['bufferView']];offset=v.get('byteOffset',0);h.update(key.encode());h.update(b[offset:offset+v['byteLength']]);h.update(json.dumps({k:z for k,z in a.items() if k not in {'bufferView','byteOffset'}},sort_keys=True).encode())
  result[mesh['name']]=h.hexdigest()
 for i,img in enumerate(g.get('images',[])):
  if 'bufferView' in img:
   v=g['bufferViews'][img['bufferView']];o=v.get('byteOffset',0);result['IMAGE-'+str(i)]=hashlib.sha256(b[o:o+v['byteLength']]).hexdigest()
 return result

def refine(path):
 raw=path.read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);blob=bytearray(raw[28+n:]);measure=json.loads((ROOT/'work/xbox_original_security_measurements.json').read_text())
 if g.get('extras',{}).get('originalXboxMasteringRevision')==1:return
 before=fingerprint(g,blob);baseline=ROOT/'work/original_xbox_security_baseline.json'
 if not baseline.exists():baseline.write_text(json.dumps(before,indent=2))
 def acc(data,kind):
  a=np.asarray(data,dtype='<f4');blob.extend(b'\0'*((-len(blob))%4));vi=len(g['bufferViews']);g['bufferViews'].append({'buffer':0,'byteOffset':len(blob),'byteLength':a.nbytes});blob.extend(a.tobytes());i=len(g['accessors']);g['accessors'].append({'bufferView':vi,'componentType':5126,'type':kind,'count':len(a),'min':a.min(axis=0).tolist(),'max':a.max(axis=0).tolist()});return i
 def primitive(pos,norm,uv,tan,material):return {'material':material,'attributes':{k:acc(a,t) for k,a,t in [('POSITION',pos,'VEC3'),('NORMAL',norm,'VEC3'),('TEXCOORD_0',uv,'VEC2'),('TANGENT',tan,'VEC4')]}}
 def annulus(ri,ro,y,runs,material):
  pos=[];norm=[];uv=[];tan=[]
  for start,end in runs:
   steps=max(1,math.ceil((end-start)/.25))
   for i in range(steps):
    a=math.radians(start+(end-start)*i/steps);b=math.radians(start+(end-start)*(i+1)/steps);corners=[(r*math.sin(t),y,r*math.cos(t)) for r,t in [(ri,a),(ro,a),(ro,b),(ri,b)]]
    for tri in [(0,2,1),(0,3,2)]:
     for k in tri:
      x,yy,z=corners[k];pos.append((x,yy,z));norm.append((0,-1,0));uv.append((.5-x/.12,.5-z/.12));angle=math.atan2(x,z);tan.append((math.cos(angle),0,-math.sin(angle),1))
  return primitive(pos,norm,uv,tan,material)
 def pattern(seed,arc):
  rng=random.Random(seed);cursor,end=arc;result=[]
  while cursor<end:
   width=rng.choice(measure['barcodeWidthSamplesDeg'])*rng.uniform(.94,1.06);stop=min(end,cursor+width)
   if stop-cursor>.2:result.append((cursor,stop))
   cursor=stop+rng.choice(measure['barcodeGapSamplesDeg'])*rng.uniform(.94,1.06)
  return result
 band=next(m for m in g['meshes'] if m['name']=='10_Original_Xbox_Back_Mastering_Band');band['primitives']=[annulus(measure['bandInnerRadiusMm']/1000,measure['bandOuterRadiusMm']/1000,-.00066,[(0,360)],band['primitives'][0]['material'])]
 # Reflective marks, not light-coloured paint. Copy the approved mirror's
 # texture-free optical response; only these new bars use the new material.
 mirror=next(m for m in g['materials'] if m['name']=='ORIGINAL_XBOX_TEST_PLAIN_REFLECTIVE_SILVER');mat=copy.deepcopy(mirror);mat['name']='ORIGINAL_XBOX_REFERENCE_MASTERING_BARS';mat['pbrMetallicRoughness']['roughnessFactor']=.12;mi=len(g['materials']);g['materials'].append(mat)
 tracks=[]
 for i,(name,rad,height,arc) in enumerate([('12_Original_Xbox_Mastering_Barcode_Outer_Track',measure['outerTrackRadiusMm'],measure['outerTrackHeightMm'],measure['outerArcDeg']),('13_Original_Xbox_Mastering_Barcode_Inner_Track',measure['innerTrackRadiusMm'],measure['innerTrackHeightMm'],measure['innerArcDeg']),('14_Original_Xbox_Mastering_Barcode_Middle_Group',(measure['innerTrackRadiusMm']+measure['outerTrackRadiusMm'])/2,.28,measure['middleArcDeg'])]):
  runs=pattern(measure['seed']+i,arc);next(m for m in g['meshes'] if m['name']==name)['primitives']=[annulus((rad-height/2)/1000,(rad+height/2)/1000,-.00072,runs,mi)];tracks.append({'name':name,'radiusMm':rad,'heightMm':height,'arcDeg':arc,'barCount':len(runs)})
 # Retain the photographed matrix silhouette rather than inventing a serial.
 tree=ast.parse((ROOT/'work/make_gamecube_branding.py').read_text(encoding='utf-8'));fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='trace');ns={'np':np};exec(compile(ast.Module(body=[fn],type_ignores=[]),'trace','exec'),ns)
 image=np.asarray(Image.open(ROOT/'work/xbox-original-matrix-reference-unwrapped.png').convert('RGB'),float);mask=image.mean(axis=2)>168;mask[:117]=False;mask[205:]=False;mask[:,:110]=False;mask[:,850:]=False
 pen=OutlinePen();parse_path(ns['trace'](mask),pen);shape=GeometryCollection();scale=measure['pixelsPerMm']
 for contour in pen.paths:
  points=[]
  for x,y in contour:
   angle=math.radians(-45+(x-1)/1099*75);radius=(435-(y-1)/249*70)/scale;points.append((radius*math.sin(angle),radius*math.cos(angle)))
  if len(points)>2:shape=shape.symmetric_difference(Polygon(points).buffer(0))
 shape=shape.simplify(.012,preserve_topology=True);pos=[];norm=[];uv=[];tan=[]
 for triangle in triangulate(shape):
  if shape.covers(triangle):
   for x,z in list(triangle.exterior.coords)[:3]:pos.append((x/1000,-.00076,z/1000));norm.append((0,-1,0));uv.append((.5-x/120,.5-z/120));tan.append((1,0,0,1))
 textmat=copy.deepcopy(mirror);textmat['name']='ORIGINAL_XBOX_REFERENCE_MATRIX_LETTERING';textmat['pbrMetallicRoughness']['roughnessFactor']=.18;textmi=len(g['materials']);g['materials'].append(textmat);band['primitives'].append(primitive(pos,norm,uv,tan,textmi))
 g.setdefault('extras',{})['originalXboxMasteringRevision']=1;g['extras']['originalXboxMasteringTracks']=tracks;g['extras']['originalXboxMatrixSource']='Vector silhouette from supplied original Xbox photograph; no invented serial';g['extras']['originalXboxCentrePreserved']=True
 assert before==fingerprint(g,blob),'Protected centre or assets changed'
 g['buffers'][0]['byteLength']=len(blob);j=json.dumps(g,separators=(',',':')).encode();j+=b' '*((-len(j))%4);blob.extend(b'\0'*((-len(blob))%4));path.write_bytes(struct.pack('<III',0x46546c67,2,28+len(j)+len(blob))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(blob),0x004e4942)+blob)
 print('Original Xbox outer mastering band refined; centre geometry, hologram maps and materials verified unchanged.')
if __name__=='__main__':refine(ROOT/'outputs/xbox-original-disc.glb')
