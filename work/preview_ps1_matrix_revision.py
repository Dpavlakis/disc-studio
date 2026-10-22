"""Preview OCR lettering, dark-backed barcode and linked mastering symbols."""
from pathlib import Path
import math,os,subprocess
from original_xbox_vectors import text_paths,bounds
ROOT=Path(__file__).resolve().parents[1]
parts=[]
def path(points):return 'M'+' L'.join(f'{x:.5f},{y:.5f}' for x,y in points)+' Z'
def polar(r,a):return (r*math.sin(math.radians(a)),-r*math.cos(math.radians(a)))
def curved(text,angle,size,r=20.72):
 outlines=text_paths('C:/Windows/Fonts/OCRAEXT.TTF',text,size)
 x0,y0,x1,y1=bounds(outlines);middle=(x0+x1)/2
 ds=[]
 for outline in outlines:
  points=[]
  for x,y in outline:
   a=math.radians(angle)+(x-middle)/r;rr=r-y+(y0+y1)/2
   points.append((rr*math.sin(a),-rr*math.cos(a)))
  ds.append(path(points))
 parts.append('<path fill="#202024" fill-rule="evenodd" d="'+' '.join(ds)+'"/>')
def sector(a,b,ri,ro,color='#202024'):
 points=[polar(r,v) for r,angles in ((ro,[a+(b-a)*i/12 for i in range(13)]),(ri,[b-(b-a)*i/12 for i in range(13)])) for v in angles]
 parts.append(f'<path fill="{color}" d="{path(points)}"/>')
curved('PSRM-002320',324,.94)
curved('IFPI L331',24,.42,r=21.5)
curved('10',270,.8)
# A continuous dark bed remains behind and alongside the pale barcode bars.
sector(77,192,19.62,21.9)
cursor=83;i=0
while cursor<153:
 width=1.6*(.14,.24,.18,.33,.12,.20,.28)[i%7]
 if not 119<cursor<122.4:sector(cursor,cursor+width,19.83,21.65,'#b9bdb6')
 cursor+=width+1.8*(.18,.25,.13,.20,.16)[i%5];i+=1
# Connected outline hexagons with short registration spurs, rather than stars.
angles=[212+4.8*i for i in range(9)]
centres=[polar(20.72,a) for a in angles]
for (x,y),(xx,yy) in zip(centres,centres[1:]):
 dx,dy=xx-x,yy-y;length=math.hypot(dx,dy);ux,uy=dx/length,dy/length
 parts.append(f'<path fill="none" stroke="#202024" stroke-width=".055" d="M{x+ux*.33},{y+uy*.33} L{xx-ux*.33},{yy-uy*.33}"/>')
for angle,(cx,cy) in zip(angles,centres):
 a=math.radians(angle)
 points=[(cx+.34*math.cos(a+math.pi/6+i*math.pi/3),cy+.34*math.sin(a+math.pi/6+i*math.pi/3)) for i in range(6)]
 parts.append(f'<path fill="none" stroke="#202024" stroke-width=".065" d="{path(points)}"/>')
 for offset in (0,math.pi/2,math.pi,3*math.pi/2):
  t=a+offset
  parts.append(f'<path stroke="#202024" stroke-width=".055" d="M{cx+.27*math.cos(t)},{cy+.27*math.sin(t)} L{cx+.49*math.cos(t)},{cy+.49*math.sin(t)}"/>')
for r in (19.58,21.93):parts.append(f'<circle r="{r}" fill="none" stroke="#303034" stroke-width=".09"/>')
revised=''.join(parts)
current=(ROOT/'outputs/branding-source/ps1-mastering-ring.svg').read_text(encoding='utf-8').split('>',1)[1].rsplit('</svg>',1)[0]
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1060" viewBox="0 0 1800 1060"><rect width="1800" height="1060" fill="#eceee9"/>',
 '<g font-family="Segoe UI,Arial,sans-serif" fill="#283129"><text x="50" y="55" font-size="29" font-weight="600">PS1 SILVER RING — REVISED DETAIL PREVIEW</text>',
 '<text x="50" y="88" font-size="18" fill="#677366">Preview only · The webpage is unchanged.</text>',
 '<text x="450" y="145" text-anchor="middle" font-size="24">Current</text><text x="1350" y="145" text-anchor="middle" font-size="24" font-weight="600">OCR font + Revised barcode and symbols</text></g>']
for cx,marks in ((450,current),(1350,revised)):
 svg.append(f'<g transform="translate({cx},575) scale(18.4)"><circle r="22" fill="#b9bdb6"/><circle r="19.5" fill="#0a0d0e"/><circle r="7.5" fill="#465360"/>{marks}</g>')
svg.append('<text x="900" y="1030" font-family="Segoe UI,Arial,sans-serif" text-anchor="middle" fill="#677366" font-size="18">OCR lettering · Dark barcode bed with a gap · Linked outline symbols · Heavier boundary lines</text></svg>')
(ROOT/'outputs/ps1-ring-revised-details-preview.svg').write_text(''.join(svg),encoding='utf-8')
env=os.environ.copy();env['NODE_PATH']='C:/Users/dimit/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules'
subprocess.run(['node','-e',"require('sharp')('outputs/ps1-ring-revised-details-preview.svg').png().toFile('outputs/ps1-ring-revised-details-preview.png').catch(e=>{console.error(e);process.exit(1)})"],cwd=ROOT,env=env,check=True)
print('Revised preview saved; studio model and textures unchanged.')
