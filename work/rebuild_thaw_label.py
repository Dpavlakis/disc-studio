"""Native SVG label reconstruction for a transparent-ink Disc Studio test."""
from pathlib import Path
import sys,ast,json,xml.etree.ElementTree as ET,copy,math
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'outputs/branding-source/tony-hawk-american-wasteland';OUT=ROOT/'outputs/artwork-samples';OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT/'work/vector-deps'))
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
# Reuse only the contour routine, without running the older branding importer.
tree=ast.parse((ROOT/'work/make_gamecube_branding.py').read_text(encoding='utf-8'));fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='trace');ns={'np':np};exec(compile(ast.Module(body=[fn],type_ignores=[]),'trace','exec'),ns);trace=ns['trace']
font=TTFont('C:/Windows/Fonts/arialn.ttf');glyphs=font.getGlyphSet();cmap=font.getBestCmap();units=font['head'].unitsPerEm

def text(value,x,y,size,maxwidth=None,anchor='start',fill='#090909'):
 advance=sum(font['hmtx'][cmap[ord(ch)]][0] for ch in value);scale=size/units;sx=scale if maxwidth is None else min(scale,maxwidth/advance);width=advance*sx
 if anchor=='end':x-=width
 if anchor=='middle':x-=width/2
 parts=[];offset=0
 for ch in value:
  name=cmap[ord(ch)];pen=SVGPathPen(glyphs);glyphs[name].draw(pen);parts.append(f'<path d="{pen.getCommands()}" transform="translate({offset},0)"/>');offset+=font['hmtx'][name][0]
 return f'<g fill="{fill}" transform="translate({x},{y}) scale({sx},{-scale})">'+''.join(parts)+'</g>'

def nested(raw,x,y,w,h):
 r=ET.fromstring(raw);r.set('x',str(x));r.set('y',str(y));r.set('width',str(w));r.set('height',str(h));return ET.tostring(r,encoding='unicode')
