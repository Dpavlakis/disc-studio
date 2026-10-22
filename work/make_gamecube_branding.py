"""Trace supplied label-reference silhouettes into reusable native SVG assets."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/branding-source/gamecube-label';OUT.mkdir(parents=True,exist_ok=True)
REF=Path('D:/LaunchBox/Images/Nintendo GameCube/Disc/North America')
sources={
 'logo':('Monster 4x4_ Masters of Metal-01.png',(390,850,910,980)),
 'seal':('Monster 4x4_ Masters of Metal-01.png',(128,825,358,1002)),
 'quality':('Metroid Prime-01.png',(126,820,350,1000)),
 'rating-e':('Monster 4x4_ Masters of Metal-01.png',(937,793,1098,1017)),
 'rating-t':('Mission_ Impossible_ Operation Surma-01.png',(937,793,1098,1017)),
}
def trace(mask):
 a=np.pad(mask,1);edges={}
 def add(ys,xs,dx0,dy0,dx1,dy1):
  for y,x in zip(ys.tolist(),xs.tolist()):edges[(x+dx0,y+dy0)]=(x+dx1,y+dy1)
 add(*np.where(a[1:,:]&~a[:-1,:]),0,1,1,1);add(*np.where(a[:-1,:]&~a[1:,:]),1,1,0,1);add(*np.where(a[:,1:]&~a[:,:-1]),1,1,1,0);add(*np.where(a[:,:-1]&~a[:,1:]),1,0,1,1)
 paths=[]
 while edges:
  start=next(iter(edges));p=start;path=[]
  while p in edges:
   path.append(p);p=edges.pop(p)
   if p==start:break
  if len(path)<5:continue
  reduced=[p for i,p in enumerate(path) if (p[0]-path[i-1][0])*(path[(i+1)%len(path)][1]-p[1])!=(p[1]-path[i-1][1])*(path[(i+1)%len(path)][0]-p[0])]
  if reduced:paths.append('M'+' L'.join(f'{x},{y}' for x,y in reduced)+' Z')
 return ' '.join(paths)
assets={}
for key,(file,box) in sources.items():
 im=Image.open(REF/file).convert('RGB');rgb=np.asarray(im)[box[1]:box[3],box[0]:box[2]]
 mask=rgb.max(axis=2)>48;h,w=mask.shape
 if key in ('seal','quality'):
  yy,xx=np.mgrid[0:h,0:w];mask&=((xx-w/2)/(w/2))**2+((yy-h/2)/(h/2))**2<1
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w+2} {h+2}"><path fill="white" fill-rule="evenodd" d="{trace(mask)}"/></svg>'
 (OUT/(key+'.svg')).write_text(svg,encoding='utf-8');assets[key]=svg
(OUT/'assets.json').write_text(json.dumps(assets),encoding='utf-8')
(OUT/'notes.txt').write_text('Native vector silhouettes traced from supplied local GameCube label references. Baked rainbow colour discarded. GameCube logo, two supplied seal wordings and E/T ratings retained as independent masks; live material supplies foil reflections. Not an assertion that every pressing uses the same placement.\n',encoding='utf-8')
print('Built',len(assets),'vector branding masks from supplied references.')
