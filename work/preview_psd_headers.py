from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parent/'psd-deps'))
from psd_tools import PSDImage
from PIL import Image,ImageDraw,ImageFont,ImageChops
root=Path(__file__).resolve().parents[1]
out=root/'outputs/xbox360-header-preview';out.mkdir(exist_ok=True)
psd=PSDImage.open('C:/Users/dimit/Downloads/xbox360_Template.psd')
branding=next(l for l in psd if l.name.strip()=='Branding')
top=next(l for l in branding if l.name=='Top Branding')
items=[('Old Logo','Classic',372),('Old Logo - Live','Classic · Xbox Live',372),('New Top - Live','New · Live wordmark',363),('New Top - No live','New · No Live',363),('New Top - Xbox Live','New · Xbox Live',363),('New Top - Split','New · Split',363),('Kinect','Kinect',362),('Newest Top','Newest · Green waves',374)]
for layer in psd:layer.visible=layer is branding
for layer in branding:layer.visible=layer is top
records=[]
for index,(name,label,cut) in enumerate(items,1):
 for layer in top:layer.visible=layer.name==name
 group=next(l for l in top if l.name==name)
 image=psd.composite(viewport=(0,0,1440,1440),force=True,ignore_preview=True).convert('RGBA')
 # Only the native header groups: never render Disc / Outer / Inner Ring.
 # Clip the printed header to the artwork circle, with no painted edge ring.
 clip=Image.new('L',(1440,1440));d=ImageDraw.Draw(clip);d.ellipse((30,30,1410,1410),fill=255);d.rectangle((0,cut,1440,1440),fill=0)
 image.putalpha(ImageChops.multiply(image.getchannel('A'),clip))
 path=out/f'{index:02d}-header.png'
 image.save(path,optimize=True)
 records.append({'name':name,'label':label,'file':path.name,'cut':cut})
 print(label,image.getbbox(),flush=True)
# A neutral checkerboard makes the transparent area and clean curved edge clear.
sheet=Image.new('RGB',(1440,1040),'#171c23');draw=ImageDraw.Draw(sheet)
title=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',30)
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20)
draw.text((32,20),'Xbox 360 · Printed header options',font=title,fill='#f1f4f8')
draw.text((32,65),'PSD branding layers only · No disc rim, foil or center ring',font=font,fill='#aab7c7')
for i,item in enumerate(records):
 x=28+(i%2)*710;y=115+(i//2)*228
 draw.rounded_rectangle((x,y,x+684,y+211),radius=12,fill='#242c36')
 draw.text((x+16,y+10),f'{i+1:02d}  {item["label"]}',font=font,fill='#e4ebf4')
 checker=Image.new('RGBA',(650,171),'#c9cdd1');cd=ImageDraw.Draw(checker)
 for yy in range(0,171,12):
  for xx in range(0,650,12):
   if (xx//12+yy//12)%2==0:cd.rectangle((xx,yy,xx+11,yy+11),fill='#e3e6e9')
 header=Image.open(out/item['file']).crop((0,0,1440,380)).resize((650,171),Image.Resampling.LANCZOS)
 checker.alpha_composite(header);sheet.paste(checker.convert('RGB'),(x+16,y+36))
sheet.save(out/'all-headers.png')
(out/'headers.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
