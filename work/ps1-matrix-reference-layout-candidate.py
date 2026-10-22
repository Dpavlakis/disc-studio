"""Vector reconstruction of the visible Tekken reference mastering marks."""
from pathlib import Path
import math,os,subprocess
from original_xbox_vectors import text_paths,bounds

ROOT=Path(__file__).resolve().parents[1]
parts=[]
def path(points):
 return 'M'+' L'.join(f'{x:.5f},{y:.5f}' for x,y in points)+' Z'
def curved(text,angle,size,r=20.72):
 outlines=text_paths('C:/Windows/Fonts/OCRAEXT.TTF',text,size)
 x0,y0,x1,y1=bounds(outlines);middle=(x0+x1)/2
 transformed=[]
 for outline in outlines:
  points=[]
  for x,y in outline:
   a=math.radians(angle)+(x-middle)/r
   rr=r-y+(y0+y1)/2
   points.append((rr*math.sin(a),-rr*math.cos(a)))
  transformed.append(path(points))
 parts.append('<path fill="#202024" fill-rule="evenodd" d="'+' '.join(transformed)+'"/>')
curved('PSRM-002320',90,1.35)
curved('IFPI L331',158,.58,r=20.72)
curved('10',49,1.2)
def sector(a,b,ri,ro,color='#202024',target=None):
 def xy(r,angle):return r*math.sin(math.radians(angle)),-r*math.cos(math.radians(angle))
 x0,y0=xy(ro,a);x1,y1=xy(ro,b);x2,y2=xy(ri,b);x3,y3=xy(ri,a)
 large=1 if b-a>180 else 0
 d=f'M{x0},{y0} A{ro},{ro} 0 {large},1 {x1},{y1} L{x2},{y2} A{ri},{ri} 0 {large},0 {x3},{y3} Z'
 (parts if target is None else target).append(f'<path fill="{color}" d="{d}"/>')
# Transparent bar cutouts reveal actual reflective foil rather than white paint.
cutouts=[]
bed=[]
sector(205,301,20.75,21.9,target=bed)
cursor=213
i=0
while cursor<295:
 width=1.6*(.14,.24,.18,.33,.12,.20,.28)[i%7]
 if not 250<cursor<253.4:sector(cursor,cursor+width,20.87,21.76,'black',cutouts)
 cursor+=width+1.8*(.18,.25,.13,.20,.16)[i%5];i+=1
parts.append('<defs><mask id="barcode-cutouts" maskUnits="userSpaceOnUse" x="-22" y="-22" width="44" height="44"><rect x="-22" y="-22" width="44" height="44" fill="white"/>'+''.join(cutouts)+'</mask></defs><g mask="url(#barcode-cutouts)">'+''.join(bed)+'</g>')
for group in ([345+4.2*i for i in range(8)],[382.8,387.0],[395.4]):
 centres=[(20.72*math.sin(math.radians(a)),-20.72*math.cos(math.radians(a))) for a in group]
 for (x,y),(xx,yy) in zip(centres,centres[1:]):
  dx,dy=xx-x,yy-y;length=math.hypot(dx,dy);ux,uy=dx/length,dy/length
  parts.append(f'<path fill="none" stroke="#202024" stroke-width=".045" d="M{x+ux*.28},{y+uy*.28} L{xx-ux*.28},{yy-uy*.28}"/>')
 for angle,(cx,cy) in zip(group,centres):
  a=math.radians(angle)
  parts.append(f'<circle cx="{cx}" cy="{cy}" r=".28" fill="none" stroke="#202024" stroke-width=".055"/>')
  for offset in (0,math.pi/2,math.pi,3*math.pi/2):
   t=a+offset
   parts.append(f'<path stroke="#202024" stroke-width=".045" d="M{cx+.28*math.cos(t)},{cy+.28*math.sin(t)} L{cx+.49*math.cos(t)},{cy+.49*math.sin(t)}"/>')
for r in (19.58,21.93):parts.append(f'<circle r="{r}" fill="none" stroke="#303034" stroke-width=".09"/>')
svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="-22 -22 44 44">'+''.join(parts)+'</svg>'
