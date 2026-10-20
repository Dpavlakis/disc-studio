"""Xbox 360 silver disc, using the supplied Xbox symbol and X360 font."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,math,json,struct
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs';S=4096;C=S/2;scale=S/.12
foil=Image.new('RGB',(S,S),'#a8aaa6');d=ImageDraw.Draw(foil)
font=ImageFont.truetype(str(OUT/'branding-source'/'X360.ttf'),76)
def stamp(tile,r,angle):
 tile=tile.rotate(-angle,resample=Image.Resampling.BICUBIC,expand=True)
 a=math.radians(angle);x=C+math.sin(a)*r*scale;y=C-math.cos(a)*r*scale
 foil.paste(tile,(round(x-tile.width/2),round(y-tile.height/2)),tile)
logo=Image.open(ROOT/'work'/'xbox-logo.png').convert('RGBA').resize((155,155),Image.Resampling.LANCZOS)
logo.putalpha(logo.getchannel('A').point(lambda value:round(value*.2)))
for angle in range(0,360,90):stamp(logo,.01485,angle)
for center in [45,135,225,315]:
 text='XBOX 360';adv=[font.getlength(ch) for ch in text];factor=180/math.pi/(.01485*scale);angle=center-sum(adv)*factor/2
 for ch,width in zip(text,adv):
  tile=Image.new('RGBA',(140,160));ImageDraw.Draw(tile).text((70,80),ch,font=font,fill='#a8aaa6',stroke_width=1,stroke_fill='#777975',anchor='mm')
  stamp(tile,.01485,angle+width*factor/2);angle+=width*factor
# Fine etched hatching changes reflectance, without painting lighting or rainbows.
rng=np.random.default_rng(360);tile=rng.uniform(.94,1.035,(16,16)).astype(np.float32)
grain=np.tile(tile,(S//16,S//16))
foil=Image.fromarray(np.uint8(np.clip(np.asarray(foil,dtype=np.float32)*grain[...,None],0,255))).convert('L')
foil.save(OUT/'xbox360-holographic-ring.png')
foil.crop((int(C-.0178*scale),int(C-.0178*scale),int(C+.0178*scale),int(C+.0178*scale))).resize((1000,1000)).save(OUT/'xbox360-hub-preview.png')
art=Image.new('RGB',(2048,2048),'#e5e7e3');d=ImageDraw.Draw(art)
f=ImageFont.truetype(str(OUT/'branding-source'/'X360.ttf'),108)
d.text((1024,590),'YOUR XBOX 360 ART',font=f,fill='#273326',anchor='mm')
d.text((1024,1460),'Replace this image with your disc artwork',font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',38),fill='#4b554d',anchor='mm')
art.save(OUT/'xbox360-label-art.png')
Image.open(OUT/'groove-normal.png').resize((512,512),Image.Resampling.LANCZOS).save(OUT/'xbox360-groove-normal.png')
y,x=np.mgrid[:256,:256].astype(np.float32);a=np.arctan2(y-127.5,x-127.5);r=np.hypot(x-127.5,y-127.5)/256
film=np.uint8(np.clip(.5+.28*np.sin(a*3)+.14*np.sin(r*90),0,1)*255)
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
for name in ['xbox360-label-art.png','xbox360-groove-normal.png','xbox360-holographic-ring.png']:
 g['images'].append({'bufferView':view((OUT/name).read_bytes()),'mimeType':'image/png','name':name});g['textures'].append({'source':len(g['images'])-1,'sampler':0})
g['materials']=[
 {'name':'TOP_ART_REPLACE_THIS_TEXTURE','alphaMode':'MASK','pbrMetallicRoughness':{'baseColorTexture':{'index':0},'metallicFactor':0,'roughnessFactor':.36}},
 {'name':'XBOX360_DATA_REFLECTIVE','doubleSided':True,'pbrMetallicRoughness':{'baseColorFactor':[.52,.52,.52,1],'metallicFactor':1,'roughnessFactor':.13},'normalTexture':{'index':1,'scale':.2},'extensions':{'KHR_materials_iridescence':{'iridescenceFactor':.22,'iridescenceIor':1.38,'iridescenceThicknessMinimum':380,'iridescenceThicknessMaximum':380},'KHR_materials_anisotropy':{'anisotropyStrength':.8},'KHR_materials_clearcoat':{'clearcoatFactor':.12,'clearcoatRoughnessFactor':.07}}},
 {'name':'CLEAR_XBOX360_POLYCARBONATE','alphaMode':'BLEND','pbrMetallicRoughness':{'baseColorFactor':[.92,.95,1,.22],'metallicFactor':0,'roughnessFactor':.06},'extensions':{'KHR_materials_transmission':{'transmissionFactor':.95},'KHR_materials_ior':{'ior':1.58}}},
 {'name':'XBOX360_HOLOGRAPHIC_AUTHENTICATION_RING','doubleSided':True,'pbrMetallicRoughness':{'baseColorTexture':{'index':2},'metallicFactor':1,'roughnessFactor':.19},'normalTexture':{'index':1,'scale':.12},'extensions':{'KHR_materials_iridescence':{'iridescenceFactor':.9,'iridescenceIor':1.42,'iridescenceThicknessMinimum':440,'iridescenceThicknessMaximum':440}}},
 {'name':'XBOX360_DARK_SMOOTH_RIM','pbrMetallicRoughness':{'baseColorFactor':[.002,.002,.002,1],'metallicFactor':1,'roughnessFactor':.23}},
 {'name':'XBOX360_CLEAR_MOULDED_RINGS','alphaMode':'BLEND','pbrMetallicRoughness':{'baseColorFactor':[.8,.85,.95,.28],'metallicFactor':0,'roughnessFactor':.09}},
 {'name':'XBOX360_DARK_MASTERING_BAND','pbrMetallicRoughness':{'baseColorFactor':[.12,.12,.12,1],'metallicFactor':1,'roughnessFactor':.22}},
 {'name':'XBOX360_MASTERING_REFLECTIVE_BARS','pbrMetallicRoughness':{'baseColorFactor':[.52,.52,.52,1],'metallicFactor':1,'roughnessFactor':.13},'extensions':{'KHR_materials_iridescence':{'iridescenceFactor':.4,'iridescenceIor':1.38,'iridescenceThicknessMinimum':380,'iridescenceThicknessMaximum':380}}}
]
# Broad fixed thickness variation made the ring resemble a colored print.
# Use a neutral chrome foil with restrained, angle-dependent thin-film response.
g['materials'][3]['extensions']['KHR_materials_iridescence'].update(iridescenceFactor=.22,iridescenceThicknessMinimum=380,iridescenceThicknessMaximum=380)
g['materials'][3]['pbrMetallicRoughness']['roughnessFactor']=.105
g['materials'][6]['pbrMetallicRoughness'].update(baseColorFactor=[.025,.025,.025,1],roughnessFactor=.16)
g['materials'].append({'name':'XBOX360_RAISED_IFPI_CLEAR_PLASTIC','alphaMode':'BLEND','pbrMetallicRoughness':{'baseColorFactor':[.82,.86,.92,.66],'metallicFactor':0,'roughnessFactor':.12},'extensions':{'KHR_materials_transmission':{'transmissionFactor':.55},'KHR_materials_ior':{'ior':1.58}}})
def surface(name,profile,mat,angle_ranges=None):
 p=[];norm=[];uv=[];tan=[];idx=[];resolution=2048 if mat==4 else 1024
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
surface('01_Xbox360_Replaceable_Artwork',[(.0587,.00061),(.0173,.00061)],0)
surface('02_Xbox360_Silver_Underside',[(.0173,-.0006),(.0594,-.0006)],1)
surface('03_Xbox360_Clear_Outer_Bevel',[(.0594,-.0006),(.0598,-.0006),(.06,-.0004),(.06,.0004),(.0598,.0006),(.0594,.0006)],2)
surface('04_Xbox360_Clear_Hub',[(.0125,.0006),(.0075,.0006),(.0075,-.0006),(.0125,-.0006)],2)
for i,(r,w) in enumerate([(.0081,.0001),(.0101,.00008),(.0122,.00008)]):surface('05_Xbox360_Moulded_Ring_'+str(i),[(r-w,-.000605),(r-w,-.0007),(r+w,-.0007),(r+w,-.000605)],5)
surface('06_Xbox360_Holographic_Center',[(.0173,.00064),(.0125,.00064)],3)
surface('07_Xbox360_Smooth_Dark_Rim',[(.059,-.000605),(.0593,-.000605),(.0593,.000605),(.059,.000605),(.059,-.000605)],4)
surface('08_Xbox360_Hologram_Outer_Boundary',[(.0173,.00068),(.0171,.00068)],4)
surface('09_Xbox360_Reverse_Holographic_Center',[(.0125,-.00064),(.0173,-.00064)],3)
surface('10_Xbox360_Back_Mastering_Band',[(.01765,-.00066),(.0212,-.00066)],6)
surface('11_Xbox360_Back_Hologram_Chrome_Lip',[(.0173,-.00064),(.01745,-.00072),(.01765,-.00064)],1)
# Two narrow barcode rows, with reflective bars rather than white ink.
import random
def mastering_pattern(seed,arcs,widths,gaps):
 rng=random.Random(seed);result=[]
 for start,end in arcs:
  angle=start
  while angle<end:
   width=rng.choice(widths);result.append((angle,min(end,angle+width)));angle+=width+rng.choice(gaps)
 return result
outer=mastering_pattern(360,[(50,130),(230,310)],[.14,.2,.28,.42,.6],[.18,.25,.4,.65])
inner=mastering_pattern(361,[(58,124),(238,304)],[.12,.18,.3,.5],[.2,.35,.55,.8])
middle=mastering_pattern(362,[(154,174)],[.3,.45,.7,1.0],[.3,.5,.9,1.5])
surface('12_Xbox360_Mastering_Barcode_Outer_Track',[(.0206,-.00072),(.0211,-.00072)],7,outer)
surface('13_Xbox360_Mastering_Barcode_Inner_Track',[(.0196,-.00072),(.02,-.00072)],7,inner)
surface('14_Xbox360_Mastering_Barcode_Middle_Group',[(.0201,-.00072),(.0205,-.00072)],7,middle)

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
text='IFPI KKA0';advance=.00056;radius=.0109;stroke=.000018
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
