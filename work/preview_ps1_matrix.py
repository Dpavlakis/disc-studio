"""Preview thicker PS1 mastering marks without changing studio assets."""
from pathlib import Path
import os,subprocess

ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'work/make_ps1_matrix.py').read_text(encoding='utf-8')
# Evaluate only the vector construction, before its asset-writing stage.
source=source.split("(ROOT/'outputs/branding-source/ps1-mastering-ring.svg')")[0]
def construct(code):
 namespace={'__file__':str(ROOT/'work/make_ps1_matrix.py')}
 exec(compile(code,'matrix-preview-source','exec'),namespace)
 return namespace['svg'].split('>',1)[1].rsplit('</svg>',1)[0]
current=construct(source)
thicker=source.replace('width=(.14,.24,.18,.33,.12,.20,.28)[i%7]','width=1.6*(.14,.24,.18,.33,.12,.20,.28)[i%7]')
thicker=thicker.replace('width+(.18,.25,.13,.20,.16)[i%5]','width+1.8*(.18,.25,.13,.20,.16)[i%5]')
thicker=thicker.replace('stroke-width=".045"','stroke-width=".08"').replace('stroke-width=".035"','stroke-width=".09"')
thicker=thicker.replace('fill-rule="evenodd"','stroke="#202024" stroke-width=".022" stroke-linejoin="round" paint-order="stroke fill" fill-rule="evenodd"')
proposed=construct(thicker)
parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1060" viewBox="0 0 1800 1060">',
 '<rect width="1800" height="1060" fill="#eceee9"/>',
 '<g font-family="Segoe UI,Arial,sans-serif" fill="#283129"><text x="50" y="55" font-size="29" font-weight="600">PS1 SILVER RING — STROKE PREVIEW</text>',
 '<text x="50" y="88" font-size="18" fill="#677366">Preview only · The studio has not been changed.</text>',
 '<text x="450" y="145" text-anchor="middle" font-size="24">Current</text>',
 '<text x="1350" y="145" text-anchor="middle" font-size="24" font-weight="600">Thicker lines</text></g>']
for cx,marks in ((450,current),(1350,proposed)):
 parts.append(f'<g transform="translate({cx},575) scale(18.4)"><circle r="22" fill="#b9bdb6"/><circle r="19.5" fill="#0a0d0e"/><circle r="7.5" fill="#465360"/>{marks}</g>')
parts.append('<text x="900" y="1030" font-family="Segoe UI,Arial,sans-serif" text-anchor="middle" fill="#677366" font-size="19">Wider barcode bars and spacing · Heavier ring outlines and symbols · Slightly bolder lettering</text></svg>')
output=ROOT/'outputs/ps1-ring-thicker-lines-preview.svg'
output.write_text(''.join(parts),encoding='utf-8')
env=os.environ.copy();env['NODE_PATH']='C:/Users/dimit/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules'
subprocess.run(['node','-e',"require('sharp')('outputs/ps1-ring-thicker-lines-preview.svg').png().toFile('outputs/ps1-ring-thicker-lines-preview.png').catch(e=>{console.error(e);process.exit(1)})"],cwd=ROOT,env=env,check=True)
print('Saved side-by-side preview; no studio assets changed.')
