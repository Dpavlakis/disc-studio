"""Editable vector covers; layout units remain 1200, output is 4096px."""
from pathlib import Path
import base64,io,math,subprocess
from xml.sax.saxutils import escape
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'outputs/branding-source/default-labels'
SOURCES=ASSETS/'templates'
KEYS=['ps1','ps2','ps3','ps4','xbox','x360','gc','ps2-branding']
COLORS={'ps1':'#bd3c3f','ps2':'#173da5','ps3':'#34383a','ps4':'#0073ce','xbox':'#82d92b','x360':'#6abf36','gc':'#6352a4'}
def text(x,y,s,size,color,bold=False):
 return f'<text x="{x}" y="{y}" text-anchor="middle" dominant-baseline="central" font-family="Arial, sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="{color}">{escape(s)}</text>'
def logo(key,x,y,w,h,color=None):
 im=Image.open(ASSETS/(key+'.png')).convert('RGBA')
 if color:
  tint=Image.new('RGBA',im.size,color);tint.putalpha(im.getchannel('A'));im=tint
 ratio=min(w/im.width,h/im.height);w=im.width*ratio;h=im.height*ratio
 out=io.BytesIO();im.save(out,format='PNG');uri='data:image/png;base64,'+base64.b64encode(out.getvalue()).decode()
 return f'<image x="{x-w/2}" y="{y-h/2}" width="{w}" height="{h}" href="{uri}"/>'
def rect(x,y,w,h,c):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{c}"/>'
def line(x,y,a,b,c,w):return f'<path d="M{x} {y}L{a} {b}" stroke="{c}" stroke-width="{w}"/>'
def arc(box,start,end,color,width):
 x,y,a,b=box;cx=(x+a)/2;cy=(y+b)/2;rx=(a-x)/2;ry=(b-y)/2;t,u=map(math.radians,[start,end])
 return f'<path d="M{cx+rx*math.cos(t)} {cy+ry*math.sin(t)}A{rx} {ry} 0 {int(end-start>180)} 1 {cx+rx*math.cos(u)} {cy+ry*math.sin(u)}" fill="none" stroke="{color}" stroke-width="{width}"/>'
def cover(key):
 p=['<svg xmlns="http://www.w3.org/2000/svg" width="4096" height="4096" viewBox="0 0 1200 1200">','<defs><linearGradient id="silver" x2="1" y2="1"><stop stop-color="#e1e4e1"/><stop offset=".55" stop-color="#eceeea"/><stop offset="1" stop-color="#dfe3e0"/></linearGradient></defs>']
 if key!='ps2-branding':
  p += [rect(0,0,1200,1200,'url(#silver)'),'<circle cx="600" cy="600" r="583" fill="none" stroke="#aaaead" stroke-width="4"/>']
  if key!='gc':p.append(arc((33,33,1167,1167),25 if key=='xbox' else 205,155 if key=='xbox' else 318,COLORS[key],9))
 if key=='ps1':
  p += [logo('ps',600,213,190,155),text(600,318,'PlayStation',43,'#232728',True)]
  p += [rect(429+i*89,365,62,6,c) for i,c in enumerate(['#d63c3e','#e4be33','#16958b','#286da7'])]
 elif key=='ps2':p += [logo('ps',600,215,125,113),text(600,324,'PLAYSTATION 2',40,'#2f3336',True)]
 elif key=='ps2-branding':p += [rect(0,947,1200,253,'#111317'),line(0,947,1200,947,'#6b80b4',3),logo('ps2',600,1046,580,123,'#f3f3ee')]
 elif key=='ps3':p += ['<path d="M0 0H1200V330L0 375Z" fill="#25282c"/>',logo('ps3',600,217,390,135,'#f4f4ef'),text(600,387,'PLAYSTATION 3',27,'#545b60')]
 elif key=='ps4':p += [rect(0,0,1200,310,'#0065b3'),'<path d="M0 298H1200V314L0 366Z" fill="#009ee8"/>',logo('ps4',600,210,410,140,'#ffffff'),text(600,383,'PLAYSTATION 4',27,'#375d77')]
 elif key=='xbox':p += [rect(0,0,1200,330,'#15201a'),logo('xbox',600,219,460,125,'#89d536')]
 elif key=='x360':p += [logo('x360-wordmark',600,214,615,115),arc((-280,1028,1460,1950),195,339,'#69bd38',125),arc((-280,1003,1460,1925),195,339,'#b7d77b',13),text(600,310,'PLAY WITHOUT LIMITS',23,'#66805c')]
 elif key=='gc':p += [rect(0,0,1200,350,'#564686'),line(0,351,1200,351,'#8171b0',7),logo('gc',600,229,480,170,'#ffffff')]
 if key=='gc':p += [text(600,386,'YOUR ARTWORK',36,'#323b3d',True),text(600,414,'REPLACE THIS LABEL TO BEGIN',14,'#6d7675')]
 elif key!='ps2-branding':
  p += [text(600,851,'YOUR ARTWORK',53,'#323b3d',True),text(600,906,'REPLACE THIS LABEL TO BEGIN',22,'#6d7675')]
  if key not in ['ps2','x360']:
   if key!='xbox':p.append(line(455,981,745,981,COLORS[key],4))
   p.append(text(600,1030,'DISC STUDIO / EDITABLE LABEL',20,'#69716e'))
 return ''.join(p)+'</svg>'
def main():
 SOURCES.mkdir(parents=True,exist_ok=True)
 for key in KEYS:(SOURCES/(key+'.svg')).write_text(cover(key),encoding='utf-8')
 subprocess.run(['node',str(ROOT/'work/render_default_labels.cjs')],cwd=ROOT,check=True)
if __name__=='__main__':main()
