"""Package only the disc viewer/models for static hosting; omit artwork samples."""
from pathlib import Path
import re,json,shutil
root=Path(__file__).resolve().parents[1]
source=(root/'outputs'/'studio.html').read_text(encoding='utf-8')
model_files=sorted((root/'outputs').glob('*.glb'))
model_urls={p.stem:'models/'+p.name for p in model_files}
start=source.index('const models=')+len('const models=')
end=source.index('; const v=',start)
page=source[:start]+json.dumps(model_urls)+source[end:]
page=page.replace("'data:model/gltf-binary;base64,'+models[","models[")
dest=root/'outputs'/'site'
(dest/'models').mkdir(parents=True,exist_ok=True)
(dest/'index.html').write_text(page,encoding='utf-8')
(dest/'.nojekyll').write_text('')
for p in model_files:shutil.copy2(p,dest/'models'/p.name)
assert '007-from-russia' not in page
assert 'data:model/gltf-binary;base64,' not in page
print('Static site prepared:',dest,'with',len(model_files),'models and no example game artwork')
