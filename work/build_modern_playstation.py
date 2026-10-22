"""PS3/PS4 silver discs derived from the approved PS2 silver body."""
from pathlib import Path
import json,struct,copy,math,random,xml.etree.ElementTree as ET,hashlib,io
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from original_xbox_vectors import OutlinePen,text_paths,bounds
from fontTools.svgLib.path import parse_path
from shapely.geometry import Polygon,GeometryCollection
from shapely import constrained_delaunay_triangles
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs'
def load(path):
 raw=path.read_bytes();n=struct.unpack_from('<I',raw,12)[0];return json.loads(raw[20:20+n]),bytearray(raw[28+n:])
def svg_paths(path):
 paths=[]
 for el in ET.parse(path).getroot().iter():
  if el.tag.endswith('path'):
   assert not el.get('transform');pen=OutlinePen();parse_path(el.attrib['d'],pen);paths.extend(pen.paths)
 return paths
def build(console):
 target=OUT/(console+'-silver-disc.glb')
 if target.exists():
  existing,_=load(target)
  if existing.get('extras',{}).get('modernPlayStationVersion')==(13 if console=='ps3' else 9):return
 source=OUT/'ps2-silver-disc.glb';g,blob=load(source);sourcehash=hashlib.sha256(source.read_bytes()).hexdigest();word=OUT/'branding-source'/(console+'-supplied.svg')
 # Rebuild from the unmodified source material, then reapply the ink pass.
 previous_ink=g.get('extras',{}).pop('printedInkFinish',None)
 if previous_ink:
  for index,material in previous_ink['originalMaterials'].items():g['materials'][int(index)]=material
 if not word.exists():word.write_bytes(Path('C:/Users/dimit/Downloads/playstation'+console[-1]+'-svgrepo-com.svg').read_bytes())
 def acc(data,kind):
  a=np.asarray(data,dtype='<f4');blob.extend(b'\0'*((-len(blob))%4));vi=len(g['bufferViews']);g['bufferViews'].append({'buffer':0,'byteOffset':len(blob),'byteLength':a.nbytes});blob.extend(a.tobytes());i=len(g['accessors']);g['accessors'].append({'bufferView':vi,'componentType':5126,'type':kind,'count':len(a),'min':a.min(axis=0).tolist(),'max':a.max(axis=0).tolist()});return i
 def primitive(points,material):
  p=np.asarray(points,dtype='<f4').reshape(-1,3,3);cross=np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]);p=p[cross[:,1]<0].reshape(-1,3);return {'material':material,'attributes':{k:acc(a,t) for k,a,t in [('POSITION',p,'VEC3'),('NORMAL',np.tile([0,-1,0],(len(p),1)),'VEC3'),('TEXCOORD_0',np.column_stack((.5-p[:,0]/.12,.5-p[:,2]/.12)),'VEC2'),('TANGENT',np.tile([1,0,0,1],(len(p),1)),'VEC4')]}}
 def annulus(ri,ro,y,runs,material):
  points=[]
  for start,end in runs:
   steps=max(1,math.ceil((end-start)/.25))
   for i in range(steps):
    a=math.radians(start+(end-start)*i/steps);b=math.radians(start+(end-start)*(i+1)/steps);corners=[(r*math.sin(t)/1000,y,r*math.cos(t)/1000) for r,t in [(ri,a),(ro,a),(ro,b),(ri,b)]];points.extend(corners[k] for k in [0,2,1,0,3,2])
  return primitive(points,material)
 def mat(name,color,metal,rough,iri=0):
  m={'name':name,'pbrMetallicRoughness':{'baseColorFactor':color+[1],'metallicFactor':metal,'roughnessFactor':rough}}
  if iri:m['extensions']={'KHR_materials_iridescence':{'iridescenceFactor':iri,'iridescenceIor':1.45,'iridescenceThicknessMinimum':320,'iridescenceThicknessMaximum':360}}
  i=len(g['materials']);g['materials'].append(m);return i
 silver=mat(console.upper()+'_SILVER_SECURITY_FIELD',[.72,.72,.70],1,.09)
 track=mat(console.upper()+'_POLISHED_MASTERING_TRACK',[.57,.58,.55],1,.065,.10)
 etched=mat(console.upper()+'_ETCHED_VECTOR_LOGOS',[.50,.51,.49],1,.22,.22)
 barsmat=mat(console.upper()+'_REFLECTIVE_SECURITY_TAGS',[.78,.79,.76],1,.17,.32)
 dark=mat(console.upper()+'_INNER_POLISHED_BOUNDARY',[.06,.065,.06],1,.08)
 inner=10.45 if console=='ps3' else 11.4;outer=18.6 if console=='ps3' else 18.8;logo_radius=13.8 if console=='ps3' else 14.15
 def replace(index,name,prims):g['meshes'][index]={'name':name,'primitives':prims}
 replace(7,console.upper()+'_Silver_Inner_Security_Field',[annulus(inner,outer,-.00066,[(0,360)],silver)])
 replace(10,console.upper()+'_Fine_Mastering_Outer_Boundary',[annulus(outer-.08,outer,-.00075,[(0,360)],silver)])
 replace(11,console.upper()+'_Inner_Polished_Boundary',[annulus(inner+.05,inner+.27,-.00074,[(0,360)],dark)])
 replace(12,console.upper()+'_Clear_Hub_Silver_Seam',[annulus(inner+.28,inner+.47,-.00074,[(0,360)],silver)])
 replace(13,console.upper()+'_Mastering_Track',[annulus(outer-1.25,outer-.15,-.00071,[(0,360)],track)])
 rng=random.Random(303 if console=='ps3' else 404);runs=[]
 if console in ['ps3','ps4']:
  # User's quarter-ring reference: one 90-degree sector with broad end
  # blocks. No additional marks on the top or lower circumference.
  for start,stop in [(47,129)]:
   cursor=start
   while cursor<stop:
    width=rng.choice([.26,.38,.52,.70])*rng.uniform(.95,1.05);end=min(stop,cursor+width)
    if end-cursor>.2:runs.append((cursor,end))
    cursor=end+rng.choice([.55,.70,.90,1.15])
  runs.extend([(43,46),(130,133)])
  tag_inner,tag_outer=outer-1.02,outer-.40
 else:
  for start,stop in [(43,217),(-23,23)]:
   cursor=start
   while cursor<stop:
    width=rng.choice([.26,.38,.52,.78,1.05])*rng.uniform(.95,1.05);end=min(stop,cursor+width)
    if end-cursor>.2:runs.append((cursor,end))
    cursor=end+rng.choice([.32,.45,.65,.85])
  tag_inner,tag_outer=outer-1.14,outer-.27
 if console=='ps4':
  # Separate PS4 code: four clusters with wider separator gaps and a
  # different wide/narrow sequence inside the same 90-degree envelope.
  runs=[(43,46),(130,133)];rng=random.Random(413254)
  for start,stop in [(47,66),(69,89),(92,110),(113,129)]:
   cursor=start
   while cursor<stop:
    width=rng.choice([.30,.45,.70,.95])*rng.uniform(.96,1.04);end=min(stop,cursor+width)
    if end-cursor>.2:runs.append((cursor,end))
    cursor=end+rng.choice([.50,.65,.85,1.05])
 runs.sort()
 replace(14,console.upper()+'_Separated_Mastering_Tags',[annulus(tag_inner,tag_outer,-.00076,runs,barsmat)])
 replace(15,console.upper()+'_Inner_Silver_Substrate',[annulus(inner,outer,-.00064,[(0,360)],silver)])
 if console in ['ps3','ps4']:
  # Join the plain read face directly to the resized security edge. The PS2
  # face began at 22 mm, leaving an exposed annular gap after shrinking.
  replace(1,console.upper()+'_Silver_Data_Underside',[annulus(outer,58.4,-.0006,[(0,360)],1)])
  # Xbox 360 construction: diffraction stops at 58.4 mm, followed by a
  # 1 mm plain silver finishing band and the clear 59.4–60 mm bevel.
  for rim_primitive in g['meshes'][9]['primitives']:rim_primitive['material']=silver
  g['meshes'][9]['primitives'].append(annulus(58.4,59.4,-.00072,[(0,360)],silver))
  g['meshes'][9]['name']=console.upper()+'_Plain_Outer_Rim_Transition'
 # Flat logos mapped around the radius with native width/height preserved.
 mono=svg_paths(OUT/'branding-source/PlayStation_logo.svg');wordpaths=svg_paths(word);points=[];placements=[];sourcearea=0;trianglearea=0
 def add(paths,angle,radius,width,label):
  nonlocal sourcearea,trianglearea
  x0,y0,x1,y1=bounds(paths);scale=width/(x1-x0);shape=GeometryCollection()
  for outline in paths:
   mapped=[]
   for x,y in outline:
    a=math.radians(angle)+(x-(x0+x1)/2)*scale/radius;r=radius-(y-(y0+y1)/2)*scale;mapped.append((r*math.sin(a),r*math.cos(a)))
   if len(mapped)>2:shape=shape.symmetric_difference(Polygon(mapped).buffer(0))
  triangles=constrained_delaunay_triangles(shape);sourcearea+=shape.area;trianglearea+=sum(t.area for t in triangles.geoms)
  for t in triangles.geoms:
   p=np.array([(x/1000,-.00078,z/1000) for x,z in list(t.exterior.coords)[:3]])
   if np.cross(p[1]-p[0],p[2]-p[0])[1]>0:p=p[::-1]
   points.extend(p.tolist())
  placements.append({'label':label,'angleDeg':angle,'radiusMm':radius,'widthMm':width,'heightMm':(y1-y0)*scale,'nativeAspect':(x1-x0)/(y1-y0)})
 for angle in [0,120,240]:add(mono,angle,logo_radius,3.30,'PS monogram')
 for angle in [60,180,300]:add(wordpaths,angle,logo_radius,7.15 if console=='ps3' else 6.71,console.upper())
 for value,angle,height in [('BPSS-012340A1' if console=='ps3' else 'B4DL-132540B1',271,.65),('IFPI LZ01',327,.35)]:
  if console in ['ps3','ps4']:
   from fontTools.ttLib import TTFont
   font='C:/Windows/Fonts/OCRAEXT.TTF';unit=bounds(text_paths(font,value,1));size=height/(unit[3]-unit[1]);face=TTFont(font);cmap=face.getBestCmap();factor=size/face['head'].unitsPerEm;offset=0;paths=[]
   # Space the clean glyphs physically, including clear character gaps.
   for character in value:
    paths.extend([[(x+offset,y) for x,y in contour] for contour in text_paths(font,character,size)])
    offset+=face['hmtx'][cmap[ord(character)]][0]*factor+.06
   x0,y0,x1,y1=bounds(paths);add(paths,angle,outer-.70,x1-x0,'Representative '+value)
  else:
   paths=text_paths('C:/Windows/Fonts/arial.ttf',value,1);x0,y0,x1,y1=bounds(paths);add(paths,angle,outer-.70,(x1-x0)*height/(y1-y0),'Representative '+value)
 assert abs(sourcearea-trianglearea)<1e-8
 replace(8,console.upper()+'_Native_Logo_And_Matrix_Outlines',[primitive(points,etched)])
 # Standalone neutral top template; no PS2 band is carried into these models.
 im=Image.new('RGBA',(2048,2048),(227,228,226,255));d=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',64);d.text((1024,480),'PLAYSTATION '+console[-1],font=font,anchor='mm',fill='#6d726e');small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',30);d.text((1024,1510),'YOUR ARTWORK',font=small,anchor='mm',fill='#9a9e99');d.ellipse((26,26,2022,2022),outline='#c3c7c1',width=2)
 imagepath=OUT/(console+'-label-template.png');im.save(imagepath);stream=io.BytesIO();im.save(stream,format='PNG');data=stream.getvalue();blob.extend(b'\0'*((-len(blob))%4));vi=len(g['bufferViews']);g['bufferViews'].append({'buffer':0,'byteOffset':len(blob),'byteLength':len(data)});blob.extend(data);imageindex=len(g['images']);g['images'].append({'bufferView':vi,'mimeType':'image/png'});textureindex=len(g['textures']);g['textures'].append({'source':imageindex,'sampler':g['textures'][0].get('sampler',0)});g['materials'][0]['pbrMetallicRoughness']['baseColorTexture']={'index':textureindex}
 # The broad PS watermark and its roughness mask belong only to PS2.
 data_pbr=g['materials'][1]['pbrMetallicRoughness'];data_pbr.pop('baseColorTexture',None);data_pbr.pop('metallicRoughnessTexture',None);data_pbr['roughnessFactor']=.075
 # Match the approved Xbox mirror response exactly, including extensions.
 xbox,xboxblob=load(OUT/'xbox-original-disc.glb');mirror=copy.deepcopy(next(m for m in xbox['materials'] if m['name']=='ORIGINAL_XBOX_TEST_PLAIN_REFLECTIVE_SILVER'))
 for material_index,name in [(1,console.upper()+'_XBOX_MIRROR_READ_SIDE'),(silver,console.upper()+'_XBOX_MIRROR_SECURITY_FIELD')]:
  replacement=copy.deepcopy(mirror);replacement['name']=name;g['materials'][material_index]=replacement
 
 # Resize only PS3's clear hub and moulded rings around the fixed 7.5 mm hole.
 if console=='ps3':
  ratio=(inner-7.5)/(11.4-7.5)
  for index in [3,4,5,6]:
   for primitive_data in g['meshes'][index]['primitives']:
    for key in ['POSITION','NORMAL']:
     ai=primitive_data['attributes'][key];a=g['accessors'][ai];v=g['bufferViews'][a['bufferView']];arr=np.frombuffer(blob,dtype='<f4',count=a['count']*3,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,3).copy()
     if key=='POSITION':
      radius=np.linalg.norm(arr[:,[0,2]],axis=1);newradius=.0075+(radius-.0075)*ratio;arr[:,0]*=newradius/radius;arr[:,2]*=newradius/radius
     else:
      arr[:,[0,2]]/=ratio;arr/=np.linalg.norm(arr,axis=1)[:,None]
     primitive_data['attributes'][key]=acc(arr,'VEC3')
 if console in ['ps3','ps4']:
  for index,source_name,suffix in [(track,'ORIGINAL_XBOX_TEST_PLAIN_REFLECTIVE_SILVER','MASTERING_TRACK'),(barsmat,'ORIGINAL_XBOX_REFERENCE_MASTERING_BARS','SECURITY_TAGS'),(etched,'ORIGINAL_XBOX_REFERENCE_MATRIX_LETTERING','ETCHED_MARKINGS')]:
   replacement=copy.deepcopy(next(m for m in xbox['materials'] if m['name']==source_name));replacement['name']=console.upper()+'_XBOX_SECURITY_'+suffix;g['materials'][index]=replacement
 if console in ['ps3','ps4']:
  # The read zone diffracts strongly; the inner mastering zone remains mirror.
  imported=[];texture_map={}
  def import_texture(index):
   if index in texture_map:return texture_map[index]
   texture=copy.deepcopy(xbox['textures'][index]);image=copy.deepcopy(xbox['images'][texture['source']]);view=xbox['bufferViews'][image['bufferView']];offset=view.get('byteOffset',0);data=xboxblob[offset:offset+view['byteLength']]
   blob.extend(b'\0'*((-len(blob))%4));vi=len(g['bufferViews']);g['bufferViews'].append({'buffer':0,'byteOffset':len(blob),'byteLength':len(data)});blob.extend(data);image['bufferView']=vi;image_index=len(g['images']);g['images'].append(image);imported.append(image_index);texture['source']=image_index
   if 'sampler' in texture:
    sampler=copy.deepcopy(xbox['samplers'][texture['sampler']]);texture['sampler']=len(g.setdefault('samplers',[]));g['samplers'].append(sampler)
   ti=len(g['textures']);g['textures'].append(texture);texture_map[index]=ti;return ti
  data_material=copy.deepcopy(xbox['materials'][1]);data_material['name']=console.upper()+'_XBOX_DIFFRACTIVE_DATA_AREA'
  data_material['normalTexture']['index']=import_texture(data_material['normalTexture']['index'])
  film=data_material['extensions']['KHR_materials_iridescence']['iridescenceThicknessTexture'];film['index']=import_texture(film['index'])
  g['materials'][1]=data_material;g.setdefault('extras',{})['modernImportedDataImages']=imported
  # Barcode carrier is the data surface itself, with etched marks above it.
  g['meshes'][13]['primitives'][0]['material']=1
  g['meshes'][8]['primitives'][0]['material']=1
 g['materials'][6]['name']='UNUSED_REMOVED_PS2_LABEL_BAND'
 g['meshes'][1]['name']=console.upper()+'_Silver_Data_Underside'
 g.setdefault('extras',{}).update({'modernPlayStationVersion':(13 if console=='ps3' else 9),'platform':console,'baseModel':'ps2-silver-disc.glb','baseSha256':sourcehash,'securityPlacements':placements,'securityTextSourceAreaMm2':sourcearea,'securityTriangleAreaMm2':trianglearea,'masteringRunsDeg':runs,'modernOuterDataTransitionVersion':1,'dataOuterRadiusMm':58.4,'plainRimOuterRadiusMm':59.4,'masteringTagHeightMm':tag_outer-tag_inner,'masteringGroupLayout':'Single quarter-ring sector, 43 to 133 degrees','securityOuterRadiusMm':outer,'securityInnerRadiusMm':inner,'mirrorFinishSource':'ORIGINAL_XBOX_TEST_PLAIN_REFLECTIVE_SILVER','referenceProportions':'PS3 close-up calibrated to a 15 mm hole: approx. 301 px hole diameter and 744 px security diameter; PS4 retained independently. Logos preserve SVG proportions.'})
 g['buffers'][0]['byteLength']=len(blob);j=json.dumps(g,separators=(',',':')).encode();j+=b' '*((-len(j))%4);blob.extend(b'\0'*((-len(blob))%4));target.write_bytes(struct.pack('<III',0x46546c67,2,28+len(j)+len(blob))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(blob),0x004e4942)+blob)
 print('Built',target.name,'from unchanged PS2 silver base, with supplied vector branding.')
if __name__=='__main__':
 for console in ['ps3','ps4']:build(console)
