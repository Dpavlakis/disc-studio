"""Xbox 360 silver disc, using the supplied Xbox symbol and X360 font."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,math,json,struct
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs';S=4096;C=S/2;scale=S/.12
foil=Image.new('RGB',(S,S),'#a8aaa6');d=ImageDraw.Draw(foil)
font=ImageFont.truetype(str(OUT/'branding-source'/'X360.ttf'),100)
def stamp(tile,r,angle):
 tile=tile.rotate(-angle,resample=Image.Resampling.BICUBIC,expand=True)
 a=math.radians(angle);x=C+math.sin(a)*r*scale;y=C-math.cos(a)*r*scale
 foil.paste(tile,(round(x-tile.width/2),round(y-tile.height/2)),tile)
logo=Image.open(ROOT/'work'/'xbox-logo.png').convert('RGBA').resize((145,145),Image.Resampling.LANCZOS)
logo.putalpha(logo.getchannel('A').point(lambda value:round(value*.2)))
for angle in range(0,360,90):stamp(logo,.0137,angle)
for center in [45,135,225,315]:
 text='XBOX 360';adv=[font.getlength(ch) for ch in text];factor=180/math.pi/(.0137*scale);angle=center-sum(adv)*factor/2
 for ch,width in zip(text,adv):
  tile=Image.new('RGBA',(140,160));bounds=font.getbbox(ch)
  # Center visible glyph bounds, rather than the font's ascender/baseline box.
  ImageDraw.Draw(tile).text((70-(bounds[0]+bounds[2])/2,80-(bounds[1]+bounds[3])/2),ch,font=font,fill='#868884')
  stamp(tile,.0137,angle+width*factor/2);angle+=width*factor
# Fine etched hatching changes reflectance, without painting lighting or rainbows.
rng=np.random.default_rng(360)
yy,xx=np.mgrid[:S,:S].astype(np.float32);xx-=C;yy-=C
rr=np.hypot(xx,yy);aa=np.arctan2(yy,xx)
# Thin directional etch lines with irregular phase, rather than repeating dots.
grain=1+.032*np.sin(yy*3.1+2*np.sin(xx*.035))+.012*np.sin(aa*1800+rr*.15)
grain=np.where((rr>.0111*scale)&(rr<.0163*scale),grain,1)
foil=Image.fromarray(np.uint8(np.clip((np.asarray(foil,dtype=np.float32)*.70+92)*grain[...,None],0,255))).convert('L')
# Preserve fine lines while keeping the embedded asset compact.
foil=foil.quantize(colors=16).convert('L')
foil.resize((2048,2048),Image.Resampling.LANCZOS).quantize(colors=32).save(OUT/'xbox360-holographic-ring.png',optimize=True)
# Separate reflective mastering inscriptions, arranged between barcode sectors.
mark_size=4096;mark_center=mark_size/2
marks=Image.new('RGBA',(mark_size,mark_size))
def inscription(text,center,radius,size):
 mf=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',size)
 rad=radius*mark_size/.12;adv=[mf.getlength(ch) for ch in text]
 angle=center-sum(adv)/rad*90/math.pi
 for ch,width in zip(text,adv):
  mid=angle+width/rad*90/math.pi
  tile=Image.new('RGBA',(80,80));ImageDraw.Draw(tile).text((40,40),ch,font=mf,fill=(155,153,144,255),anchor='mm')
  tile=tile.rotate(-mid,resample=Image.Resampling.BICUBIC,expand=True)
  a=math.radians(mid);px=mark_center+math.sin(a)*rad;py=mark_center-math.cos(a)*rad
  marks.alpha_composite(tile,(round(px-tile.width/2),round(py-tile.height/2)))
  angle+=width/rad*180/math.pi
inscription('1EA92F01-L1 24',225,.02055,22)
inscription('1EA92F01-L0 22',225,.01965,22)
inscription('IFPI LP73',315,.0194,14)
marks.quantize(colors=32,method=Image.Quantize.FASTOCTREE).save(OUT/'xbox360-mastering-inscriptions.png',optimize=True)
foil.crop((int(C-.0178*scale),int(C-.0178*scale),int(C+.0178*scale),int(C+.0178*scale))).resize((1000,1000)).save(OUT/'previews/xbox360-hub-preview.png')
art=Image.new('RGB',(2048,2048),'#e5e7e3');d=ImageDraw.Draw(art)
f=ImageFont.truetype(str(OUT/'branding-source'/'X360.ttf'),108)
d.text((1024,590),'YOUR XBOX 360 ART',font=f,fill='#273326',anchor='mm')
d.text((1024,1460),'Replace this image with your disc artwork',font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',38),fill='#4b554d',anchor='mm')
art.save(OUT/'xbox360-label-art.png')
Image.open(OUT/'groove-normal.png').resize((512,512),Image.Resampling.LANCZOS).save(OUT/'xbox360-groove-normal.png')
y,x=np.mgrid[:256,:256].astype(np.float32);a=np.arctan2(y-127.5,x-127.5);r=np.hypot(x-127.5,y-127.5)/256
# Optical response map, not a colored photograph: the renderer derives the
# reflected spectrum from this thickness and the current light/view direction.
# This approximates track diffraction using glTF's available thin-film model.
film=np.uint8(np.clip(.5+.48*np.sin(a*2),0,1)*255)
Image.fromarray(np.stack([film,film,film],axis=-1)).save(OUT/'xbox360-film-thickness.png')
# Molded lettering is relief in the clear plastic, with no opaque printed color.
hs=2048;hc=hs/2;hub_mask=Image.new('L',(hs,hs));hf=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',25)
code='IFPI KKA0';rad=.01095*hs/.12;adv=[hf.getlength(ch) for ch in code];angle=180-sum(adv)/rad*90/math.pi
for ch,width in zip(code,adv):
 tile=Image.new('L',(90,90));ImageDraw.Draw(tile).text((45,45),ch,font=hf,fill=255,anchor='mm')
 mid=angle+width/rad*90/math.pi;tile=tile.rotate(-mid,resample=Image.Resampling.BICUBIC,expand=True)
 a=math.radians(mid);px=hc+math.sin(a)*rad;py=hc-math.cos(a)*rad
 hub_mask.paste(tile,(round(px-tile.width/2),round(py-tile.height/2)),tile);angle+=width/rad*180/math.pi
height=np.asarray(hub_mask,dtype=np.float32)/255;gy,gx=np.gradient(height);nn=np.stack([-gx*.65,gy*.65,np.ones_like(gx)],axis=-1);nn/=np.linalg.norm(nn,axis=-1)[...,None]
Image.fromarray(np.uint8(np.clip(nn*.5+.5,0,1)*255)).save(OUT/'xbox360-hub-molded-normal.png')
g={'asset':{'version':'2.0','generator':'Xbox 360 disc studio'},'scene':0,'scenes':[{'nodes':[]}],'nodes':[],'meshes':[],'materials':[],'buffers':[{}],'bufferViews':[],'accessors':[],'images':[],'textures':[],'samplers':[{'magFilter':9729,'minFilter':9987,'wrapS':33071,'wrapT':33071}],'extensionsUsed':['KHR_materials_iridescence','KHR_materials_transmission','KHR_materials_ior','KHR_materials_clearcoat','KHR_materials_anisotropy']}
blob=bytearray()
def view(data):
 while len(blob)%4:blob.append(0)
 off=len(blob);blob.extend(data);g['bufferViews'].append({'buffer':0,'byteOffset':off,'byteLength':len(data)});return len(g['bufferViews'])-1
def acc(data,kind,integer=False):
 a=np.asarray(data,dtype='<u4' if integer else '<f4');v=view(a.tobytes());item={'bufferView':v,'componentType':5125 if integer else 5126,'count':len(a),'type':kind}
 if not integer:item.update(min=a.min(axis=0).tolist(),max=a.max(axis=0).tolist())
 g['accessors'].append(item);return len(g['accessors'])-1
for name in ['xbox360-label-art.png','xbox360-groove-normal.png','xbox360-holographic-ring.png','xbox360-mastering-inscriptions.png','xbox360-film-thickness.png']:
 g['images'].append({'bufferView':view((OUT/name).read_bytes()),'mimeType':'image/png','name':name});g['textures'].append({'source':len(g['images'])-1,'sampler':0})
g['materials']=[
 {'name':'TOP_ART_REPLACE_THIS_TEXTURE','alphaMode':'MASK','pbrMetallicRoughness':{'baseColorTexture':{'index':0},'metallicFactor':0,'roughnessFactor':.36}},
 {'name':'XBOX360_DATA_REFLECTIVE','doubleSided':True,'pbrMetallicRoughness':{'baseColorFactor':[.52,.52,.52,1],'metallicFactor':1,'roughnessFactor':.13},'normalTexture':{'index':1,'scale':.2},'extensions':{'KHR_materials_iridescence':{'iridescenceFactor':.22,'iridescenceIor':1.38,'iridescenceThicknessMinimum':380,'iridescenceThicknessMaximum':380},'KHR_materials_anisotropy':{'anisotropyStrength':.8},'KHR_materials_clearcoat':{'clearcoatFactor':.12,'clearcoatRoughnessFactor':.07}}},
 {'name':'CLEAR_XBOX360_POLYCARBONATE','alphaMode':'BLEND','pbrMetallicRoughness':{'baseColorFactor':[.92,.95,1,.22],'metallicFactor':0,'roughnessFactor':.06},'extensions':{'KHR_materials_transmission':{'transmissionFactor':.95},'KHR_materials_ior':{'ior':1.58}}},
 {'name':'XBOX360_HOLOGRAPHIC_AUTHENTICATION_RING','doubleSided':True,'pbrMetallicRoughness':{'baseColorTexture':{'index':2},'metallicFactor':1,'roughnessFactor':.19},'normalTexture':{'index':1,'scale':.12},'extensions':{'KHR_materials_iridescence':{'iridescenceFactor':.9,'iridescenceIor':1.42,'iridescenceThicknessMinimum':440,'iridescenceThicknessMaximum':440}}},
 {'name':'XBOX360_DARK_SMOOTH_RIM','pbrMetallicRoughness':{'baseColorFactor':[.002,.002,.002,1],'metallicFactor':1,'roughnessFactor':.23}},
 {'name':'XBOX360_CLEAR_MOULDED_RINGS','alphaMode':'BLEND','pbrMetallicRoughness':{'baseColorFactor':[.8,.85,.95,.28],'metallicFactor':0,'roughnessFactor':.09}},
 {'name':'XBOX360_SILVER_MASTERING_BAND','pbrMetallicRoughness':{'baseColorFactor':[.72,.72,.72,1],'metallicFactor':1,'roughnessFactor':.09}},
 {'name':'XBOX360_MASTERING_REFLECTIVE_BARS','pbrMetallicRoughness':{'baseColorFactor':[.52,.52,.52,1],'metallicFactor':1,'roughnessFactor':.13},'extensions':{'KHR_materials_iridescence':{'iridescenceFactor':.4,'iridescenceIor':1.38,'iridescenceThicknessMinimum':380,'iridescenceThicknessMaximum':380}}}
]
# Broad fixed thickness variation made the ring resemble a colored print.
# Use a neutral chrome foil with restrained, angle-dependent thin-film response.
g['materials'][1]['pbrMetallicRoughness'].update(baseColorFactor=[.68,.68,.68,1],roughnessFactor=.075)
g['materials'][1]['normalTexture']['scale']=.07
g['materials'][1]['extensions']['KHR_materials_iridescence'].update(iridescenceFactor=.85,iridescenceIor=1.3,iridescenceThicknessMinimum=120,iridescenceThicknessMaximum=1100,iridescenceThicknessTexture={'index':4})
g['materials'][1]['extensions']['KHR_materials_anisotropy'].update(anisotropyStrength=.95,anisotropyRotation=math.pi/2)
g['materials'][3]['extensions']['KHR_materials_iridescence'].update(iridescenceFactor=.85,iridescenceIor=1.3,iridescenceThicknessMinimum=120,iridescenceThicknessMaximum=1100,iridescenceThicknessTexture={'index':4})
g['materials'][3]['pbrMetallicRoughness'].update(roughnessFactor=.22,metallicFactor=.82)
# Match the established PS2 clear center and outer bevel material exactly.
g['materials'][2].update(alphaMode='BLEND',pbrMetallicRoughness={'baseColorFactor':[.92,.95,1,.22],'metallicFactor':0,'roughnessFactor':.06},extensions={'KHR_materials_transmission':{'transmissionFactor':.95},'KHR_materials_ior':{'ior':1.58},'KHR_materials_clearcoat':{'clearcoatFactor':1}})
g['materials'][5].update(alphaMode='BLEND',pbrMetallicRoughness={'baseColorFactor':[.8,.85,.95,.28],'metallicFactor':0,'roughnessFactor':.09})
g['materials'][5]['extensions']={'KHR_materials_iridescence':{'iridescenceFactor':.3,'iridescenceIor':1.3,'iridescenceThicknessMinimum':120,'iridescenceThicknessMaximum':1100,'iridescenceThicknessTexture':{'index':4}}}
# The band is silver; dark sectors in the photographs are reflected surroundings.
# Barcode contrast comes from a different surface finish on the same metal.
g['materials'][7]['pbrMetallicRoughness'].update(baseColorFactor=[.72,.72,.72,1],roughnessFactor=.25)
g['materials'].append({'name':'XBOX360_RAISED_IFPI_CLEAR_PLASTIC','alphaMode':'BLEND','pbrMetallicRoughness':{'baseColorFactor':[.82,.86,.92,.66],'metallicFactor':0,'roughnessFactor':.12},'extensions':{'KHR_materials_transmission':{'transmissionFactor':.55},'KHR_materials_ior':{'ior':1.58}}})
def surface(name,profile,mat,angle_ranges=None):
 p=[];norm=[];uv=[];tan=[];idx=[];resolution=128 if mat==9 else (256 if mat in (2,5) else (512 if mat==10 else (2048 if mat==4 else 1024)))
 for start,end in (angle_ranges or [(0,360)]):
  N=max(2,math.ceil((end-start)/360*resolution))
  for (ra,za),(rb,zb) in zip(profile,profile[1:]):
   dr=rb-ra;dz=zb-za;length=math.hypot(dr,dz);base=len(p)
   for i in range(N+1):
    a=math.radians(start+(end-start)*i/N);c=math.cos(a);s=math.sin(a)
    for rr,zz in [(ra,za),(rb,zb)]:
     p.append((rr*c,zz,rr*s));norm.append((dz/length*c,-dr/length,dz/length*s));uv.append((.5+(-1 if mat in (0,3) else 1)*rr*c/.12,.5-rr*s/.12));tan.append((-s,0,c,1))
   for i in range(N):
    k=base+2*i;idx.extend([k,k+1,k+3,k,k+3,k+2])
 attrs={'POSITION':acc(p,'VEC3'),'NORMAL':acc(norm,'VEC3'),'TEXCOORD_0':acc(uv,'VEC2'),'TANGENT':acc(tan,'VEC4')}
 g['meshes'].append({'name':name,'primitives':[{'attributes':attrs,'indices':acc(idx,'SCALAR',True),'material':mat}]})
 g['nodes'].append({'name':name,'mesh':len(g['meshes'])-1,'rotation':[-math.sqrt(.5),0,0,math.sqrt(.5)],'translation':[0,.06,0]});g['scenes'][0]['nodes'].append(len(g['nodes'])-1)
surface('01_Xbox360_Replaceable_Artwork',[(.0587,.00061),(.0162,.00061)],0)
surface('02_Xbox360_Silver_Underside',[(.0162,-.0006),(.0584,-.0006)],1)
surface('03_Xbox360_Clear_Outer_Bevel',[(.0594,-.0006),(.0598,-.0006),(.06,-.0004),(.06,.0004),(.0598,.0006),(.0594,.0006)],2)
# Smooth front face; the recessed concentric molding belongs only to the back.
hub_section=[(.0112,.00060),(.00765,.00060),(.00755,.00055),(.0075,.00045),(.0075,-.00045),(.0076,-.00060)]
rear_grooves=[(.0081,.00016),(.0095,.00014),(.0107,.00013)]
for r,w in rear_grooves:
 hub_section.append((r-w,-.00060))
 # Rounded U-shaped recess, 0.18 mm deep into the rear surface.
 hub_section.extend((r-w*math.cos(a),-.00060+.00018*math.sin(a)) for a in np.linspace(0,math.pi,9)[1:])
hub_section.extend([(.01105,-.00060),(.0112,-.00055),(.0112,.00060)])
surface('04_Xbox360_Clear_Hub',hub_section,2)
for i,(r,w) in enumerate(rear_grooves):
 # A narrow finish strip follows the recessed floor, with no raised front ring.
 profile=[(r-w*math.cos(a),-.000602+.00018*math.sin(a)) for a in np.linspace(math.pi*.42,math.pi*.58,5)]
 surface('05_Xbox360_Rear_Recessed_Ring_'+str(i),profile,5)
surface('06_Xbox360_Holographic_Center',[(.0162,.00064),(.0112,.00064)],3)
surface('07_Xbox360_Silver_Outer_Finish_Band',[(.0584,-.000605),(.0594,-.000605)],10)
surface('07b_Xbox360_Exposed_Silver_Between_Artwork_And_Clear_Rim',[(.0594,.00060),(.0587,.00060)],10)
# Rounded shoulder, shallow recessed channel, and a second fine outer bead.
# Multiple curved facets produce the paired highlights visible on the real lip.
bezel_profile=[(.01605,-.00064),(.01612,-.00068),(.01618,-.00076),(.01625,-.00081),(.01632,-.00082),(.01639,-.00079),(.01645,-.00072),(.01648,-.00065),(.01651,-.00063),(.01654,-.00067),(.01658,-.00072),(.01662,-.00073),(.01666,-.00070),(.01670,-.00066)]
surface('08_Xbox360_Rounded_Front_Hologram_Bezel',[(r,-y) for r,y in reversed(bezel_profile)],10)
surface('09_Xbox360_Reverse_Holographic_Center',[(.0112,-.00064),(.0162,-.00064)],3)
surface('10_Xbox360_Back_Mastering_Band',[(.01655,-.00066),(.0212,-.00066)],6)
surface('11_Xbox360_Rounded_Back_Hologram_Bezel',bezel_profile,10)
# Two narrow barcode rows, with reflective bars rather than white ink.
import random
def mastering_pattern(seed,arcs,widths,gaps):
 rng=random.Random(seed);result=[]
 for start,end in arcs:
  angle=start
  while angle<end:
   width=rng.choice(widths);result.append((angle,min(end,angle+width)));angle+=width+rng.choice(gaps)
 return result
outer=mastering_pattern(360,[(275,350)],[.35,.5,.75,1.1],[.2,.3,.5,.7])
inner=mastering_pattern(361,[(275,350)],[.35,.5,.75,1.1],[.2,.3,.5,.7])
middle=mastering_pattern(362,[(302,307)],[.3,.45,.7,1.0],[.3,.5,.9,1.5])
surface('12_Xbox360_Mastering_Barcode_Outer_Track',[(.02055,-.00072),(.0211,-.00072)],7,outer)
surface('13_Xbox360_Mastering_Barcode_Inner_Track',[(.0198,-.00072),(.02035,-.00072)],7,inner)
surface('14_Xbox360_Mastering_Barcode_Middle_Group',[(.0201,-.00072),(.0205,-.00072)],7,middle)
g['materials'].append({'name':'XBOX360_MASTERING_SERIAL_AND_IFPI','alphaMode':'MASK','alphaCutoff':.25,'pbrMetallicRoughness':{'baseColorTexture':{'index':3},'metallicFactor':1,'roughnessFactor':.25}})
g['materials'].append({'name':'XBOX360_SMOOTH_SILVER_EDGE_FINISH','pbrMetallicRoughness':{'baseColorFactor':[.72,.72,.72,1],'metallicFactor':1,'roughnessFactor':.19},'extensions':{'KHR_materials_clearcoat':{'clearcoatFactor':.2,'clearcoatRoughnessFactor':.1}}})
surface('14b_Xbox360_Mastering_Inscriptions',[(.0166,-.00076),(.02115,-.00076)],9)

# Rounded clear relief strokes make the mold code visible as real geometry.
# Coordinates below describe simple sans-serif letter strokes, not printed ink.
letters={
 'I':[[(.5,0),(.5,1)]],
 'F':[[(0,0),(0,1),(1,1)],[(0,.53),(.78,.53)]],
 'P':[[(0,0),(0,1),(.7,1),(1,.86),(1,.65),(.7,.53),(0,.53)]],
 'K':[[(0,0),(0,1)],[(1,1),(0,.48),(1,0)]],
 'A':[[(0,0),(.5,1),(1,0)],[(.22,.42),(.78,.42)]],
 '0':[[(.5+.5*math.cos(a),.5+.5*math.sin(a)) for a in np.linspace(0,math.tau,17)]]}
pos=[];normals=[];uvs=[];tangents=[];indices=[]
text='IFPI KKA0';advance=.00056;radius=.0102;stroke=.000018
def on_hub(x,y):
 a=math.pi+x/radius;r=radius+y
 return np.array([r*math.sin(a),-.00069,r*math.cos(a)])
for ci,ch in enumerate(text):
 for path in letters.get(ch,[]):
  for q0,q1 in zip(path,path[1:]):
   a=on_hub((ci-(len(text)-1)/2)*advance+(q0[0]-.5)*.0004,(q0[1]-.5)*.0007)
   b=on_hub((ci-(len(text)-1)/2)*advance+(q1[0]-.5)*.0004,(q1[1]-.5)*.0007)
   direction=b-a;direction/=np.linalg.norm(direction);up=np.array([0.,-1.,0.]);side=np.cross(direction,up);side/=np.linalg.norm(side);base=len(pos)
   for point in [a,b]:
    for k in range(6):
     angle=k/6*math.tau;n=up*math.cos(angle)+side*math.sin(angle);p=point+n*stroke
     pos.append(p);normals.append(n);uvs.append((0,0));tangents.append((*direction,1))
   for k in range(6):
    j=(k+1)%6;indices.extend([base+k,base+6+j,base+6+k,base+k,base+j,base+6+j])
attrs={'POSITION':acc(pos,'VEC3'),'NORMAL':acc(normals,'VEC3'),'TEXCOORD_0':acc(uvs,'VEC2'),'TANGENT':acc(tangents,'VEC4')}
g['meshes'].append({'name':'15_Raised_IFPI_KKA0_Mold_Lettering','primitives':[{'attributes':attrs,'indices':acc(indices,'SCALAR',True),'material':8}]})
g['nodes'].append({'name':'15_Raised_IFPI_KKA0_Mold_Lettering','mesh':len(g['meshes'])-1,'rotation':[-math.sqrt(.5),0,0,math.sqrt(.5)],'translation':[0,.06,0]});g['scenes'][0]['nodes'].append(len(g['nodes'])-1)
g['buffers'][0]['byteLength']=len(blob);js=json.dumps(g,separators=(',',':')).encode();js+=b' '*((-len(js))%4);blob+=b'\0'*((-len(blob))%4)
data=struct.pack('<III',0x46546c67,2,12+8+len(js)+8+len(blob))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(blob),0x004e4942)+blob
(OUT/'xbox360-silver-disc.glb').write_bytes(data)
print('Xbox 360 model:',len(g['meshes']),'parts;',len(data),'bytes')
