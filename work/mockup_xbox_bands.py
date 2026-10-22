"""Standalone review mockup; never modifies the disc or its studio."""
from pathlib import Path
import math,copy,xml.etree.ElementTree as ET,os,subprocess,hashlib
from PIL import Image,ImageDraw,ImageFont
from original_xbox_vectors import silhouette_paths,curved
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs'
before={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in [OUT/'xbox-original-disc.glb',OUT/'studio.html']}
symbol=silhouette_paths()
source=ET.parse(OUT/'branding-source/xbox-original-security-front.svg').getroot()
main=list(source)[0];defs=next(e for e in main if e.tag.endswith('defs'))
marks=[];checks=[];after_pattern=False
for e in main:
 if e.tag.endswith('g') and e.get('clip-path'):
  after_pattern=True;continue
 if e.tag.endswith('defs'):continue
 item=copy.deepcopy(e)
 if after_pattern:
  for child in item.iter():
   if child.get('fill')=='white':child.set('fill','#d0d1c8' if item.get('data-wordmark') else '#656961')
   if child.get('stroke')=='#999':child.set('stroke','#92968a')
   if child.get('stroke')=='black':child.set('stroke','#4b5048')
  marks.append(ET.tostring(item,encoding='unicode'))
 else:
  item.set('fill','#969b90');checks.append(ET.tostring(item,encoding='unicode'))

# Filled, nested X silhouettes replace separate crossing contour strokes.
# Draw all Xs at each level before stepping inward; adjacent fields share a
# single shade at a given expansion and continue to the band boundaries.
scales=[5.0,4.2,3.5,2.95,2.5,2.13,1.84,1.59,1.38,1.19,1.0]
shades=['#a9aca2','#92978b','#b0b3a8','#999e92','#b5b8ac','#9ca195','#babdaf','#a0a598','#bdc0b3','#a3a89b','#656961']
fields=[]
for scale,shade in zip(scales,shades):
 paths=[]
 for center in [-55,-18.333,18.333,55,125,161.667,198.333,235]:
  paths.append(f'<path d="{curved(symbol,center,20*scale,.0047*scale)}" fill="{shade}"/>')
 fields.append('<g>'+''.join(paths)+'</g>')
head='<svg xmlns="http://www.w3.org/2000/svg" width="3000" height="3000" viewBox="-17 -17 34 34">'
annulus='<path d="M 16.2 0 A 16.2 16.2 0 1 0 -16.2 0 A 16.2 16.2 0 1 0 16.2 0 Z M 11.2 0 A 11.2 11.2 0 1 1 -11.2 0 A 11.2 11.2 0 1 1 11.2 0 Z" fill="#acafa4" fill-rule="evenodd"/>'
body=annulus+ET.tostring(defs,encoding='unicode')+''.join(checks)+'<g clip-path="url(#pattern-band)">'+''.join(fields)+'</g>'+''.join(marks)
svg=head+'<g transform="scale(-1,1)">'+body+'</g></svg>'
target=OUT/'previews/xbox-security-band-mockup.svg';target.write_text(svg,encoding='utf-8')
env=os.environ.copy();env['NODE_PATH']='C:/Users/dimit/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules'
subprocess.run(['node','-e',"const sharp=require('sharp');sharp('outputs/xbox-security-band-mockup.svg').png().toFile('work/xbox-band-mockup-render.png')"],cwd=ROOT,env=env,check=True)
ring=Image.open(ROOT/'work/xbox-band-mockup-render.png').convert('RGBA')
canvas=Image.new('RGB',(1800,1120),'#f5f3e9');d=ImageDraw.Draw(canvas)
title=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',35)
small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24)
d.text((55,35),'EXPANDING X BANDS — MOCKUP',font=title,fill='#30372f')
d.text((55,88),'Continuous filled bands · alternating shades · clipped cleanly at the side panels',font=small,fill='#687061')
full=ring.resize((900,900),Image.Resampling.LANCZOS);canvas.paste(full,(10,170),full)
d.text((68,160),'FULL RING',font=small,fill='#687061')
# Show three adjoining X fields on the top arc at a larger scale.
detail=ring.crop((450,0,2570,900));detail.thumbnail((850,650),Image.Resampling.LANCZOS)
canvas.paste(detail,(925,345),detail)
d.text((965,235),'ENLARGED PATTERN',font=small,fill='#687061')
d.text((965,760),'Each band grows from the same X silhouette.',font=small,fill='#434c3d')
d.text((965,802),'The shades fill the space between the marks.',font=small,fill='#434c3d')
d.text((965,844),'No separate diamond lines or open gaps.',font=small,fill='#434c3d')
d.text((55,1070),'Pattern study only — the current disc model has not been changed.',font=small,fill='#687061')
canvas.save(OUT/'previews/xbox-security-band-mockup.png')
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==digest for p,digest in before.items())
print('Mockup saved. Current GLB and studio hashes unchanged.')
