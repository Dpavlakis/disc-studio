"""Original Xbox branding on the approved disc construction and foil finish."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageChops
import numpy as np,json,struct,math,hashlib
root=Path(__file__).resolve().parents[1];out=root/'outputs'
source=out/'xbox360-test.glb';raw=source.read_bytes();digest=hashlib.sha256(raw).hexdigest()
jn=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+jn]);bn=struct.unpack_from('<I',raw,20+jn)[0];blob=bytearray(raw[28+jn:28+jn+bn])
S=4096;N=4096;UV_SPAN=.034;C=S/2;scale=S/UV_SPAN
mask=Image.new('L',(S,S));front_mask=Image.new('L',(S,S));contours=Image.new('L',(S,S))
def stamp(tile,angle,r=.0137,target=None):
 target=mask if target is None else target
 tile=tile.rotate(-angle,resample=Image.Resampling.BICUBIC,expand=True)
 a=math.radians(angle);x=C+math.sin(a)*r*scale;y=C-math.cos(a)*r*scale
 target.paste(tile,(round(x-tile.width/2),round(y-tile.height/2)),tile)
def polar_stamp(tile,center,arc_width,radial_height,target=None):
 if target is None:
  # Counter-reflect each local mark before the front's panel-layout reflection.
  # This swaps the panel positions without reversing letters in either panel.
  polar_stamp(tile.transpose(Image.Transpose.FLIP_LEFT_RIGHT),center,arc_width,radial_height,target=front_mask)
 target=mask if target is None else target
 theta=math.radians(center);rc=.0137
 extent=math.ceil((radial_height/2+math.radians(arc_width)*(rc+radial_height/2)/2)*scale)+12
 cx=C+math.sin(theta)*rc*scale;cy=C-math.cos(theta)*rc*scale
 left=max(0,int(cx-extent));top=max(0,int(cy-extent));right=min(S,int(cx+extent));bottom=min(S,int(cy+extent))
 yy0,xx0=np.mgrid[top:bottom,left:right].astype(np.float32);xx0=(xx0+.5-C)/scale;yy0=(yy0+.5-C)/scale
 radius=np.hypot(xx0,yy0);delta=(np.arctan2(xx0,-yy0)-theta+math.pi)%math.tau-math.pi
 u=(delta/math.radians(arc_width)+.5)*(tile.width-1);v=((rc+radial_height/2-radius)/radial_height)*(tile.height-1)
 valid=(u>=0)&(u<tile.width-1)&(v>=0)&(v<tile.height-1)
 u=np.clip(u,0,tile.width-1.001);v=np.clip(v,0,tile.height-1.001);ix=u.astype(int);iy=v.astype(int);fx=u-ix;fy=v-iy
 pixels=np.asarray(tile,dtype=np.float32)
 sampled=(pixels[iy,ix]*(1-fx)*(1-fy)+pixels[iy,ix+1]*fx*(1-fy)+pixels[iy+1,ix]*(1-fx)*fy+pixels[iy+1,ix+1]*fx*fy)*valid
 old=np.asarray(target.crop((left,top,right,bottom)));target.paste(Image.fromarray(np.uint8(np.maximum(old,sampled))),(left,top))
symbol=Image.open(root/'work/xbox-original-symbol.png').getchannel('A');symbol=symbol.crop(symbol.getbbox())
foil_font=ImageFont.truetype(str(out/'branding-source/XboxOriginalBold.ttf'),160)
bounds=foil_font.getbbox('XBOX');word=Image.new('L',(bounds[2]-bounds[0]+12,bounds[3]-bounds[1]+12))
ImageDraw.Draw(word).text((6-bounds[0],6-bounds[1]),'XBOX',font=foil_font,fill=255)
word_arc=30
# Equal physical scale along the arc and radius preserves the font's native
# proportions. Previously the two axes were fitted independently.
word_height=.0137*math.radians(word_arc)*word.height/word.width
# Four symbols and three wordmarks occupy each arc between the side panels.
# The end symbols stop before the +/-20 degree panel boundaries.
symbol_centers=[-55,-18.333,18.333,55,125,161.667,198.333,235]
word_centers=[-36.667,0,36.667,90,143.333,180,216.667]
for center in word_centers:polar_stamp(word,center,word_arc,word_height)
for symbol_center in symbol_centers:
 polar_stamp(symbol,symbol_center,20,.0047)
 for expansion in (1.12,1.28,1.44,1.60,1.76,1.92):
  tile=symbol.resize((300,300),Image.Resampling.LANCZOS)
  outline=ImageChops.subtract(tile.filter(ImageFilter.MaxFilter(5)),tile.filter(ImageFilter.MinFilter(5)))
  polar_stamp(outline,symbol_center,20*expansion,.0047*expansion,target=contours)
# Left checkerboard panel: seven alternating lines; no disc-specific code.
panel=Image.new('L',(210,420));d=ImageDraw.Draw(panel)
font=ImageFont.truetype(str(out/'branding-source/XboxOriginalBold.ttf'),47)
genuine_font=ImageFont.truetype('C:/Windows/Fonts/georgiaz.ttf',49)
panel_lines=['XBOX','genuine','XBOX','genuine','XBOX','genuine','XBOX']
for i,line in enumerate(panel_lines):
 row_font=font if line=='XBOX' else genuine_font
 box=row_font.getbbox(line)
 # Center the visible ink rather than the font's differing ascender metrics.
 # Both word styles occupy about 98% of the panel's radial width.
 x=105-(box[0]+box[2])/2;y=32+i*59-(box[1]+box[3])/2
 d.text((x,y),line,font=row_font,fill=255,stroke_width=1 if line=='genuine' else 0)
 assert .965*panel.width<=box[2]-box[0]<=.995*panel.width
polar_stamp(panel.rotate(90,expand=True),270,38,.005)
from original_xbox_vectors import build_vectors
build_vectors()
mask=Image.open(root/'work/xbox-vector-rear.png').convert('L')
front_mask=Image.open(root/'work/xbox-vector-front.png').convert('L')
contours=Image.open(root/'work/xbox-vector-contours.png').convert('L')
# Expand the approved subtle gray levels into a usable surface-finish range.
pattern_values=np.asarray(contours,dtype=np.float32)/255
pattern_values=np.clip((pattern_values-140/255)/(50/255),0,1)
a=np.asarray(mask,dtype=np.float32)/255
yy,xx=np.mgrid[:N,:N].astype(np.float32);xx-=N/2;yy-=N/2;r=np.hypot(xx,yy)*UV_SPAN/N;angle=np.arctan2(xx,-yy)
annulus=(r>.0112)&(r<.0162)
degrees=np.degrees(angle)
checker_sections=(np.abs((degrees-90+180)%360-180)<20)|(np.abs((degrees-270+180)%360-180)<20)
background=annulus*(1-a)
checker_grid=((np.floor((degrees+20)/(40/6))+np.floor((r-.0112)/(.005/3)))%2)*checker_sections*annulus
checker=checker_grid*(1-a)
x_pattern=pattern_values*(~checker_sections)*background
# Broad alternating bands grow directly from each X silhouette.
microdetail=checker+x_pattern
# Keep the background inside the restrained finish range of the 360 swirls.
# Main marks retain their stronger finish difference and crisp relief edges.
PATTERN_VISIBILITY=1.02
CHECKER_FINISH=.014*PATTERN_VISIBILITY;BAND_FINISH=.018*PATTERN_VISIBILITY;BACKGROUND_RELIEF=.035*PATTERN_VISIBILITY
def finish_map(glyphs,checks,bands):
 return .055+.18*glyphs+CHECKER_FINISH*checks+BAND_FINISH*bands
mr=np.full((N,N,3),255,dtype=np.uint8);mr[:,:,1]=np.uint8(np.clip(finish_map(a,checker,x_pattern),0,1)*255)
mrpath=out/'xbox-original-metal-roughness.png';Image.fromarray(mr).save(mrpath,optimize=True)
gy,gx=np.gradient(a);py,px=np.gradient(microdetail)
n=np.stack([gx*.3+px*BACKGROUND_RELIEF,-gy*.3-py*BACKGROUND_RELIEF,np.ones_like(gx)],axis=-1);n/=np.linalg.norm(n,axis=-1)[...,None]
normalpath=out/'xbox-original-security-normal.png';Image.fromarray(np.uint8(np.clip(n*.5+.5,0,1)*255)).save(normalpath,optimize=True)
preview=Image.fromarray(np.uint8(np.clip(215-a*85-microdetail*8*PATTERN_VISIBILITY,0,255))).convert('RGB');preview.crop((100,100,N-100,N-100)).resize((1100,1100)).save(out/'previews/xbox-original-hub-preview.png')
# Front lettering gets its own maps; the rear retains its own reading direction.
fa=np.asarray(front_mask.resize((N,N),Image.Resampling.LANCZOS),dtype=np.float32)/255
front_checker=checker_grid*(1-fa)
front_pattern=pattern_values*(~checker_sections)*annulus*(1-fa)
front_detail=front_checker+front_pattern
front_mr=mr.copy();front_mr[:,:,1]=np.uint8(np.clip(finish_map(fa,front_checker,front_pattern),0,1)*255)
front_mrpath=out/'xbox-original-front-metal-roughness.png';Image.fromarray(front_mr).save(front_mrpath,optimize=True)
gy,gx=np.gradient(fa);py,px=np.gradient(front_detail)
fn=np.stack([gx*.3+px*BACKGROUND_RELIEF,-gy*.3-py*BACKGROUND_RELIEF,np.ones_like(gx)],axis=-1);fn/=np.linalg.norm(fn,axis=-1)[...,None]
front_normalpath=out/'xbox-original-front-security-normal.png';Image.fromarray(np.uint8(np.clip(fn*.5+.5,0,1)*255)).save(front_normalpath,optimize=True)
front_preview=Image.fromarray(np.uint8(np.clip(215-fa*85-front_detail*8*PATTERN_VISIBILITY,0,255))).transpose(Image.Transpose.FLIP_LEFT_RIGHT)
front_preview.crop((100,100,N-100,N-100)).resize((1100,1100)).save(out/'previews/xbox-original-front-hub-preview.png')
assert np.count_nonzero(checker)>1000 and np.count_nonzero(x_pattern)>1000
assert len(symbol_centers)==8 and len(word_centers)==7
for center in symbol_centers:
 for panel_center in (90,270):
  assert abs((center-panel_center+180)%360-180)-10>=20
# The glyph and panel maps use equal arc/radial scale (no independent stretch).
assert abs(word_height/(.0137*math.radians(word_arc))-word.height/word.width)<1e-9
art=Image.new('RGB',(2048,2048),'#e9e7df');d=ImageDraw.Draw(art)
title=ImageFont.truetype(str(out/'branding-source/XboxOriginalBold.ttf'),105)
d.text((1024,490),'XBOX',font=title,fill='#5c8c32',anchor='mm')
d.text((1024,1500),'YOUR ORIGINAL XBOX ART',font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',48),fill='#293a26',anchor='mm')
artpath=out/'xbox-original-label-art.png';art.save(artpath)
def texture(path):
 while len(blob)%4:blob.append(0)
 data=path.read_bytes();g['bufferViews'].append({'buffer':0,'byteOffset':len(blob),'byteLength':len(data)});blob.extend(data)
 g['images'].append({'bufferView':len(g['bufferViews'])-1,'mimeType':'image/png','name':path.name});g['textures'].append({'source':len(g['images'])-1,'sampler':0});return len(g['textures'])-1
mi=texture(mrpath);ni=texture(normalpath);ai=texture(artpath)
g['materials'][0]['pbrMetallicRoughness']['baseColorTexture']={'index':ai}
g['materials'][3]['pbrMetallicRoughness']['metallicRoughnessTexture']={'index':mi}
g['materials'][3]['normalTexture']={'index':ni,'scale':.8}
front_material=json.loads(json.dumps(g['materials'][3]))
front_material['name']='ORIGINAL_XBOX_FRONT_READABLE_SECURITY_FOIL'
front_material['pbrMetallicRoughness']['metallicRoughnessTexture']={'index':texture(front_mrpath)}
front_material['normalTexture']={'index':texture(front_normalpath),'scale':.8}
g['materials'].append(front_material);front_material_index=len(g['materials'])-1
# Mirror the front security ring only. The reverse keeps its original mapping.
def mirrored_attribute(index,width,reflect=True):
 accessor=g['accessors'][index];view=g['bufferViews'][accessor['bufferView']]
 assert accessor['componentType']==5126 and not view.get('byteStride')
 offset=view.get('byteOffset',0)+accessor.get('byteOffset',0)
 values=np.frombuffer(blob,dtype='<f4',count=accessor['count']*width,offset=offset).copy().reshape(-1,width)
 if width==2:
  if reflect:values[:,0]=1-values[:,0]
  values[:,:]=.5+(values[:,:]-.5)*(.12/UV_SPAN)
 else:values[:,:3]*=-1;values[:,3]*=-1
 while len(blob)%4:blob.append(0)
 payload=values.astype('<f4').tobytes()
 g['bufferViews'].append({'buffer':0,'byteOffset':len(blob),'byteLength':len(payload)});blob.extend(payload)
 copied=dict(accessor,bufferView=len(g['bufferViews'])-1,byteOffset=0)
 copied.pop('min',None);copied.pop('max',None)
 g['accessors'].append(copied)
 return len(g['accessors'])-1
front_count=0
for mesh in g['meshes']:
 if mesh['name']=='06_Xbox360_Holographic_Center':
  for primitive in mesh['primitives']:
   primitive['material']=front_material_index
   attrs=primitive['attributes']
   attrs['TEXCOORD_0']=mirrored_attribute(attrs['TEXCOORD_0'],2)
   attrs['TANGENT']=mirrored_attribute(attrs['TANGENT'],4)
  front_count+=1
assert front_count==1
for mesh in g['meshes']:
 if mesh['name']=='09_Xbox360_Reverse_Holographic_Center':
  for primitive in mesh['primitives']:
   attrs=primitive['attributes'];attrs['TEXCOORD_0']=mirrored_attribute(attrs['TEXCOORD_0'],2,False)
# Remove Xbox 360-specific pressing codes from the active scene, then compact
# the mesh/node lists so no unsupported inscription appears on this model.
drop=('Raised_IFPI','Mastering_Inscriptions')
oldnodes=g['nodes'];oldmeshes=g['meshes'];g['nodes']=[];g['meshes']=[]
for old in oldnodes:
 if any(t in old.get('name','') for t in drop):continue
 mesh=oldmeshes[old['mesh']];mesh['name']=mesh['name'].replace('Xbox360','Original_Xbox')
 old['name']=mesh['name'];old['mesh']=len(g['meshes']);g['meshes'].append(mesh);g['nodes'].append(old)
g['scenes'][0]['nodes']=list(range(len(g['nodes'])))
for m in g['materials']:
 if m['name']!='TOP_ART_REPLACE_THIS_TEXTURE':m['name']=m['name'].replace('XBOX360','ORIGINAL_XBOX')
g['asset']['generator']='Original Xbox disc: supplied vector marks, approved constant-distance X bands, dedicated 4K foil maps'
g['buffers'][0]['byteLength']=len(blob);js=json.dumps(g,separators=(',',':')).encode();js+=b' '*((-len(js))%4);blob+=b'\0'*((-len(blob))%4)
data=struct.pack('<III',0x46546c67,2,28+len(js)+len(blob))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(blob),0x004e4942)+blob
(out/'xbox-original-disc.glb').write_bytes(data)
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
print('Original Xbox created:',len(g['meshes']),'parts; Xbox 360 source unchanged')
