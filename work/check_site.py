"""Check the hosted bundle references only included public assets."""
from pathlib import Path
import gzip,hashlib,json,re
root=Path(__file__).resolve().parents[1]/'outputs/site'
html=(root/'index.html').read_text(encoding='utf-8')
manifest=json.loads((root/'build-manifest.json').read_text())['files']
for name,entry in manifest.items():
 p=root/name
 assert p.is_file() and p.stat().st_size==entry['bytes']
 assert hashlib.sha256(p.read_bytes()).hexdigest()==entry['sha256']
for name in set(re.findall(r'assets/[a-f0-9]{16}\.[a-z0-9]+',html)):assert (root/name).is_file(),name
models=json.loads(html.split('<script>const models=',1)[1].split('; const v=',1)[0])
assert len(models)==12
for name,value in models.items():
 assert value.startswith('gzip-url:assets/')
 payload=(root/value[9:]).read_bytes()
 source=(root.parent/'optimized-models'/f'{name}.glb').read_bytes()
 assert gzip.decompress(payload)==source
 assert len(payload)<len(source)*.8
assert 'id="export"' not in html and 'v.exportScene(' not in html
assert 'id="download-png"' in html
assert 'value="living-room" selected' in html and "chooseSystem('ps1');" in html
assert len(html.encode())<2_000_000
assert not any(p.suffix in {'.zip','.py','.git'} for p in root.rglob('*'))
print('Hosted assets, hashes, all 12 lazy models, PNG-only controls and approved defaults verified.')
