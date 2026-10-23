from pathlib import Path
import math
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
ROOT=Path(__file__).resolve().parents[1]/'outputs/branding-source/default-labels'
OUT=Path(__file__).resolve().parents[1]/'outputs/default-labels'
FONTS=Path('C:/Windows/Fonts')
def font(size,bold=False):return ImageFont.truetype(str(FONTS/('arialbd.ttf' if bold else 'segoeui.ttf')),size)
def text(im,xy,value,size,color,bold=False,anchor='mm'):
 ImageDraw.Draw(im).text(xy,value,font=font(size,bold),fill=color,anchor=anchor)
def logo(im,key,box,color=None):
 a=Image.open(ROOT/(key+'.png')).convert('RGBA');a.thumbnail((box[2],box[3]),Image.Resampling.LANCZOS)
 if color:
  tint=Image.new('RGBA',a.size,color);tint.putalpha(a.getchannel('A'));a=tint
 im.alpha_composite(a,(int(box[0]-a.width/2),int(box[1]-a.height/2)))
def label(key):
 S=1200;y,x=np.indices((S,S));v=(x/S*.6+y/S*.4)
 shade=222+13*np.sin(v*math.pi)+5*np.cos((x-y)/S*6)
 arr=np.stack([shade+2,shade+3,shade+2],axis=-1).clip(0,255).astype('uint8')
 im=Image.fromarray(arr).convert('RGBA');d=ImageDraw.Draw(im)
 # Fine perimeter accent and generous unprinted silver around the spindle.
 accent={'ps1':'#bd3c3f','ps2':'#173da5','ps3':'#34383a','ps4':'#0073ce','xbox':'#82d92b','x360':'#6abf36','gc':'#6352a4'}[key]
 d.ellipse((17,17,S-17,S-17),outline='#aaaead',width=4)
 d.arc((33,33,S-33,S-33),205,318,fill=accent,width=9)
 if key=='ps1':
  logo(im,'ps',(600,213,190,155))
  text(im,(600,318),'PlayStation',43,'#232728',True)
  for i,c in enumerate(['#d63c3e','#e4be33','#16958b','#286da7']):d.rectangle((429+i*89,365,491+i*89,371),fill=c)
 elif key=='ps2':
  d.rectangle((0,947,S,S),fill='#111317');d.line((0,947,S,947),fill='#6b80b4',width=3)
  logo(im,'ps2',(600,1046,580,123),'#f3f3ee')
  logo(im,'ps',(600,215,125,113))
  text(im,(600,324),'PLAYSTATION 2',40,'#2f3336',True)
 elif key=='ps3':
  d.rectangle((0,0,S,322),fill='#25282c')
  d.polygon([(0,300),(S,300),(S,330),(0,375)],fill='#25282c')
  logo(im,'ps3',(600,217,390,135),'#f4f4ef')
  text(im,(600,387),'PLAYSTATION 3',27,'#545b60')
 elif key=='ps4':
  d.rectangle((0,0,S,310),fill='#0065b3')
  d.polygon([(0,298),(S,298),(S,314),(0,366)],fill='#009ee8')
  logo(im,'ps4',(600,210,410,140),'#ffffff')
  text(im,(600,383),'PLAYSTATION 4',27,'#375d77')
 elif key=='xbox':
  d.rectangle((0,0,S,330),fill='#15201a')
  logo(im,'xbox',(600,219,460,125),'#89d536')
  d.line((180,351,1020,351),fill='#7cb836',width=6)
 elif key=='x360':
  text(im,(600,214),'XBOX 360',85,'#43563a',True)
  d.arc((-280,1028,1460,1950),195,339,fill='#69bd38',width=125)
  d.arc((-280,1003,1460,1925),195,339,fill='#b7d77b',width=13)
  text(im,(600,310),'PLAY WITHOUT LIMITS',23,'#66805c')
 else:
  d.rectangle((0,0,S,350),fill='#564686')
  d.line((0,351,S,351),fill='#8171b0',width=7)
  logo(im,'gc',(600,229,480,170),'#ffffff')
 # Common placeholder is visibly intentional and subordinate to the platform.
 text(im,(600,851),'YOUR ARTWORK',53,'#323b3d',True)
 text(im,(600,906),'REPLACE THIS LABEL TO BEGIN',22,'#6d7675')
 if key not in ['ps2','x360']:
  d.line((455,981,745,981),fill=accent,width=4)
  text(im,(600,1030),'DISC STUDIO  /  EDITABLE LABEL',20,'#69716e')
 # Artwork only: centre plastic, spindle hole and bevel remain real model parts.
 if key=='ps2':
  band=Image.new('RGBA',(S,S));band.paste(im.crop((0,947,S,S)),(0,947))
  band.save(OUT/'ps2-branding.png')
  ImageDraw.Draw(im).rectangle((0,947,S,S),fill='#e5e8e5')
 im.save(OUT/(key+'.png'))
 return im

if __name__=='__main__':
 for system in ['ps1','ps2','ps3','ps4','xbox','x360','gc']:label(system)
 print('Generated seven approved artwork-only labels and separate PS2 branding.')
