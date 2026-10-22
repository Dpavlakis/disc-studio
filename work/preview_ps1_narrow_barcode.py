"""Preview only: half-width barcode bed from the sharper reference."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'work/preview_ps1_matrix_revision.py').read_text(encoding='utf-8')
namespace={'__file__':str(ROOT/'work/preview_ps1_matrix_revision.py')}
exec(compile(source.split("revised=''.join(parts)")[0],'previous-preview','exec'),namespace)
previous=''.join(namespace['parts'])
source=source.replace('sector(77,192,19.62,21.9)','sector(77,192,20.75,21.9)')
source=source.replace('19.83,21.65','20.87,21.76')
start=source.index('# Connected outline hexagons')
end=source.index('for r in (19.58,21.93)',start)
source=source[:start]+'''# Eight linked circular targets, then a pair and a single target.
groups=[[212+4.2*i for i in range(8)],[249.8,254.0],[262.4]]
for group in groups:
 centres=[polar(20.72,a) for a in group]
 for (x,y),(xx,yy) in zip(centres,centres[1:]):
  dx,dy=xx-x,yy-y;length=math.hypot(dx,dy);ux,uy=dx/length,dy/length
  parts.append(f'<path fill="none" stroke="#202024" stroke-width=".045" d="M{x+ux*.28},{y+uy*.28} L{xx-ux*.28},{yy-uy*.28}"/>')
 for angle,(cx,cy) in zip(group,centres):
  a=math.radians(angle)
  parts.append(f'<circle cx="{cx}" cy="{cy}" r=".28" fill="none" stroke="#202024" stroke-width=".055"/>')
  for offset in (0,math.pi/2,math.pi,3*math.pi/2):
   t=a+offset
   parts.append(f'<path stroke="#202024" stroke-width=".045" d="M{cx+.28*math.cos(t)},{cy+.28*math.sin(t)} L{cx+.49*math.cos(t)},{cy+.49*math.sin(t)}"/>')
''' + source[end:]
line="current=(ROOT/'outputs/branding-source/ps1-mastering-ring.svg').read_text(encoding='utf-8').split('>',1)[1].rsplit('</svg>',1)[0]"
source=source.replace(line,'current=previous')
source=source.replace('PS1 SILVER RING — REVISED DETAIL PREVIEW','PS1 SILVER RING — NARROWER BARCODE PREVIEW')
source=source.replace('>Current</text>','>Previous preview</text>')
source=source.replace('OCR font + Revised barcode and symbols','Half-width barcode strip')
source=source.replace('OCR lettering · Dark barcode bed with a gap · Linked outline symbols · Heavier boundary lines','Outer half-width barcode strip · Silver gap next to the black hub · Circular target symbols: 8 + 2 + 1')
source=source.replace('ps1-ring-revised-details-preview','ps1-ring-narrow-barcode-preview')
exec(compile(source,'narrow-barcode-preview','exec'),{'__file__':str(ROOT/'work/preview_ps1_matrix_revision.py'),'previous':previous})
