"""Use supplied SVG curves as monochrome metallic masks; no scan tracing."""
from pathlib import Path
import json,copy,re,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/branding-source/gamecube-label';SVG='http://www.w3.org/2000/svg'
E.register_namespace('',SVG)
files={'logo':'Nintendo_GameCube_Official_Logo.svg','seal':'Nintendo_Official_Seal.svg','quality':'Nintendo_Seal_of_Quality_-_Oval_-_Trademark.svg'}
assets=json.loads((OUT/'assets.json').read_text())
for key,name in files.items():
 source=OUT/('supplied-'+name);raw=source.read_text(encoding='utf-8');root=E.fromstring(raw);vb=root.get('viewBox')
 (OUT/('supplied-'+name)).write_text(raw,encoding='utf-8')
 # All files contain path outlines, including the wording; no replacement font.
 paths=[]
 for node in root.iter():
  tag=node.tag.split('}')[-1]
  if tag not in ['path','polygon','polyline','rect','circle','ellipse','g']:continue
  if tag=='g':continue
  item=copy.deepcopy(node);style=item.attrib.pop('style','');fill=item.get('fill')
  match=re.search(r'(?:^|;)\s*fill\s*:\s*([^;]+)',style)
  if match:fill=match.group(1).strip()
  if key=='logo':ink='white' # Supplied logo is already solid outlines.
  else:ink='black' if fill and fill.lower() in ['#ffffff','#fff','white'] else 'white'
  item.set('fill',ink);item.attrib.pop('class',None)
  # Preserve shape transforms, compound paths and holes; discard baked ink colour.
  item.set('stroke','none');item.attrib.pop('opacity',None)
  paths.append(E.tostring(item,encoding='unicode'))
 mask='<svg xmlns="'+SVG+'" viewBox="'+vb+'"><defs><mask id="foil-'+key+'" maskUnits="userSpaceOnUse" x="0" y="0" width="100%" height="100%" style="mask-type:luminance">'+''.join(paths)+'</mask></defs><rect x="0" y="0" width="100%" height="100%" fill="white" mask="url(#foil-'+key+')"/></svg>'
 (OUT/(key+'.svg')).write_text(mask,encoding='utf-8');assets[key]=mask
(OUT/'assets.json').write_text(json.dumps(assets),encoding='utf-8')
(OUT/'vector-source-notes.txt').write_text('GameCube logo and both Nintendo seals use the three SVG files supplied by the user. Original source files retained here. Original outlined lettering and shapes retained; monochrome masks replace baked colours so the 3D metallic material provides live reflections. Rating variants are imported from the supplied ESRB SVGs by import_esrb_vectors.py.\n',encoding='utf-8')
print('Imported supplied vector logo and two seals without raster tracing.')
