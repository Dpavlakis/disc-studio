"""Font outlines and supplied symbol paths, curved in physical ring coordinates."""
from pathlib import Path
import sys,math,xml.etree.ElementTree as ET,subprocess,os
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).parent/'vector-deps'))
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from fontTools.svgLib.path import parse_path
from shapely.geometry import Polygon
from shapely.ops import unary_union

ROOT=Path(__file__).resolve().parents[1]
class OutlinePen(BasePen):
 def __init__(self,glyphs=None):super().__init__(glyphs);self.paths=[];self.current=[]
 def _moveTo(self,p):self.current=[p]
 def _lineTo(self,p):
  a=self.current[-1];n=max(1,math.ceil(math.dist(a,p)/20))
  self.current.extend([(a[0]+(p[0]-a[0])*i/n,a[1]+(p[1]-a[1])*i/n) for i in range(1,n+1)])
 def _curveToOne(self,b,c,d):
  a=self.current[-1]
  for i in range(1,25):
   t=i/24;s=1-t;self.current.append(tuple(s*s*s*a[j]+3*s*s*t*b[j]+3*s*t*t*c[j]+t*t*t*d[j] for j in (0,1)))
 def _qCurveToOne(self,b,c):
  a=self.current[-1]
  for i in range(1,21):
   t=i/20;s=1-t;self.current.append(tuple(s*s*a[j]+2*s*t*b[j]+t*t*c[j] for j in (0,1)))
 def _closePath(self):self.paths.append(self.current);self.current=[]
 def _endPath(self):self._closePath()

def bounds(paths):
 points=[p for path in paths for p in path]
 return min(p[0] for p in points),min(p[1] for p in points),max(p[0] for p in points),max(p[1] for p in points)
def text_paths(file,text,size):
 font=TTFont(file);glyphs=font.getGlyphSet();cmap=font.getBestCmap();factor=size/font['head'].unitsPerEm;x=0;paths=[]
 for ch in text:
  name=cmap[ord(ch)];pen=OutlinePen(glyphs);glyphs[name].draw(pen)
  paths.extend([[(x+px*factor,-py*factor) for px,py in path] for path in pen.paths]);x+=font['hmtx'][name][0]*factor
 return paths
def normalized(paths,padding=0):
 x0,y0,x1,y1=bounds(paths);w=x1-x0+2*padding;h=y1-y0+2*padding
 return [[((x-x0+padding)/w,(y-y0+padding)/h) for x,y in path] for path in paths],w,h
def curved(paths,center,arc,height,front=False,radius=.0137):
 commands=[]
 for path in paths:
  points=[]
  for u,v in path:
   if front:u=1-u
   theta=math.radians(center+(u-.5)*arc);r=radius+(.5-v)*height
   points.append((1000*r*math.sin(theta),-1000*r*math.cos(theta)))
  if points:commands.append('M'+' L'.join(f'{x:.6f},{y:.6f}' for x,y in points)+' Z')
 return ' '.join(commands)

def silhouette_paths():
 # Union the supplied symbol's touching filled pieces before outlining it.
 # Its internal 3D facets must not become extra security-pattern lines.
 im=Image.open(ROOT/'work/xbox-original-symbol.png').getchannel('A');im=im.crop(im.getbbox())
 a=np.pad(np.asarray(im)>127,1);edges={}
 def add(ys,xs,dx0,dy0,dx1,dy1):
  for y,x in zip(ys.tolist(),xs.tolist()):edges[(x+dx0,y+dy0)]=(x+dx1,y+dy1)
 add(*np.where(a[1:,:]&~a[:-1,:]),0,1,1,1)
 add(*np.where(a[:-1,:]&~a[1:,:]),1,1,0,1)
 add(*np.where(a[:,1:]&~a[:,:-1]),1,1,1,0)
 add(*np.where(a[:,:-1]&~a[:,1:]),1,0,1,1)
 paths=[]
 while edges:
  start=next(iter(edges));p=start;path=[]
  while p in edges:
   path.append(p);p=edges.pop(p)
   if p==start:break
  if len(path)>10:
   # Remove collinear pixel-edge vertices; the 1200px source exceeds the
   # rendered symbol's size, so no bitmap upsampling is introduced.
   reduced=[p for i,p in enumerate(path) if (p[0]-path[i-1][0])*(path[(i+1)%len(path)][1]-p[1])!=(p[1]-path[i-1][1])*(path[(i+1)%len(path)][0]-p[0])]
   paths.append(reduced)
 return normalized(paths)[0]

def outlined_wordmark(d):
 # Shared physical stroke widths for every XBOX mark on both faces.
 return ('<g data-wordmark="XBOX">'
  +f'<path d="{d}" fill="white" stroke="#999" stroke-width="0.095" stroke-linejoin="round"/>'
  +f'<path d="{d}" fill="white" stroke="black" stroke-width="0.045" stroke-linejoin="round"/>'
  +f'<path d="{d}" fill="white"/></g>')

def filled_shape(d):
 pen=OutlinePen();parse_path(d,pen)
 return unary_union([Polygon(path).buffer(0) for path in pen.paths if len(path)>3])

