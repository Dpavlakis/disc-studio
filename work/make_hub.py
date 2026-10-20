from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import math,random
out=Path(__file__).resolve().parents[1]/'outputs'
S=4096; C=S/2; scale=S/.12
im=Image.new('RGB',(S,S),'#ffffff'); d=ImageDraw.Draw(im)
def ring(r,w,color):
 r*=scale; d.ellipse((C-r,C-r,C+r,C+r),outline=color,width=max(1,int(w*scale)))
for r,w,col in [(.0195,.0081,'#111111')]:ring(r,w,col)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',64)
tiny=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',27)
def stamp(text,r,angle,font,color):
 tile=Image.new('RGBA',(1000,180)); td=ImageDraw.Draw(tile); td.text((500,90),text,font=font,fill=color,anchor='mm')
 if text=='0' and 'OCR' in font.getname()[0]:
  td.line((491,102,509,78),fill=color,width=2)
 tile=tile.rotate(-angle,resample=Image.Resampling.BICUBIC,expand=True)
 a=math.radians(angle); px=C+math.sin(a)*r*scale; py=C-math.cos(a)*r*scale
 im.paste(tile,(round(px-tile.width/2),round(py-tile.height/2)),tile)
for filename,angles in [('ps2-wordmark.png',[0,120,240]),('ps-logo.png',[60,180,300])]:
 source=Image.open(Path(__file__).parent/filename).convert('RGBA')
 # Match the reference's compact, alternating marks on the same radial centerline.
 width=420 if filename=='ps2-wordmark.png' else 120
 source=source.resize((width,round(source.height*width/source.width)),Image.Resampling.LANCZOS)
 source.putalpha(source.getchannel('A').point(lambda x:round(x*.62)))
 for angle in angles:
  tile=source.rotate(-angle,resample=Image.Resampling.BICUBIC,expand=True)
  a=math.radians(angle); px=C+math.sin(a)*.0147*scale; py=C-math.cos(a)*.0147*scale
  im.paste(tile,(round(px-tile.width/2),round(py-tile.height/2)),tile)
# Compact matrix lettering with true glyph advances, rather than fixed wide tracking.
matrix=ImageFont.truetype('C:/Windows/Fonts/OCRAEXT.TTF',47)
matrix_small=ImageFont.truetype('C:/Windows/Fonts/OCRAEXT.TTF',31)
serif=ImageFont.truetype('C:/Windows/Fonts/timesbd.ttf',31)
def arc_text(text,r,center,font):
 widths=[font.getlength(ch) for ch in text]
 factor=180/math.pi/(r*scale); angle=center-sum(widths)*factor/2
 for ch,w in zip(text,widths):
  stamp(ch,r,angle+w*factor/2,font,'#141414'); angle+=w*factor
arc_text('PDSS–013405A1',.0211,94,matrix)
arc_text('IFPI L331',.02115,0,matrix_small)
arc_text('A03',.0211,35,matrix_small)
arc_text('1',.0211,143,matrix)
random.seed(12); d=ImageDraw.Draw(im)
def sector(start,end,ri,ro,color):
 steps=max(2,round((end-start)*8))
 angles=[math.radians(start+(end-start)*i/steps) for i in range(steps+1)]
 points=[(C+math.sin(a)*ro*scale,C-math.cos(a)*ro*scale) for a in angles]
 points +=[(C+math.sin(a)*ri*scale,C-math.cos(a)*ri*scale) for a in reversed(angles)]
 d.polygon(points,fill=color)
# Dark mastering band with bright radial strokes and clean terminal blocks.
# Barcode is modeled as geometric sectors in build_disc.py.
im.save(out/'hub-branding.png')
# Green roughness channel gives the etched lettering a different light response.
import numpy as np
a=np.asarray(im); light=a.mean(axis=2)>100
rough=np.empty_like(a); rough[:,:,0]=255;rough[:,:,1]=np.where(light,40,65);rough[:,:,2]=255
Image.fromarray(rough).save(out/'hub-metal-roughness.png')
im.crop((int(C-.0235*scale),int(C-.0235*scale),int(C+.0235*scale),int(C+.0235*scale))).resize((1000,1000)).save(out/'hub-detail-preview.png')
