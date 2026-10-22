"""Standalone review mockup; never modifies the disc or its studio."""
from pathlib import Path
import math,copy,xml.etree.ElementTree as ET,os,subprocess,hashlib
from PIL import Image,ImageDraw,ImageFont
from original_xbox_vectors import silhouette_paths,curved
from shapely.geometry import Polygon
from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs'
before={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in [OUT/'xbox-original-disc.glb',OUT/'studio.html']}
symbol=silhouette_paths()
source=ET.parse(OUT/'branding-source/xbox-original-security-front.svg').getroot()
main=list(source)[0];defs=next(e for e in main if e.tag.endswith('defs'))
marks=[];checks=[];after_pattern=False;x_count=0
for e in main:
 if e.tag.endswith('g') and e.get('clip-path'):
  after_pattern=True;continue
 if e.tag.endswith('defs'):continue
 item=copy.deepcopy(e)
 if after_pattern:
  is_symbol=item.tag.endswith('path') and x_count<8
  if is_symbol:x_count+=1
  for child in item.iter():
   if child.get('fill')=='white':child.set('fill','#d0d1c8' if item.get('data-wordmark') else '#656961')
   if child.get('stroke')=='#999':child.set('stroke','#92968a')
   if child.get('stroke')=='black':child.set('stroke','#4b5048')
  mark=ET.tostring(item,encoding='unicode')
  marks.append('<g mask="url(#x-core-weight)">'+mark+'</g>' if is_symbol else mark)
 else:
  item.set('fill','#969b90');checks.append(ET.tostring(item,encoding='unicode'))

# Constant-distance polygon offsets: each edge moves by the same amount.
# Buffer in the flat physical ring coordinates, then bend onto the disc.
w=.0137*math.radians(20)*1000;h=4.7
pieces=[]
for path in symbol:
 polygon=Polygon([((u-.5)*w,(v-.5)*h) for u,v in path]).buffer(0)
 if polygon.area>.1:pieces.append(polygon)
seed=unary_union(pieces).simplify(.01,preserve_topology=True)
fields=[]
for level in range(30,-1,-1):
 distance=level*.18
 grown=seed.buffer(distance,join_style='mitre',mitre_limit=5) if level else seed
 geometries=list(grown.geoms) if grown.geom_type=='MultiPolygon' else [grown]
 outlines=[]
 for polygon in geometries:
  for boundary in [polygon.exterior,*polygon.interiors]:
   outlines.append([(.5+x/w,.5+y/h) for x,y in boundary.coords])
 value=round(166+10*math.cos(level*math.pi)+5*math.sin(level*.72)) if level else 101
 shade='#'+f'{value:02x}'*3
 paths=[]
 for center in [-55,-18.333,18.333,55,125,161.667,198.333,235]:
  paths.append(f'<path d="{curved(outlines,center,20,.0047)}" fill="{shade}" fill-rule="evenodd"/>')
 fields.append('<g>'+''.join(paths)+'</g>')
# Continue the same parallel edges through the upper X tips. This strip
# is a darker continuation of the X, so the main core remains recognizable.
upper=[]
for step in range(1,5):
 grown=seed.buffer(-step*.075,join_style='mitre',mitre_limit=5)
 if grown.is_empty:continue
 geometries=list(grown.geoms) if grown.geom_type=='MultiPolygon' else [grown]
 outlines=[]
 for polygon in geometries:
  for boundary in [polygon.exterior,*polygon.interiors]:
   outlines.append([(.5+x/w,.5+y/h) for x,y in boundary.coords])
 value=[128,111,133,106][step-1];shade='#'+f'{value:02x}'*3
 for center in [-55,-18.333,18.333,55,125,161.667,198.333,235]:
  upper.append(f'<path d="{curved(outlines,center,20,.0047)}" fill="{shade}" fill-rule="evenodd"/>')
upper_clip='<defs><clipPath id="outer-tip-strip"><path d="M 16.2 0 A 16.2 16.2 0 1 0 -16.2 0 A 16.2 16.2 0 1 0 16.2 0 Z M 14.1 0 A 14.1 14.1 0 1 1 -14.1 0 A 14.1 14.1 0 1 1 14.1 0 Z" fill-rule="evenodd" clip-rule="evenodd"/></clipPath></defs>'
fields.append(upper_clip+'<g clip-path="url(#outer-tip-strip)">'+''.join(upper)+'</g>')
head='<svg xmlns="http://www.w3.org/2000/svg" width="3000" height="3000" viewBox="-17 -17 34 34">'
annulus='<path d="M 16.2 0 A 16.2 16.2 0 1 0 -16.2 0 A 16.2 16.2 0 1 0 16.2 0 Z M 11.2 0 A 11.2 11.2 0 1 1 -11.2 0 A 11.2 11.2 0 1 1 11.2 0 Z" fill="#acafa4" fill-rule="evenodd"/>'
body=annulus+'<defs><radialGradient id="x-weight-gradient" gradientUnits="userSpaceOnUse" cx="0" cy="0" r="16.2"><stop offset="0.82" stop-color="white"/><stop offset="0.90" stop-color="#999"/><stop offset="1" stop-color="#777"/></radialGradient><mask id="x-core-weight" maskUnits="userSpaceOnUse" x="-17" y="-17" width="34" height="34"><rect x="-17" y="-17" width="34" height="34" fill="url(#x-weight-gradient)"/></mask></defs>'+ET.tostring(defs,encoding='unicode')+''.join(checks)+'<g clip-path="url(#pattern-band)">'+''.join(fields)+'</g>'+''.join(marks)
svg=head+'<g transform="scale(-1,1)">'+body+'</g></svg>'
target=OUT/'previews/xbox-security-band-mockup-v3.svg';target.write_text(svg,encoding='utf-8')
env=os.environ.copy();env['NODE_PATH']='C:/Users/dimit/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules'
subprocess.run(['node','-e',"const sharp=require('sharp');sharp('outputs/xbox-security-band-mockup-v3.svg').png().toFile('work/xbox-band-mockup-v3-render.png')"],cwd=ROOT,env=env,check=True)
ring=Image.open(ROOT/'work/xbox-band-mockup-v3-render.png').convert('RGBA')
canvas=Image.new('RGB',(1800,1120),'#f5f3e9');d=ImageDraw.Draw(canvas)
title=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',35)
small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24)
d.text((55,35),'GROWING THE X — OUTER BANDS ADDED',font=title,fill='#30372f')
d.text((55,88),'Constant-distance offsets · parallel edges · continuous bands behind the lettering',font=small,fill='#687061')
full=ring.resize((900,900),Image.Resampling.LANCZOS);canvas.paste(full,(10,170),full)
d.text((68,160),'FULL RING',font=small,fill='#687061')
# Show three adjoining X fields on the top arc at a larger scale.
detail=ring.crop((450,0,2570,900));detail.thumbnail((850,650),Image.Resampling.LANCZOS)
canvas.paste(detail,(925,345),detail)
d.text((965,235),'ENLARGED PATTERN',font=small,fill='#687061')
d.text((965,760),'Every edge grows outward by the same amount.',font=small,fill='#434c3d')
d.text((965,802),'Even-width bands continue behind XBOX.',font=small,fill='#434c3d')
d.text((965,844),'The upper tips now carry the bands to the rim.',font=small,fill='#434c3d')
d.text((55,1070),'Pattern study only — the current disc model has not been changed.',font=small,fill='#687061')
canvas.save(OUT/'previews/xbox-security-band-mockup-v3.png')
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==digest for p,digest in before.items())
print('Mockup saved. Current GLB and studio hashes unchanged.')
