"""Import supplied ESRB outlines as metallic masks, preserving transforms and lettering."""
from pathlib import Path
import json,re,xml.etree.ElementTree as ET,shutil
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/branding-source/gamecube-label';NS='http://www.w3.org/2000/svg';ET.register_namespace('',NS)
FILES={'e':'ESRB_E_1999.svg','t':'ESRB_T_1999.svg','m':'ESRB_M_1999.svg','e-alt':'ESRB_Everyone.svg','e10':'ESRB_Everyone_10+.svg','t-alt':'ESRB_Teen.svg','m17':'ESRB_Mature_17+.svg'}
assets=json.loads((OUT/'assets.json').read_text(encoding='utf-8'))
for key,name in FILES.items():
 source=OUT/('supplied-'+name)
 if not source.exists():shutil.copy2(Path('C:/Users/dimit/Downloads')/name,source)
 svg=ET.fromstring(source.read_text(encoding='utf-8'));vb=svg.get('viewBox')
 if not vb:
  width=float(re.match(r'[\d.]+',svg.get('width')).group());height=float(re.match(r'[\d.]+',svg.get('height')).group());vb=f'0 0 {width:g} {height:g}'
 x,y,w,h=map(float,vb.split());content=[]
 for child in svg:
  if child.tag.split('}')[-1] in {'metadata','namedview','title','desc'}:continue
  content.append(ET.tostring(child,encoding='unicode'))
 # The supplied white shapes become foil; black areas reveal the panel or
 # the physical disc. Keep all outlined lettering and parent transforms.
 mask=f'<svg xmlns="{NS}" viewBox="{vb}"><defs><mask id="rating-{key}" maskUnits="userSpaceOnUse" x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" style="mask-type:luminance"><rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="black"/><g fill="black">'+''.join(content)+f'</g></mask></defs><rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="white" mask="url(#rating-{key})"/></svg>'
 ET.fromstring(mask);assets['rating-'+key]=mask;(OUT/('rating-'+key+'.svg')).write_text(mask,encoding='utf-8')
(OUT/'assets.json').write_text(json.dumps(assets),encoding='utf-8')
(OUT/'rating-source-notes.txt').write_text('Seven ESRB variants imported from the SVGs supplied by the user. Original files retained as supplied-*.svg. White artwork maps to reflective foil; black areas are transparent. Original outlined lettering, shapes, aspect ratios and parent transforms preserved. Default E/T options now use the supplied 1999 outlines rather than scan traces.\n',encoding='utf-8')
print('Imported seven ESRB vector variants.')
