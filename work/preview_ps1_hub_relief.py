"""Procedural surface-relief study, generated independently of the scans."""
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]

def height(r,side):
 def bead(c,w,h):return h*np.exp(-((r-c)/w)**2)
 if side=='top':
  return (bead(7.62,.11,.09)+bead(9.65,.37,.12)-bead(10.35,.24,.065)
          +bead(11.7,.18,.045)-bead(12.05,.14,.026)-bead(20.5,.045,.016))
 return (bead(7.63,.11,.065)-bead(10.05,.065,.035)+bead(11.75,.08,.035)
         -bead(12.05,.10,.022)+bead(17.55,.20,.12)-bead(18.0,.12,.045)-bead(20.5,.05,.022))

def render(side,size=700):
 y,x=np.mgrid[0:size,0:size];x=(x+.5-size/2)*44/size;y=(y+.5-size/2)*44/size
 r=np.sqrt(x*x+y*y);slope=(height(r+.002,side)-height(r-.002,side))/.004
 nx=-slope*x/np.maximum(r,.001);ny=-slope*y/np.maximum(r,.001);nz=np.ones_like(r)
 length=np.sqrt(nx*nx+ny*ny+nz*nz);normal=np.stack((nx/length,ny/length,nz/length),axis=-1)
 color=np.zeros((size,size,3))+np.array([.004,.005,.006])
 # White/cool and warm studio reflections reveal the geometric relief.
 for direction,tint,strength in [((-.8,-.45,.4),(.72,.86,1),.70),((.7,.55,.35),(1,.91,.74),.46)]:
  light=np.array(direction);light/=np.linalg.norm(light);half=light+np.array([0,0,1]);half/=np.linalg.norm(half)
  spec=np.maximum(np.sum(normal*half,axis=-1),0)**110
  diffuse=np.maximum(np.sum(normal*light,axis=-1),0)
  color+=spec[...,None]*np.array(tint)*strength+diffuse[...,None]*.002
 # Slight roughness variation separates broad moulded lands, without paint.
 color+=np.exp(-((r-9)/1.4)**4)[...,None]*.001
 srgb=np.clip(np.where(color<=.0031308,color*12.92,1.055*color**(1/2.4)-.055),0,1)
 rgb=np.uint8(srgb*255)
 rgb[r<7.5]=[72,84,95]
 rgb[r>21.1]=[236,238,233]
 return Image.fromarray(rgb)

canvas=Image.new('RGB',(1600,1080),'#eceee9');draw=ImageDraw.Draw(canvas)
font=lambda n,b=False:ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf' if b else 'segoeui.ttf'),n)
draw.text((45,30),'PS1 INNER HUB — TOP & UNDERSIDE RELIEF',font=font(28,True),fill='#283129')
draw.text((45,75),'Preview only · Reconstructed surface shapes · The webpage is unchanged',font=font(18),fill='#677366')
for cx,side,title in ((410,'top','Top / artwork side'),(1190,'bottom','Underside')):
 draw.text((cx,133),title,font=font(24,True),fill='#283129',anchor='mm')
 canvas.paste(render(side),(cx-350,170))
 text='Raised collar around the hole · Recessed channel' if side=='top' else 'Fine inner grooves · Rounded outer ridge · Outer groove'
 draw.text((cx,890),text,font=font(17),fill='#52604f',anchor='mm')
 # Cross-section of one radial half, displayed with exaggerated vertical relief.
 rr=np.linspace(7.5,21.1,1000);hh=height(rr,side)
 xx=cx-300+(rr-7.5)/13.6*600;yy=985-hh*430
 points=[(round(x),round(y)) for x,y in zip(xx,yy)]
 draw.line(points,fill='#34473d',width=3)
 draw.line((cx-300,985,cx+300,985),fill='#a6afa4',width=1)
 draw.text((cx,1035),'Surface profile · relief exaggerated to show the shape',font=font(15),fill='#677366',anchor='mm')
canvas.save(ROOT/'outputs/ps1-hub-relief-preview.png')
print('Saved top and underside relief preview; no model or webpage changes.')
