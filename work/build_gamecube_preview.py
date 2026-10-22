"""Separate, unapplied GameCube construction study. Units: metres in GLB."""
import json, struct, math, copy, os, subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from ps1_silver_response import apply_xbox_silver_response
from original_xbox_vectors import text_paths,bounds

OUT=Path(__file__).resolve().parents[1]/'outputs'
g={'asset':{'version':'2.0','generator':'GameCube reference construction study'},'scene':0,'scenes':[{'nodes':[]}], 'nodes':[], 'meshes':[], 'materials':[], 'buffers':[{}], 'bufferViews':[], 'accessors':[], 'images':[], 'textures':[], 'samplers':[], 'extensionsUsed':['KHR_materials_iridescence','KHR_materials_anisotropy','KHR_materials_clearcoat','KHR_materials_transmission','KHR_materials_ior']}
blob=bytearray()
def view(data):
 while len(blob)%4:blob.append(0)
 i=len(g['bufferViews']);g['bufferViews'].append({'buffer':0,'byteOffset':len(blob),'byteLength':len(data)});blob.extend(data);return i
def acc(data,typ):
 a=np.asarray(data,dtype='<f4');g['accessors'].append({'bufferView':view(a.tobytes()),'componentType':5126,'count':len(a),'type':typ,'min':a.min(axis=0).tolist(),'max':a.max(axis=0).tolist()});return len(g['accessors'])-1
def material(name,color,metal,rough,ext=None):
 g['materials'].append({'name':name,'pbrMetallicRoughness':{'baseColorFactor':color,'metallicFactor':metal,'roughnessFactor':rough},'extensions':ext or {}});return len(g['materials'])-1
silver=material('PS1_FRONT_MASTERING_FOIL',[.68,.68,.68,1],1,.075)
apply_xbox_silver_response(g,blob,OUT);g['materials'][silver]['name']='GAMECUBE_SILVER_DATA_UNDERSIDE'
dark=material('GAMECUBE_DARK_FACE_SUBSTRATE',[.008,.009,.01,1],.4,.18,{'KHR_materials_clearcoat':{'clearcoatFactor':.7,'clearcoatRoughnessFactor':.06}})
clear=material('GAMECUBE_CLEAR_POLYCARBONATE',[.96,.97,.98,1],0,.08,{'KHR_materials_transmission':{'transmissionFactor':.94},'KHR_materials_ior':{'ior':1.58}})
# Match the established PS2 / original Xbox / Xbox 360 clear centre exactly.
g['materials'][clear].update(alphaMode='BLEND',pbrMetallicRoughness={'baseColorFactor':[.92,.95,1,.22],'metallicFactor':0,'roughnessFactor':.06},extensions={'KHR_materials_transmission':{'transmissionFactor':.95},'KHR_materials_ior':{'ior':1.58},'KHR_materials_clearcoat':{'clearcoatFactor':1}})
etch=material('GAMECUBE_SECURITY_ETCH',[.19,.20,.21,1],.8,.24)
foil=material('GAMECUBE_POLISHED_HUB',[.68,.68,.68,1],1,.09)
security=material('GAMECUBE_SILVER_SECURITY_BACKING',[.68,.68,.68,1],1,.095,{'KHR_materials_clearcoat':{'clearcoatFactor':.12,'clearcoatRoughnessFactor':.07}})
art=material('TOP_ART_REPLACE_THIS_TEXTURE',[1,1,1,0],0,.36);g['materials'][art]['alphaMode']='MASK';g['materials'][art]['alphaCutoff']=.35
def surface(name,profile,mat,start=0,end=360,mirror_u=False):
 p=[];n=[];uv=[];t=[];N=max(2,math.ceil((end-start)/360*1024))
 for (ra,ya),(rb,yb) in zip(profile,profile[1:]):
  dr=rb-ra;dy=yb-ya;length=math.hypot(dr,dy)
  for i in range(N):
   for r,y,k in [(ra,ya,i),(rb,yb,i),(rb,yb,i+1),(ra,ya,i),(rb,yb,i+1),(ra,ya,i+1)]:
    a=math.radians(start+(end-start)*k/N);c=math.cos(a);s=math.sin(a)
    p.append((r*c/1000,y/1000,r*s/1000));n.append((dy/length*c,-dr/length,dy/length*s));uv.append((.5+(1 if mirror_u else -1)*r*c/80,.5-r*s/80));t.append((-s,0,c,1))
 attrs={key:acc(data,typ) for key,data,typ in [('POSITION',p,'VEC3'),('NORMAL',n,'VEC3'),('TEXCOORD_0',uv,'VEC2'),('TANGENT',t,'VEC4')]}
 g['meshes'].append({'name':name,'primitives':[{'attributes':attrs,'material':mat}]});g['nodes'].append({'name':name,'mesh':len(g['meshes'])-1});g['scenes'][0]['nodes'].append(len(g['nodes'])-1)
