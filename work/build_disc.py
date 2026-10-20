import json, struct, math, io
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
exec((Path(__file__).parent/'make_hub.py').read_text(encoding='utf-8'))

OUT=Path(__file__).resolve().parents[1]/'outputs'
OUT.mkdir(exist_ok=True)
S=2048
art=Image.new('RGB',(S,S),'#e7e3dc')
d=ImageDraw.Draw(art)
for r,col in [(1010,'#161a24'),(986,'#e7e3dc'),(199,'#242936')]:
 d.ellipse((S/2-r,S/2-r,S/2+r,S/2+r),fill=col)
fontpath='C:/Windows/Fonts/arial.ttf'
f=ImageFont.truetype(fontpath,86); small=ImageFont.truetype(fontpath,34)
d.text((1024,540),'YOUR DISC ART',font=f,fill='#161a24',anchor='mm')
d.text((1024,660),'Replace label-art.png with your square artwork',font=small,fill='#414857',anchor='mm')
d.text((1024,1480),'120 mm  /  BLUE OPTICAL DISC',font=small,fill='#414857',anchor='mm')
art.save(OUT/'label-art.png')
badge=Image.new('RGBA',(S,S));bd=ImageDraw.Draw(badge)
bd.rectangle((0,1643,S,S),fill=(0,0,0,255))
bd.line((0,1642,S,1642),fill=(240,240,240,255),width=2)
word=Image.open(Path(__file__).parent/'ps2-top-wordmark.png').convert('RGBA')
word=word.resize((912,round(word.height*912/word.width)),Image.Resampling.LANCZOS)
badge.alpha_composite(word,((S-word.width)//2,1712))
# Match the physical label's circular boundary.
clip=Image.new('L',(S,S));ImageDraw.Draw(clip).ellipse((10,10,S-10,S-10),fill=255)
badge.putalpha(Image.fromarray(np.minimum(np.asarray(badge.getchannel('A')),np.asarray(clip))))
badge.save(OUT/'top-ps2-branding.png')
# Faint mastering logos belong to the reflective substrate, not a decal layer.
finish=Image.new('RGB',(S,S),'white')
mask=Image.new('L',(S,S),0)
logo=Image.open(Path(__file__).parent/'ps-logo.png').convert('RGBA')
logo=logo.resize((270,round(logo.height*270/logo.width)),Image.Resampling.LANCZOS)
# Registration symbol is part of the supplied SVG geometry.
for angle in range(20,360,60):
 tile=logo.rotate(-angle,resample=Image.Resampling.BICUBIC,expand=True)
 a=math.radians(angle); px=S/2+math.sin(a)*.048*S/.12; py=S/2-math.cos(a)*.048*S/.12
 pos=(round(px-tile.width/2),round(py-tile.height/2))
 mask.paste(tile.getchannel('A'),pos)
finish.paste(Image.new('RGB',(S,S),'#f5f5f5'),(0,0),mask)
finish.save(OUT/'disc-substrate-marks.png')
mr=np.empty((S,S,3),dtype=np.uint8);mr[:,:,0]=255;mr[:,:,1]=np.uint8(255*.115+np.asarray(mask)*.015);mr[:,:,2]=255
Image.fromarray(mr).save(OUT/'disc-substrate-roughness.png')
# Subtle concentric surface micro-normal. No baked highlights or rainbow colors.
y,x=np.mgrid[0:S,0:S]; x=(x+.5)/S-.5; y=(y+.5)/S-.5
r=np.sqrt(x*x+y*y); slope=.045*np.sin(r*math.tau*1400)
n=np.stack((slope*x/(r+1e-8),slope*y/(r+1e-8),np.ones_like(r)),axis=-1)
n/=np.linalg.norm(n,axis=-1)[...,None]
normal=Image.fromarray(np.uint8(np.clip(n*.5+.5,0,1)*255)); normal.save(OUT/'groove-normal.png')
g={'asset':{'version':'2.0','generator':'PS2 blue disc builder'},'scene':0,'scenes':[{'nodes':[]}], 'nodes':[], 'meshes':[], 'materials':[], 'buffers':[{}], 'bufferViews':[], 'accessors':[], 'images':[], 'textures':[], 'samplers':[{'magFilter':9729,'minFilter':9987,'wrapS':33071,'wrapT':33071}], 'extensionsUsed':['KHR_materials_iridescence','KHR_materials_anisotropy','KHR_materials_clearcoat','KHR_materials_transmission','KHR_materials_ior']}
blob=bytearray()
def view(data):
 while len(blob)%4: blob.append(0)
 off=len(blob); blob.extend(data); g['bufferViews'].append({'buffer':0,'byteOffset':off,'byteLength':len(data)}); return len(g['bufferViews'])-1
def acc(a,typ):
 a=np.asarray(a,dtype='<f4'); v=view(a.tobytes()); g['accessors'].append({'bufferView':v,'componentType':5126,'count':len(a),'type':typ,'min':a.min(axis=0).tolist(),'max':a.max(axis=0).tolist()}); return len(g['accessors'])-1
for name in ['label-art.png','groove-normal.png','hub-branding.png','hub-metal-roughness.png','disc-substrate-marks.png','disc-substrate-roughness.png','top-ps2-branding.png']:
 g['images'].append({'bufferView':view((OUT/name).read_bytes()),'mimeType':'image/png','name':name}); g['textures'].append({'source':len(g['images'])-1,'sampler':0})
g['materials']=[
 {'name':'TOP_ART_REPLACE_THIS_TEXTURE','pbrMetallicRoughness':{'baseColorTexture':{'index':0},'metallicFactor':0,'roughnessFactor':.36}},
 {'name':'BLUE_DATA_REFLECTIVE','pbrMetallicRoughness':{'baseColorFactor':[.012,.018,.55,1],'metallicFactor':.92,'roughnessFactor':.115},'normalTexture':{'index':1,'scale':.25},'extensions':{'KHR_materials_iridescence':{'iridescenceFactor':.72,'iridescenceIor':1.38,'iridescenceThicknessMinimum':380,'iridescenceThicknessMaximum':380},'KHR_materials_anisotropy':{'anisotropyStrength':.83,'anisotropyRotation':0},'KHR_materials_clearcoat':{'clearcoatFactor':1,'clearcoatRoughnessFactor':.07}}},
 {'name':'CLEAR_BLUE_HUB','pbrMetallicRoughness':{'baseColorFactor':[.09,.12,.47,1],'metallicFactor':.08,'roughnessFactor':.12},'extensions':{'KHR_materials_transmission':{'transmissionFactor':.78},'KHR_materials_ior':{'ior':1.58},'KHR_materials_clearcoat':{'clearcoatFactor':1}}},
 {'name':'BLUE_POLISHED_EDGE','pbrMetallicRoughness':{'baseColorFactor':[.012,.015,.14,1],'metallicFactor':.65,'roughnessFactor':.15}},
 {'name':'HUB_MOULDED_RINGS','pbrMetallicRoughness':{'baseColorFactor':[.025,.04,.22,1],'metallicFactor':.6,'roughnessFactor':.2}}
]
g['materials'].append({'name':'ETCHED_PLAYSTATION_INNER_RING','pbrMetallicRoughness':{'baseColorTexture':{'index':2},'metallicFactor':.92,'roughnessFactor':1,'metallicRoughnessTexture':{'index':3}},'extensions':{'KHR_materials_iridescence':{'iridescenceFactor':.6,'iridescenceIor':1.38,'iridescenceThicknessMinimum':320,'iridescenceThicknessMaximum':320},'KHR_materials_clearcoat':{'clearcoatFactor':.7,'clearcoatRoughnessFactor':.09}}})
g['materials'].append({'name':'TOP_PERMANENT_PS2_BRANDING','alphaMode':'MASK','alphaCutoff':.5,'pbrMetallicRoughness':{'baseColorTexture':{'index':6},'metallicFactor':0,'roughnessFactor':.38}})
g['materials'].append({'name':'SOLID_DARK_OUTER_RING','pbrMetallicRoughness':{'baseColorFactor':[.006,.006,.006,1],'metallicFactor':.15,'roughnessFactor':.23}})
g['materials'].append({'name':'INNER_RING_REFLECTIVE_SEPARATOR','pbrMetallicRoughness':{'baseColorFactor':[.48,.48,.48,1],'metallicFactor':1,'roughnessFactor':.12}})
def surface(name,profile,mat,angle_ranges=None):
 p=[]; norms=[]; uv=[]; tan=[]; resolution=2048 if mat in (2,4,5,7,8) else 512
 for start,end in (angle_ranges or [(0,360)]):
  N=max(2,math.ceil((end-start)/360*resolution))
  for j in range(len(profile)-1):
   ra,za=profile[j]; rb,zb=profile[j+1]; dr=rb-ra; dz=zb-za; length=math.hypot(dr,dz)
   for i in range(N):
    for rr,zz,k in [(ra,za,i),(rb,zb,i),(rb,zb,i+1),(ra,za,i),(rb,zb,i+1),(ra,za,i+1)]:
     a=math.radians(start+(end-start)*k/N); c=math.cos(a); s=math.sin(a)
     p.append((rr*c,zz,rr*s)); norms.append((dz/length*c,-dr/length,dz/length*s)); uv.append((.5+(-1 if mat in (0,6) else 1)*rr*c/.12,.5+(-1 if mat in (0,1,5,6) else 1)*rr*s/.12)); tan.append((-s,0,c,1))
 attrs={'POSITION':acc(p,'VEC3'),'NORMAL':acc(norms,'VEC3'),'TEXCOORD_0':acc(uv,'VEC2'),'TANGENT':acc(tan,'VEC4')}
 g['meshes'].append({'name':name,'primitives':[{'attributes':attrs,'material':mat}]}); g['nodes'].append({'name':name,'mesh':len(g['meshes'])-1}); g['scenes'][0]['nodes'].append(len(g['nodes'])-1)
# Profile winding makes outward-facing normals. Units are meters; disc lies XZ, top +Y.
surface('01_Replaceable_Art_Top',[(.0587,.00061),(.0114,.00061)],0)
surface('02_Blue_Data_Underside',[(.022,-.0006),(.0594,-.0006)],1)
surface('03_Outer_Bevel_Edge',[(.0594,-.0006),(.0598,-.0006),(.06,-.0004),(.06,.0004),(.0598,.0006),(.0594,.0006)],2)
surface('04_Clear_Centre_Hub',[(.0114,.0006),(.0075,.0006),(.0075,-.0006),(.0114,-.0006)],2)
for j,(rr,w) in enumerate([(.0081,.0001),(.0095,.00008),(.011,.00008)]):
 surface('05_Moulded_Ring_'+str(j),[(rr-w,-.000605),(rr-w,-.0007),(rr+w,-.0007),(rr+w,-.000605)],4)
surface('06_Etched_Branding_Matrix_Ring',[(.0114,-.00066),(.022,-.00066)],5)
surface('07_Top_PS2_Branding_Above_Artwork',[(.0587,.00064),(.0114,.00064)],6)
surface('08_Smooth_Outer_Ring_Both_Sides',[(.0590,-.000605),(.0593,-.000605),(.0593,.000605),(.0590,.000605),(.0590,-.000605)],7)
def precision_ring(name,ri,ro,material,depth=-.00074):
 surface(name,[(ri,depth),(ro,depth)],material)
precision_ring('09_Smooth_Matrix_Outer_Boundary',.02181,.02195,7)
precision_ring('10_Smooth_Matrix_Inner_Dark_Boundary',.01945,.02005,7)
precision_ring('11_Smooth_Reflective_Separator',.01961,.01969,8,-.00080)
# Angles in the measured texture run clockwise from its top; convert to XZ.
surface('12_Geometric_Barcode_End_Blocks',[(.02005,-.00074),(.02181,-.00074)],7,[(105,109),(204,207)])
runs=json.loads((Path(__file__).parent/'barcode-runs.json').read_text())
gaps=[];cursor=199
for a,b in runs:
 if a>cursor:gaps.append((cursor-90,a-90))
 cursor=max(cursor,b)
if cursor<294:gaps.append((cursor-90,204))
surface('13_Geometric_Barcode_Dark_Gaps',[(.02005,-.00074),(.02181,-.00074)],7,gaps)
g['materials'][7]['doubleSided']=True
g['materials'][8]['doubleSided']=True
g['materials'][7]['pbrMetallicRoughness'].update(baseColorFactor=[.002,.002,.002,1],metallicFactor=1,roughnessFactor=.23)
g['materials'][8]['name']='DISC_COLORED_BARCODE_AND_SEPARATOR'
g['materials'][8]['pbrMetallicRoughness'].update(baseColorFactor=[.012,.018,.55,1],metallicFactor=1,roughnessFactor=.14)
g['materials'][8]['extensions']={'KHR_materials_iridescence':{'iridescenceFactor':.35,'iridescenceIor':1.38,'iridescenceThicknessMinimum':380,'iridescenceThicknessMaximum':380}}
g['materials'][2]['name']='CLEAR_CENTRE_POLYCARBONATE'
g['materials'][2]['alphaMode']='BLEND'
g['materials'][2]['pbrMetallicRoughness'].update(baseColorFactor=[.92,.95,1,.22],metallicFactor=0,roughnessFactor=.06)
g['materials'][2]['extensions']['KHR_materials_transmission']['transmissionFactor']=.95
g['materials'][4]['alphaMode']='BLEND'
g['materials'][4]['pbrMetallicRoughness'].update(baseColorFactor=[.8,.85,.95,.28],metallicFactor=0,roughnessFactor=.09)
# Bare substrate is visible from either side. The same etching naturally reads
# mirrored when viewed from the artwork side, with no duplicated logo layer.
g['materials'][1]['doubleSided']=True
g['materials'][1]['pbrMetallicRoughness'].update(baseColorTexture={'index':4},metallicRoughnessTexture={'index':5},roughnessFactor=1)
g['materials'][5]['doubleSided']=True
g['materials'][5]['alphaMode']='MASK'
g['materials'][5]['alphaCutoff']=.5
g['materials'][5]['pbrMetallicRoughness']['baseColorFactor']=[.012,.018,.55,1]
g['materials'][5]['pbrMetallicRoughness']['metallicFactor']=1
g['materials'][5]['extensions']['KHR_materials_clearcoat']['clearcoatFactor']=0
g['materials'][5]['extensions']['KHR_materials_iridescence']['iridescenceFactor']=0
# A single-sided substrate on either side of the mastering film keeps the
# cutouts metallic from both viewing directions without hiding the reverse etch.
substrate=json.loads(json.dumps(g['materials'][1]));substrate['name']='INNER_DISC_SUBSTRATE';substrate['doubleSided']=False
g['materials'].append(substrate)
surface('14_Inner_Reflective_Substrate',[(.0114,-.0006),(.022,-.0006),(.022,-.0009),(.0114,-.0009),(.0114,-.0006)],9)
# Stand on the rim: rotate -90 degrees about X, then raise by the radius.
for node in g['nodes']:
 node['rotation']=[-math.sqrt(.5),0,0,math.sqrt(.5)]
 node['translation']=[0,.06,0]
g['buffers'][0]['byteLength']=len(blob)
js=json.dumps(g,separators=(',',':')).encode(); js+=b' '*((-len(js))%4); blob+=b'\0'*((-len(blob))%4)
glb=struct.pack('<III',0x46546c67,2,12+8+len(js)+8+len(blob))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(blob),0x004e4942)+blob
(OUT/'ps2-blue-disc.glb').write_bytes(glb)
for variant,color,metal,rough,iri in [('silver',[.52,.52,.52,1],1,.16,.14),('gold',[.68,.45,.14,1],1,.14,.28),('black',[.009,.006,.014,1],.35,.13,.18)]:
 m=g['materials'][1]; m['name']=variant.upper()+'_DATA_REFLECTIVE'
 m['pbrMetallicRoughness'].update(baseColorFactor=color,metallicFactor=metal,roughnessFactor=1)
 m['extensions']['KHR_materials_iridescence']['iridescenceFactor']=iri
 g['materials'][5]['pbrMetallicRoughness']['baseColorFactor']=color
 g['materials'][5]['extensions']['KHR_materials_iridescence']['iridescenceFactor']=0
 g['materials'][8]['pbrMetallicRoughness']['baseColorFactor']=color
 g['materials'][8]['pbrMetallicRoughness']['metallicFactor']=metal
 g['materials'][8]['extensions']['KHR_materials_iridescence']['iridescenceFactor']=iri
 m['extensions']['KHR_materials_clearcoat']['clearcoatFactor']=.15 if variant=='silver' else .65
 g['materials'][9]=json.loads(json.dumps(m));g['materials'][9]['name']='INNER_DISC_SUBSTRATE';g['materials'][9]['doubleSided']=False
 g['materials'][3]['pbrMetallicRoughness']['baseColorFactor']=[c*.35 for c in color[:3]]+[1]
 j=json.dumps(g,separators=(',',':')).encode(); j+=b' '*((-len(j))%4)
 b=struct.pack('<III',0x46546c67,2,12+8+len(j)+8+len(blob))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(blob),0x004e4942)+blob
 (OUT/(('ps1-' if variant=='black' else 'ps2-')+variant+'-disc.glb')).write_bytes(b)
print('Created GLB:',len(glb),'bytes;',len(g['meshes']),'separate mesh parts')
