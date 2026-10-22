"""Compare existing ring typography with proportions measured from the scan."""
from pathlib import Path
import os,subprocess
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'work/make_ps1_matrix.py').read_text(encoding='utf-8').split("(ROOT/'outputs/branding-source/ps1-mastering-ring.svg')")[0]
def construct(code):
 ns={'__file__':str(ROOT/'work/make_ps1_matrix.py')};exec(compile(code,'ring-layout-preview','exec'),ns)
 return ns['svg'].split('>',1)[1].rsplit('</svg>',1)[0]
current=construct(source).replace('barcode-cutouts','current-barcode-cutouts')
proposed=source.replace("curved('PSRM-002320',324,.94)","curved('PSRM-002320',90,1.35)")
proposed=proposed.replace("curved('IFPI L331',24,.42,r=21.5)","curved('IFPI L331',158,.58,r=20.72)")
proposed=proposed.replace("curved('10',270,.8)","curved('10',49,1.2)")
proposed=proposed.replace('sector(77,192,','sector(205,301,').replace('cursor=83','cursor=213').replace('cursor<153','cursor<295').replace('119<cursor<122.4','250<cursor<253.4')
proposed=proposed.replace('[212+4.2*i for i in range(8)],[249.8,254.0],[262.4]','[345+4.2*i for i in range(8)],[382.8,387.0],[395.4]')
updated=construct(proposed).replace('barcode-cutouts','reference-barcode-cutouts')
parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1060" viewBox="0 0 1800 1060"><rect width="1800" height="1060" fill="#eceee9"/>',
 '<g font-family="Segoe UI,Arial,sans-serif" fill="#283129"><text x="50" y="55" font-size="29" font-weight="600">PS1 RING — REFERENCE TEXT SCALE &amp; POSITION</text>',
 '<text x="50" y="88" font-size="18" fill="#677366">Layout preview · Serial values retained · Text changes have not been applied</text>',
 '<text x="450" y="145" text-anchor="middle" font-size="24">Current placement</text><text x="1350" y="145" text-anchor="middle" font-size="24" font-weight="600">Reference placement and scale</text></g>']
for cx,marks in ((450,current),(1350,updated)):
 parts.append(f'<g transform="translate({cx},575) scale(18.4)"><circle r="22" fill="#b9bdb6"/><circle r="19.5" fill="#0a0d0e"/><circle r="7.5" fill="#465360"/>{marks}</g>')
parts.append('<text x="900" y="1030" font-family="Segoe UI,Arial,sans-serif" text-anchor="middle" fill="#677366" font-size="18">Larger serial on the right · IFPI below · Symbols above · Narrow barcode strip on the left</text></svg>')
(ROOT/'outputs/ps1-ring-reference-layout-preview.svg').write_text(''.join(parts),encoding='utf-8')
# Keep a candidate vector source for approval; the studio still uses its current layout.
(ROOT/'work/ps1-matrix-reference-layout-candidate.py').write_text(proposed,encoding='utf-8')
env=os.environ.copy();env['NODE_PATH']='C:/Users/dimit/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules'
subprocess.run(['node','-e',"require('sharp')('outputs/ps1-ring-reference-layout-preview.svg').png().toFile('outputs/ps1-ring-reference-layout-preview.png').catch(e=>{console.error(e);process.exit(1)})"],cwd=ROOT,env=env,check=True)
print('Saved reference-layout preview; no typography changes applied to the model.')
