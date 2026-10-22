"""Separate foil material experiment; never rewrite the approved Xbox model."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,struct,math,hashlib
import numpy as np
root=Path(__file__).resolve().parents[1];out=root/'outputs'
source=out/'xbox360-silver-disc.glb';data=source.read_bytes();original=hashlib.sha256(data).hexdigest()
jn=struct.unpack_from('<I',data,12)[0];g=json.loads(data[20:20+jn]);bn=struct.unpack_from('<I',data,20+jn)[0]
blob=bytearray(data[28+jn:28+jn+bn])
S=4096;C=S/2;scale=S/.12
mask=Image.new('L',(S,S));font=ImageFont.truetype(str(out/'branding-source/X360.ttf'),100)
def stamp(tile,angle):
 tile=tile.rotate(-angle,resample=Image.Resampling.BICUBIC,expand=True)
 a=math.radians(angle);x=C+math.sin(a)*.0137*scale;y=C-math.cos(a)*.0137*scale
 mask.paste(tile,(round(x-tile.width/2),round(y-tile.height/2)),tile)
logo=Image.open(root/'work/xbox-logo.png').convert('RGBA').resize((145,145),Image.Resampling.LANCZOS).getchannel('A')
for angle in range(0,360,90):stamp(logo,angle)
for center in [45,135,225,315]:
 advances=[font.getlength(ch) for ch in 'XBOX 360'];factor=180/math.pi/(.0137*scale);angle=center-sum(advances)*factor/2
 for ch,width in zip('XBOX 360',advances):
  tile=Image.new('L',(140,160));b=font.getbbox(ch)
  ImageDraw.Draw(tile).text((70-(b[0]+b[2])/2,80-(b[1]+b[3])/2),ch,font=font,fill=255)
  stamp(tile,angle+width*factor/2);angle+=width*factor
mask=mask.resize((2048,2048),Image.Resampling.LANCZOS);security=np.asarray(mask,dtype=np.float32)/255
mr=np.full((2048,2048,3),255,dtype=np.uint8);mr[:,:,1]=np.uint8(255*(.045+.14*security))
mrpath=out/'xbox360-test-metal-roughness.png';Image.fromarray(mr).save(mrpath,optimize=True)
yy,xx=np.mgrid[:2048,:2048].astype(np.float32);xx=(xx-1024)*.12/2048;yy=(yy-1024)*.12/2048
radius=np.hypot(xx,yy);azimuth=np.arctan2(yy,xx)
annulus=(radius>.01115)&(radius<.01625)
# Local circular cells form small overlapping swirls inside the security band,
# rather than one set of circles centered on the disc hole.
background=annulus*(1-security)
waves=np.zeros_like(radius);optical=np.zeros_like(radius);weights=np.zeros_like(radius)
for i in range(12):
 angle=i*math.tau/12;cr=.0137+.00065*math.sin(i*2.3)
 distance=np.hypot(xx-cr*math.cos(angle),yy-cr*math.sin(angle))
 weight=np.exp(-(distance/.00315)**4)
 waves+=weight*np.sin(distance*math.tau/.00032)
 optical+=weight*np.sin(distance*math.tau/.0015)
 weights+=weight
waves/=np.maximum(weights,1e-6);optical/=np.maximum(weights,1e-6)
wy,wx=np.gradient(waves);gy,gx=np.gradient(security)
# Transform the circle slopes into the mesh's circumferential tangent frame.
tx=-np.sin(azimuth);ty=np.cos(azimuth);rx=np.cos(azimuth);ry=np.sin(azimuth)
nx=(wx*tx+wy*ty)*.13*background+gx*.3
ny=(wx*rx+wy*ry)*.13*background-gy*.3
n=np.stack([nx,ny,np.ones_like(gx)],axis=-1);n/=np.linalg.norm(n,axis=-1)[...,None]
normalpath=out/'xbox360-test-security-normal.png';Image.fromarray(np.uint8(np.clip(n*.5+.5,0,1)*255)).save(normalpath,optimize=True)
# Circles modulate highlight shape and width, not a persistent colored pattern.
roughness=.045+.025*(waves*.5+.5)*background+.14*security
mr[:,:,1]=np.uint8(np.clip(roughness,0,1)*255)
Image.fromarray(mr).save(mrpath,optimize=True)
# A grayscale optical thickness map supplies a range of spectra. Color itself
# is still calculated by the renderer from view/light angle, not painted RGB.
# Keep the local circles in the microrelief, but reduce their constant hue
# contrast. Sharper specular reflections carry the stronger moving response.
thickness=.5+.42*np.sin(azimuth*3+radius*300)
thickness=np.where(annulus,thickness,.5)
film=np.full((2048,2048,3),255,dtype=np.uint8)
film[:,:,0]=np.uint8(255*(.12+.88*security)*annulus)
film[:,:,1]=np.uint8(np.clip(thickness,0,1)*255)
filmpath=out/'xbox360-test-optical-thickness.png';Image.fromarray(film).save(filmpath,optimize=True)
# Each circular cell supplies its own local reflection axis. Logo regions get
# a different direction from the backing foil, breaking the single broad lobe.
oy,ox=np.gradient(optical);dt=ox*tx+oy*ty;dr=ox*rx+oy*ry
direction=np.arctan2(dr,dt)+security*math.pi/3
flow=np.full((2048,2048,3),255,dtype=np.uint8)
# Blend the local circle flow with the common radial foil flow, avoiding
# isolated pinwheel-like mirror patches around every cell.
dx=.10*np.cos(direction);dy=.90+.10*np.sin(direction)
dl=np.maximum(np.hypot(dx,dy),1e-6);dx/=dl;dy/=dl
flow[:,:,0]=np.uint8((dx*.5+.5)*255)
flow[:,:,1]=np.uint8((dy*.5+.5)*255)
flowpath=out/'xbox360-test-local-anisotropy.png';Image.fromarray(flow).save(flowpath,optimize=True)
def texture(path):
 while len(blob)%4:blob.append(0)
 raw=path.read_bytes();g['bufferViews'].append({'buffer':0,'byteOffset':len(blob),'byteLength':len(raw)});blob.extend(raw)
 g['images'].append({'bufferView':len(g['bufferViews'])-1,'mimeType':'image/png','name':path.name})
 g['textures'].append({'source':len(g['images'])-1,'sampler':0});return len(g['textures'])-1
mrindex=texture(mrpath);normalindex=texture(normalpath);filmindex=texture(filmpath);flowindex=texture(flowpath)
m=g['materials'][3];m['name']='XBOX360_TEST_ANISOTROPIC_SECURITY_FOIL'
m['pbrMetallicRoughness']={'baseColorFactor':[.82,.82,.82,1],'metallicFactor':1,'roughnessFactor':1,'metallicRoughnessTexture':{'index':mrindex}}
m['normalTexture']={'index':normalindex,'scale':.8}
# The source mesh tangent is circumferential, so a quarter turn gives a radial
# anisotropy direction (equivalent to zero rotation with an explicit radial tangent).
m['extensions']={'KHR_materials_anisotropy':{'anisotropyStrength':.9,'anisotropyRotation':math.pi/2},'KHR_materials_iridescence':{'iridescenceFactor':.22,'iridescenceIor':1.45,'iridescenceThicknessMinimum':360,'iridescenceThicknessMaximum':360}}
# Match the broad silver bands without changing the rounded divider bezel.
# The divider shares material 10 with the outer finish in the source model,
# so give only the broad outer finish its own material before altering it.
import copy
plain={'name':'XBOX360_TEST_PLAIN_REFLECTIVE_SILVER','pbrMetallicRoughness':{'baseColorFactor':[.82,.82,.82,1],'metallicFactor':1,'roughnessFactor':.045},'extensions':copy.deepcopy(m['extensions'])}
g['materials'][6]=copy.deepcopy(plain)
outer_material=len(g['materials']);g['materials'].append(copy.deepcopy(plain))
for mesh in g['meshes']:
 if mesh['name'] in ('07_Xbox360_Silver_Outer_Finish_Band','07b_Xbox360_Exposed_Silver_Between_Artwork_And_Clear_Rim'):
  for primitive in mesh['primitives']:primitive['material']=outer_material
# A sharper isotropic reflection keeps the narrow lip and recessed channel
# readable independently of the broad anisotropic reflection on either side.
g['materials'][10]['pbrMetallicRoughness']['roughnessFactor']=.10
# Close the foil sandwich at its circular boundaries, without filling the
# central spindle hole or adding an opaque plate over the clear hub.
def array_accessor(values,kind,integer=False):
 a=np.asarray(values,dtype='<u4' if integer else '<f4')
 while len(blob)%4:blob.append(0)
 g['bufferViews'].append({'buffer':0,'byteOffset':len(blob),'byteLength':a.nbytes});blob.extend(a.tobytes())
 item={'bufferView':len(g['bufferViews'])-1,'componentType':5125 if integer else 5126,'count':len(a),'type':kind}
 if not integer:item.update(min=a.min(axis=0).tolist(),max=a.max(axis=0).tolist())
 g['accessors'].append(item);return len(g['accessors'])-1
positions=[];normals=[];uv=[];tangents=[];indices=[]
for radius,sign in ((.0112,-1),(.0162,1)):
 for i in range(512):
  base=len(positions)
  for angle,y in ((i*math.tau/512,-.00064),((i+1)*math.tau/512,-.00064),((i+1)*math.tau/512,.00064),(i*math.tau/512,.00064)):
   c=math.cos(angle);s=math.sin(angle);positions.append((radius*c,y,radius*s));normals.append((sign*c,0,sign*s));uv.append((0,0));tangents.append((-s,0,c,1))
  for tri in ((0,1,2),(0,2,3)):
   a,b,c=[base+k for k in tri]
   face=np.cross(np.array(positions[b])-positions[a],np.array(positions[c])-positions[a])
   indices.extend((a,b,c) if np.dot(face,normals[a])>0 else (a,c,b))
attrs={'POSITION':array_accessor(positions,'VEC3'),'NORMAL':array_accessor(normals,'VEC3'),'TEXCOORD_0':array_accessor(uv,'VEC2'),'TANGENT':array_accessor(tangents,'VEC4')}
g['meshes'].append({'name':'20_Security_Foil_Closed_Edge_Walls','primitives':[{'attributes':attrs,'indices':array_accessor(indices,'SCALAR',True),'material':10}]})
g['nodes'].append({'name':'20_Security_Foil_Closed_Edge_Walls','mesh':len(g['meshes'])-1,'rotation':[-math.sqrt(.5),0,0,math.sqrt(.5)],'translation':[0,.06,0]});g['scenes'][0]['nodes'].append(len(g['nodes'])-1)
g['asset']['generator']='Xbox 360 – Test: roughness security mask, radial anisotropy and thin-film foil'
g['buffers'][0]['byteLength']=len(blob);js=json.dumps(g,separators=(',',':')).encode();js+=b' '*((-len(js))%4);blob+=b'\0'*((-len(blob))%4)
result=struct.pack('<III',0x46546c67,2,28+len(js)+len(blob))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(blob),0x004e4942)+blob
(out/'xbox360-test.glb').write_bytes(result)
assert hashlib.sha256(source.read_bytes()).hexdigest()==original
assert m['pbrMetallicRoughness']['metallicFactor']==1 and 'baseColorTexture' not in m['pbrMetallicRoughness']
print('Xbox 360 – Test created; original model verified unchanged:',original)

from disc_edge_caps import cap_outer_edge
cap_outer_edge(out/'xbox360-test.glb')