surface('Silver_read_side',[(22.12,-.6),(39.15,-.6)],silver)
surface('Polished_silver_security_read_side',[(11.5,-.6),(22.12,-.6)],security)
surface('Silver_beneath_clear_face',[(39.15,.56),(11.5,.56)],silver)
surface('Clear_face_layer',[(39.15,.6),(11.5,.6)],clear)
surface('Black_front_security_ring',[(22.12,.70),(11.5,.70)],dark)
surface('Thin_black_outer_face_ring',[(39.15,.615),(38.90,.615)],dark)
surface('Clear_outer_bevel',[(39.15,-.6),(39.9,-.6),(40,-.5),(40,.5),(39.9,.6),(39.15,.6)],clear)
def hub_top(r):
 return .66+.17*math.exp(-((r-10.85)/.36)**2)+.07*math.exp(-((r-7.8)/.18)**2)-.06*math.exp(-((r-11.5)/.12)**2)
hub_radii=np.linspace(11.5,7.6,120)
surface('Raised_rounded_clear_hub_collar',[(float(r),hub_top(r)) for r in hub_radii]+[(7.5,.5),(7.5,-.5),(7.6,-.6),(11.5,-.6)],clear)
surface('Artwork_layer',[(39.15,.92),(11.5,.92)],art)
# Reference-derived moulded shoulders; relief is deliberately modest.
for side in [-1,1]:
 for r,w,h in ([(8.15,.12,.025),(9.7,.18,.035),(11.4,.16,.04)] if side<0 else []):
  profile=[(r-w,.6*side),(r-w*.5,(.6+h)*side),(r+w*.5,(.6+h)*side),(r+w,.6*side)]
  if side>0:profile.reverse()
  if side>0 and r>11.6:profile=[(rr,yy+.10) for rr,yy in profile]
  surface(f'Hub_ridge_{side}_{r}',profile,clear if r<11.6 else foil)
# One fine security groove, rather than two bright metallic raised rings.
groove=material('GAMECUBE_SINGLE_SECURITY_GROOVE',[.22,.23,.24,1],.35,.23)
surface('Single_fine_front_security_circle',[(17.78,.712),(17.75,.712)],groove)
surface('Single_fine_back_security_circle',[(17.75,-.612),(17.78,-.612)],groove)
# Representative mastering bars, not a decoded/authenticated security sequence.
# Irregular short/medium/wide runs and uneven gaps, reconstructed visually.
# This describes the appearance, not the original encoded security data.
widths=[.19,.22,.61,.21,.38,.18,.78,.25,.20,.47,.30,.16,.23,.66,.33,.21,.43,.18,.72,.26,.20,.36,.57,.19,.24,.45,.17,.69,.22,.31,.20,.51,.27,.18,.75,.34,.21]
gaps=[.23,.17,.31,.19,.24,.18,.29,.22,.16,.26,.21,.35,.18,.24,.20,.28,.17,.22,.32]
from gamecube_security_pattern import security_bars
barspec=security_bars()
for side in [-1,1]:
 for a,b in barspec:
  depth=.72 if side>0 else -.615
  profile=[(21.0,depth),(22.05,depth)]
  if side>0:profile.reverse()
  surface(f'Security_bar_{side}_{a:.2f}',profile,silver,float(a),float(b))