def build_vectors():
 font=ROOT/'outputs/branding-source/XboxOriginalBold.ttf'
 word,w,h=normalized(text_paths(font,'XBOX',160),6)
 symbols=[]
 svg=ET.parse(ROOT/'outputs/branding-source/xbox-original-symbol.svg')
 layer=next(e for e in svg.iter() if e.attrib.get('id')=='layer1')
 for element in layer.iter():
  if element.tag.endswith('path'):
   pen=OutlinePen();parse_path(element.attrib['d'],pen);symbols.extend(pen.paths)
 symbol,_,_=normalized(symbols)
 # Fit the complete outlined word between the adjacent X shapes. Preserve
 # the native letter proportions and include the keyline in the clearance.
 neighbors=unary_union([filled_shape(curved(symbol,c,20,.0047)) for c in (-18.333,18.333)])
 low,high=24.,30.
 for _ in range(22):
  arc=(low+high)/2
  shape=filled_shape(curved(word,0,arc,.0137*math.radians(arc)*h/w)).buffer(.0475)
  if shape.distance(neighbors)>=.005:low=arc
  else:high=arc
 fitted_arc=low
 print(f'Arc XBOX lettering fitted at {fitted_arc:.4f} degrees, with 0.005 mm keyline clearance')
 # Exact constant-distance field from the user-selected v2 mockup.
 # Keep this frozen source separate from subsequent rejected mockups.
 approved=ET.parse(ROOT/'outputs/branding-source/xbox-original-approved-x-bands.svg').getroot()
 approved_defs=next(e for e in approved if e.tag.endswith('defs'))
 approved_field=next(e for e in approved if e.get('clip-path')=='url(#pattern-band)')
 assert len(approved_field)==31
 defs=ET.tostring(approved_defs,encoding='unicode')
 pattern=[ET.tostring(e,encoding='unicode') for e in approved_field]
 pattern_group=defs+'<g clip-path="url(#pattern-band)">'+''.join(pattern)+'</g>'
 head='<svg xmlns="http://www.w3.org/2000/svg" width="4096" height="4096" viewBox="-17 -17 34 34">'
 (ROOT/'work/xbox-vector-contours.svg').write_text(head+'<rect x="-17" y="-17" width="34" height="34" fill="black"/>'+pattern_group+'</svg>',encoding='utf-8')
 panel=[]
 for i,line in enumerate(['XBOX','genuine','XBOX','genuine','XBOX','genuine','XBOX']):
  file=font if line=='XBOX' else 'C:/Windows/Fonts/georgiaz.ttf'
  native=text_paths(file,line,1);b=bounds(native);size=(210*.95)/(b[2]-b[0])
  paths=text_paths(file,line,size);x0,y0,x1,y1=bounds(paths)
  assert abs((x1-x0)/210-.95)<1e-8
  # Original 210 x 420 panel rotated 90 degrees, before its polar mapping.
  panel.append((line,[[((y-(y0+y1)/2+32+i*59)/420,(210-(x-(x0+x1)/2+105))/210) for x,y in path] for path in paths]))
 for front in (False,True):
  parts=[]
  for center in [-55,-18.333,18.333,55,125,161.667,198.333,235]:
   parts.append(f'<path d="{curved(symbol,center,20,.0047,front)}" fill="white"/>')
  for center in [-36.667,0,36.667,90,143.333,180,216.667]:
   arc=30 if center==90 else fitted_arc
   d=curved(word,center,arc,.0137*math.radians(arc)*h/w,front)
   parts.append(outlined_wordmark(d))
  for line,paths in panel:
   # Center on the exposed foil, inside the lip at radius 16.05 mm.
   d=curved(paths,270,38,.005,front,radius=.013625)
   parts.append(outlined_wordmark(d) if line=='XBOX' else f'<path d="{d}" fill="white"/>')
  head='<svg xmlns="http://www.w3.org/2000/svg" width="4096" height="4096" viewBox="-17 -17 34 34">'
  side='front' if front else 'rear'
  mask=head+'<rect x="-17" y="-17" width="34" height="34" fill="black"/>'+''.join(parts)+'</svg>'
  (ROOT/f'work/xbox-vector-{side}.svg').write_text(mask,encoding='utf-8')
  # Readable front artwork: reverse the layout while retaining local lettering.
  # Checker sectors have exactly three radial rows, six angular columns.
  checks=[]
  for center in (90,270):
   for row in range(3):
    for col in range(6):
     if (row+col)%2==0:continue
     a0=center-20+col*40/6;a1=a0+40/6;r0=11.2+row*5/3;r1=r0+5/3
     points=[(r*math.sin(math.radians(a)),-r*math.cos(math.radians(a))) for r,angles in ((r0,[a0+(a1-a0)*i/12 for i in range(13)]),(r1,[a1-(a1-a0)*i/12 for i in range(13)])) for a in angles]
     checks.append('<path fill="#686868" d="M'+' L'.join(f'{x:.5f},{y:.5f}' for x,y in points)+' Z"/>')
  master=head+'<g'+(' transform="scale(-1,1)"' if front else '')+'>'+''.join(checks)+defs+'<g clip-path="url(#pattern-band)">'+''.join(pattern)+'</g>'+''.join(parts)+'</g></svg>'
  (ROOT/f'outputs/branding-source/xbox-original-security-{side}.svg').write_text(master,encoding='utf-8')
 env=os.environ.copy();env['NODE_PATH']='C:/Users/dimit/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules'
 subprocess.run(['node',str(ROOT/'work/render_xbox_vectors.cjs')],cwd=ROOT,env=env,check=True)

if __name__=='__main__':build_vectors()