# Retain the supplied clear logo's letter outlines. Its pale lettering is bare
# metal on this pressing, so it becomes an opening rather than white ink.
im=Image.open('D:/LaunchBox/Images/Nintendo GameCube/Clear Logo/Tony Hawk_s American Wasteland-01.png').convert('RGBA');a=np.array(im);rgb=a[:,:,:3].astype(float);alpha=a[:,:,3]>100
pale=(rgb.min(axis=2)>145)&((rgb.max(axis=2)-rgb.min(axis=2))<60)
pink=(rgb[:,:,0]>110)&(rgb[:,:,2]>65)&(rgb[:,:,0]>rgb[:,:,1]*1.6)&alpha
black=alpha&~pale
parts=[f'<g transform="translate(280,115) scale(.72)"><g transform="translate(-1,-1)"><path fill="#070707" fill-rule="evenodd" d="{trace(black)}"/><path fill="#ed0085" fill-rule="evenodd" d="{trace(pink)}"/></g></g>']
parts.append(nested((SRC/'Activision.svg').read_text(encoding='utf-8'),78,486,300,75));parts.append('<path d="M78 580H368" stroke="#111" stroke-width="2"/>');parts.append(text('activision.com',78,610,23))
# Trace the clearest user-supplied wordmark, avoiding a substitute typeface.
neversoft=Image.open(SRC/'neversoft-photo-detail.png').convert('RGB');arr=np.asarray(neversoft);mask=arr.max(axis=2)<88
ns_svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {neversoft.width+2} {neversoft.height+2}"><path fill="#090909" fill-rule="evenodd" d="{trace(mask)}"/></svg>';(SRC/'neversoft-reconstructed.svg').write_text(ns_svg,encoding='utf-8');parts.append(nested(ns_svg,78,636,290,120))
lines=['© 2005 Activision Publishing, Inc. Activision is a','registered trademark and THAW is a trademark of','Activision Publishing, Inc. All rights reserved.','Tony Hawk is a registered trademark of Tony','Hawk, Inc. All rights reserved. The ratings icon','is a registered trademark of the Entertainment','Software Association. All other trademarks','and trade names are the properties of their','respective owners.']
for i,line in enumerate(lines):parts.append(text(line,870,494+i*25,22,355))
parts.append(text('80949.101.US',1222,725,22,355,'end'))
ink=''.join(parts)
svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 1280" width="4096" height="4096"><defs><clipPath id="print"><path fill-rule="evenodd" d="M1266.4 640A626.4 626.4 0 1 1 13.6 640A626.4 626.4 0 1 1 1266.4 640 M824 640A184 184 0 1 0 456 640A184 184 0 1 0 824 640"/></clipPath></defs><g clip-path="url(#print)">'+ink+'</g></svg>'
(OUT/'tony-hawk-american-wasteland-test.svg').write_text(svg,encoding='utf-8')
# A separate flat preview shows placement; the upload remains transparent.
assets=json.loads((ROOT/'outputs/branding-source/gamecube-label/assets.json').read_text(encoding='utf-8'))
preview='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 1280" width="1280" height="1280"><defs><clipPath id="disc"><circle cx="640" cy="640" r="626.4"/></clipPath></defs><circle cx="640" cy="640" r="638" fill="#b9bfbe"/><g clip-path="url(#disc)"><rect width="1280" height="1280" fill="#bfc4c2"/><circle cx="640" cy="640" r="354" fill="#161819"/><rect y="770" width="1280" height="510" fill="#080808"/>'+ink
preview+=nested(assets['logo'],390,850,520,130)+nested(assets['seal'],128,825,230,177)+nested(assets['rating-t-alt'],937,793,161,224)
preview+='<rect x="298" y="1058" width="688" height="48" fill="none" stroke="#ccd0cb" stroke-width="3"/>'+text('FOR USE ONLY IN USA, CANADA, MEXICO AND LATIN AMERICA',642,1090,20,660,'middle','#ccd0cb')+text('DL • DOL • GWJE • USA',640,1150,31,650,'middle','#ccd0cb')
# Draw lower wording as actual outlines; no renderer-dependent textPath.
value='MODEL No. DOL-006(USA)';advances=[font['hmtx'][cmap[ord(ch)]][0]*30/units for ch in value];offset=-sum(advances)/2
for ch,width in zip(value,advances):
 angle=math.pi/2-(offset+width/2)/590;x=640+590*math.cos(angle);y=640+590*math.sin(angle)
 preview+=f'<g transform="translate({x},{y}) rotate({math.degrees(angle-math.pi/2)})">'+text(ch,0,0,30,None,'middle','#ccd0cb')+'</g>';offset+=width
preview+='</g><circle cx="640" cy="640" r="184" fill="#e6e8e7" stroke="#a6acab" stroke-width="8"/><circle cx="640" cy="640" r="120" fill="#383d43"/></svg>'

(ROOT/'outputs/previews/tony-hawk-american-wasteland-layout.svg').write_text(preview,encoding='utf-8')
(OUT/'tony-hawk-american-wasteland-notes.txt').write_text('TONY HAWK AMERICAN WASTELAND - TEST RECONSTRUCTION\n\nUpload tony-hawk-american-wasteland-test.png in Disc Studio. Choose GameCube; artwork coverage 100%, rotation 0. Keep GameCube branding on; lower panel #080808; Official Nintendo Seal; alternate Teen T rating (bordered), game code GWJE, branding rotation 0.\n\nThe upload contains print only. Clear areas reveal the model foil, hub and security details. No photographed glare, rainbow, scratches, hub or lower branding are baked in. This is a visual test reconstruction, not an archival scan. Title outlines traced from the existing local LaunchBox clear logo; Activision uses the Wikimedia SVG; Neversoft traced from the clearest supplied photograph. Small legal text reconstructed using Arial Narrow outlines and should be checked against the original. Original reference logos remain third-party assets.\n\nGame code source: https://www.gametdb.com/Wii/GWJE52\nActivision source: https://commons.wikimedia.org/wiki/File:Activision.svg\n',encoding='utf-8')
print('Built native SVG artwork, separate layout preview, and test settings.')