# Outlined OCR lettering and a separate full-circle micro-striation band.
# Both are physical substrate details, independent of the uploaded artwork.
parts=[];fineparts=[];finespec=[];cursor=0.;i=0
while cursor<360:
 width=[.035,.055,.11,.045,.08,.16,.04,.065,.12,.05,.09,.035,.14][i%13]
 gap=[.07,.14,.06,.18,.09,.045,.23,.08,.12,.055,.16][(i*7+i//13)%11]
 finespec.append((cursor,min(cursor+width,360)));cursor+=width+gap;i+=1
for a,b in finespec:
 def xy(r,angle):return r*math.cos(math.radians(angle)),r*math.sin(math.radians(angle))
 points=[xy(r,t) for r,t in [(22.12,a),(22.75,a),(22.75,b),(22.12,b)]]
 fineparts.append('<path fill="rgb(255,34,255)" d="M'+' L'.join(f'{-x:.5f},{-y:.5f}' for x,y in points)+' Z"/>')
labels=[('DOL-GSSE-0-00 USA S0',260,.72),('IFPI LL08',225,.57),('C04K1402',290,.63),('M1S1',325,.55)]
for text,angle,size in labels:
 paths=text_paths('C:/Windows/Fonts/OCRAEXT.TTF',text,size);x0,y0,x1,y1=bounds(paths);commands=[]
 for outline in paths:
  points=[]
  for x,y in outline:
   a=math.radians(angle)+(x-(x0+x1)/2)/20.5;r=20.5+y-(y0+y1)/2
   points.append((-r*math.cos(a),-r*math.sin(a)))
  commands.append('M'+' L'.join(f'{x:.5f},{y:.5f}' for x,y in points)+' Z')
 parts.append('<path fill="#bcbcbc" fill-rule="evenodd" d="'+' '.join(commands)+'"/>')
svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="-40 -40 80 80">'+''.join(parts)+'</svg>'
source=OUT/'branding-source/gamecube-mastering-details.svg';source.write_text(svg,encoding='utf-8')
env=os.environ.copy();env['NODE_PATH']='C:/Users/dimit/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules'
subprocess.run(['node','-e',"require('sharp')('outputs/branding-source/gamecube-mastering-details.svg').resize(8192,8192).png().toFile('outputs/gamecube-mastering-details.png').catch(e=>{console.error(e);process.exit(1)})"],cwd=OUT.parent,env=env,check=True)
g['images'].append({'bufferView':view((OUT/'gamecube-mastering-details.png').read_bytes()),'mimeType':'image/png','name':'GameCube outlined mastering details'})
g['textures'].append({'source':len(g['images'])-1,'sampler':0});detailTexture=len(g['textures'])-1
details=copy.deepcopy(g['materials'][security]);details['name']='GAMECUBE_SILVER_MASTERING_LETTERING';details['alphaMode']='BLEND';details['pbrMetallicRoughness']['baseColorTexture']={'index':detailTexture};g['materials'].append(details);detailMat=len(g['materials'])-1
for side in [-1,1]:
 depth=.75 if side>0 else -.63
 profile=[(19.8,depth),(22.8,depth)]
 if side>0:profile.reverse()
 if side>0:
  frontDetails=copy.deepcopy(details);frontDetails['name']='GAMECUBE_SECURITY_LETTERING_AND_FAINT_EDGE';frontDetails['pbrMetallicRoughness']['baseColorFactor']=[.3,.3,.3,1];frontDetails['extensions'].pop('KHR_materials_iridescence',None);g['materials'].append(frontDetails)
 surface(f'Continuous_fine_ring_and_lettering_{side}',profile,len(g['materials'])-1 if side>0 else detailMat,mirror_u=side>0)

# Fine etchings change the reflection's roughness, not the painted colour.
# Their low contrast is revealed only when a highlight crosses this band.
fineSVG='<svg xmlns="http://www.w3.org/2000/svg" viewBox="-40 -40 80 80"><rect x="-40" y="-40" width="80" height="80" fill="rgb(255,28,255)"/>'+''.join(fineparts)+'</svg>'
(OUT/'branding-source/gamecube-fine-etch-roughness.svg').write_text(fineSVG,encoding='utf-8')
subprocess.run(['node','-e',"require('sharp')('outputs/branding-source/gamecube-fine-etch-roughness.svg').resize(8192,8192).png().toFile('outputs/gamecube-fine-etch-roughness.png').catch(e=>{console.error(e);process.exit(1)})"],cwd=OUT.parent,env=env,check=True)
g['images'].append({'bufferView':view((OUT/'gamecube-fine-etch-roughness.png').read_bytes()),'mimeType':'image/png','name':'Subtle variable-width etch roughness'})
g['textures'].append({'source':len(g['images'])-1,'sampler':0})
micro=copy.deepcopy(g['materials'][silver]);micro['name']='GAMECUBE_ANGLE_DEPENDENT_FINE_ETCH';micro['pbrMetallicRoughness']['roughnessFactor']=1;micro['pbrMetallicRoughness']['metallicRoughnessTexture']={'index':len(g['textures'])-1};g['materials'].append(micro);microMat=len(g['materials'])-1
for side in [-1,1]:
 depth=.76 if side>0 else -.635
 profile=[(22.12,depth),(22.75,depth)]
 if side>0:profile.reverse()
 surface(f'Faint_variable_outer_etch_{side}',profile,microMat)
g['extras']={'previewOnly':True,'diameterMm':80,'nominalBodyThicknessMm':1.2,'centreHoleMm':15,'hubAndMasteringRadii':'Estimated from supplied photographs; requires review','securitySequence':'Representative, not decoded','fineRing':{'innerRadiusMm':22.12,'outerRadiusMm':22.75,'marks':len(finespec),'coverageDegrees':360,'appearance':'Roughness only, variable widths and gaps'},'lettering':[x[0] for x in labels],'letteringNote':'Transcribed from photos; small suffixes require confirmation','source':'Nintendo 8 cm specification; ECMA-267/268 nominal optical disc geometry'}
from gamecube_hub_codes import add_hub_codes
add_hub_codes(g,acc,clear)
while len(blob)%4:blob.append(0)
g['buffers'][0]['byteLength']=len(blob);j=json.dumps(g,separators=(',',':')).encode();j+=b' '*((-len(j))%4)
(OUT/'previews/gamecube-disc-preview.glb').write_bytes(struct.pack('<III',0x46546c67,2,28+len(j)+len(blob))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(blob),0x004e4942)+blob)

# Diagrammatic material preview: generated directly from construction geometry.
W,H=1700,1080;img=Image.new('RGB',(W,H),'#eceee9');d=ImageDraw.Draw(img)
font=lambda n,b=False:ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf' if b else 'segoeui.ttf'),n)
d.text((45,28),'GAMECUBE — CONSTRUCTION PREVIEW',font=font(29,True),fill='#283129')
d.text((45,76),'Preview only · Studio unchanged · Material and proportion study',font=font(19),fill='#667366')
for cx,front,title in [(430,True,'Clear face · dark security markings'),(1270,False,'Read side · silver')]:
 d.text((cx,145),title,font=font(24,True),fill='#283129',anchor='mm')
 S=740;y,x=np.mgrid[0:S,0:S];x=(x+.5-S/2)*80/S;y=(y+.5-S/2)*80/S;r=np.hypot(x,y);a=np.arctan2(y,x)
 highlight=np.exp(-((np.sin(a-.55))/.17)**2)
 base=.52
 val=np.clip(base+highlight*(.10 if front else .4),0,1)
 rgb=np.repeat(val[...,None],3,axis=2)
 if not front:rgb[(r>=11.5)&(r<=22.12)]=np.repeat((.61+.31*highlight[(r>=11.5)&(r<=22.12)])[...,None],3,axis=1)
 if front:rgb[(r>=11.5)&(r<=22.12)]=.035
 if not front:
  rainbow=np.exp(-((np.sin(a-2.15))/.17)**2)*.10
  for c in range(3):rgb[:,:,c]+=rainbow*np.sin(r*.12+c*2.1)*(r>22.12)
 rgb+=np.exp(-((r-17.765)/.035)**2)[...,None]*(.035+highlight[...,None]*.025)
 hub=r<11.5;rgb[hub]=np.stack([.53+.1*highlight[hub]]*3,axis=1)
 for rr in [7.8,10.85]:rgb+=np.exp(-((r-rr)/.18)**2)[...,None]*(.035+.22*highlight[...,None])
 degrees=np.mod(np.degrees(a),360)
 ring=(r>21.0)&(r<22.05)&(degrees>15)&(degrees<201)
 bars=np.zeros_like(r,dtype=bool)
 for a0,a1 in barspec:bars|=ring&(degrees>=a0)&(degrees<a1)
 rgb[bars]=.19 if front else .38
 fine=(r>22.12)&(r<22.75)
 ticks=np.zeros_like(r,dtype=bool)
 for a0,a1 in finespec:ticks|=fine&(degrees>=a0)&(degrees<a1)
 rgb[ticks]*=(1-.012*highlight[ticks,None])
 rgb[r<7.5]=[.28,.33,.37];rgb[(r>38.90)&(r<39.15)]=.025;rgb[r>39.15]=[.62,.66,.66];rgb[r>40]=np.array([236,238,233])/255
 tile=Image.fromarray(np.uint8(np.clip(rgb,0,1)*255))
 # Same vector lettering as the model texture; rendered without the image's UV rotation.
 overlay=Image.open(OUT/'gamecube-mastering-details.png').convert('RGBA').rotate(180).resize((S,S),Image.Resampling.LANCZOS)
 tile=tile.convert('RGBA');tile.alpha_composite(overlay);img.paste(tile.convert('RGB'),(cx-S//2,180))
 d.text((cx,940),'80 mm diameter · 15 mm centre hole · 1.2 mm nominal body',font=font(18),fill='#52604f',anchor='mm')
d.text((850,990),'Hub profiles and security band estimated from photos · Barcode sequence representative',font=font(18),fill='#667366',anchor='mm')
d.text((850,1026),'Clear face over silver · Black lower panel belongs to artwork · Irregular security bars beneath the print',font=font(18),fill='#667366',anchor='mm')
img.save(OUT/'previews/gamecube-construction-preview.png')
(OUT/'previews/gamecube-preview-notes.txt').write_text(json.dumps(g['extras'],indent=2)+'\nNot integrated into the studio. Face/read materials are separate; artwork is a separate alpha layer. No Animal Crossing artwork or Nintendo logo is baked into this model.\n',encoding='utf-8')
positions=[np.array(a['min']) for a in g['accessors'] if a['type']=='VEC3']
assert g['extras']['diameterMm']==80
print('Built separate GameCube GLB and construction preview; studio unchanged.')
