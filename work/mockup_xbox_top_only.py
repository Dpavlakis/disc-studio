"""Add only three upper contours to the accepted v2 mockup."""
from pathlib import Path
import sys,copy,math,os,subprocess,hashlib,xml.etree.ElementTree as ET
from PIL import Image
from original_xbox_vectors import OutlinePen
from fontTools.svgLib.path import parse_path
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs'
ET.register_namespace('','http://www.w3.org/2000/svg')
unchanged={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in [OUT/'xbox-original-disc.glb',OUT/'studio.html']}
root=ET.parse(OUT/'previews/xbox-security-band-mockup-v2.svg').getroot();group=list(root)[0]
symbols=[];seen_words=0
for item in group:
 if item.get('data-wordmark')=='XBOX':seen_words+=1
 elif seen_words==7 and item.tag.endswith('path') and len(symbols)<8:symbols.append(item)
assert len(symbols)==8
def path_d(geometry):
 shapes=list(geometry.geoms) if geometry.geom_type=='MultiPolygon' else [geometry];parts=[]
 for polygon in shapes:
  if polygon.is_empty:continue
  for boundary in [polygon.exterior,*polygon.interiors]:
   parts.append('M'+' L'.join(f'{x:.6f},{y:.6f}' for x,y in boundary.coords)+' Z')
 return ' '.join(parts)
lines=[]
shell=Point(0,0).buffer(16.2,quad_segs=256).difference(Point(0,0).buffer(14.15,quad_segs=256))
for item in symbols:
 pen=OutlinePen();parse_path(item.get('d'),pen)
 pieces=[Polygon(p).buffer(0) for p in pen.paths if len(p)>3]
 solid=unary_union([p for p in pieces if p.area>.005])
 upper=solid.intersection(shell)
 for piece in getattr(upper,'geoms',[upper]):
  if piece.area<.05:continue
  wedge=piece.convex_hull.simplify(.035,preserve_topology=True)
  for distance in (.12,.28,.44):
   inner=wedge.buffer(-distance,join_style='mitre',mitre_limit=5)
   if inner.is_empty:continue
   points=list(inner.exterior.coords)[:-1]
   # Leave the outer rim edge open. The other three edges make the same
   # clean, parallel bend as the reference, without the symbol's facets.
   edge=max(range(len(points)),key=lambda i:math.hypot((points[i][0]+points[(i+1)%len(points)][0])/2,(points[i][1]+points[(i+1)%len(points)][1])/2))
   path=points[edge+1:]+points[:edge+1]
   def to_rim(a,b):
    dx=a[0]-b[0];dy=a[1]-b[1];length=math.hypot(dx,dy);dx/=length;dy/=length
    dot=a[0]*dx+a[1]*dy;t=-dot+math.sqrt(dot*dot+16.2**2-a[0]**2-a[1]**2)
    return (a[0]+t*dx,a[1]+t*dy)
   path[0]=to_rim(path[0],path[1]);path[-1]=to_rim(path[-1],path[-2])
   d='M'+' L'.join(f'{x:.6f},{y:.6f}' for x,y in path)
   lines.append(f'<path d="{d}" fill="none" stroke="#53584f" stroke-width="0.055" stroke-linejoin="miter"/>')
strip='<defs><clipPath id="top-only"><path d="M16.2 0 A16.2 16.2 0 1 0 -16.2 0 A16.2 16.2 0 1 0 16.2 0 Z M14.1 0 A14.1 14.1 0 1 1 -14.1 0 A14.1 14.1 0 1 1 14.1 0 Z" clip-rule="evenodd" fill-rule="evenodd"/></clipPath></defs>'
fragment=ET.fromstring('<g xmlns="http://www.w3.org/2000/svg">'+strip+'<g clip-path="url(#top-only)">'+''.join(lines)+'</g></g>')
group.append(fragment)
target=OUT/'previews/xbox-security-band-mockup-v4.svg';ET.ElementTree(root).write(target,encoding='utf-8',xml_declaration=True)
env=os.environ.copy();env['NODE_PATH']='C:/Users/dimit/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules'
subprocess.run(['node','-e',"const sharp=require('sharp');sharp('outputs/xbox-security-band-mockup-v4.svg').png().toFile('work/xbox-band-mockup-v4-render.png')"],cwd=ROOT,env=env,check=True)
ring=Image.open(ROOT/'work/xbox-band-mockup-v4-render.png').convert('RGBA')
# Preserve the accepted board exactly, replacing only the two ring previews.
canvas=Image.open(OUT/'previews/xbox-security-band-mockup-v2.png').convert('RGB')
full=ring.resize((900,900),Image.Resampling.LANCZOS);canvas.paste(full,(10,170),full)
detail=ring.crop((450,0,2570,900));detail.thumbnail((850,650),Image.Resampling.LANCZOS);canvas.paste(detail,(925,345),detail)
canvas.save(OUT/'previews/xbox-security-band-mockup-v4.png')
closeup=Image.new('RGB',(645,750),'#f5f3e9');crop=ring.crop((2450,450,2880,950)).resize((645,750),Image.Resampling.LANCZOS);closeup.paste(crop,(0,0),crop);closeup.save(OUT/'previews/xbox-security-upper-bands-detail.png')
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==digest for p,digest in unchanged.items())
print('Preserved the accepted v2 artwork; added upper contours only. Studio/model unchanged.')
