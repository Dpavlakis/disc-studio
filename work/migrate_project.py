from pathlib import Path
import shutil,hashlib,json
src=Path(r'C:\Users\dimit\Documents\Codex\2026-10-20\can-you-create-me-a-3d-3').resolve();dst=Path('D:/Projects/Disc Studio').resolve()
assert src.name=='can-you-create-me-a-3d-3' and str(dst)==r'D:\Projects\Disc Studio';assert not any(dst.iterdir()),'Destination must be empty'
old_pages={'studio.html','disc-preview-next.html','disc-studio-clear-plastic.html','disc-studio-office.html',*[f'disc-studio-GC-{n:02}.html' for n in range(3,7)]}
excluded=[];copied=[]
def sha(f):
 h=hashlib.sha256()
 with f.open('rb') as stream:
  for chunk in iter(lambda:stream.read(8*1024*1024),b''):h.update(chunk)
 return h.hexdigest()
for p in src.rglob('*'):
 if not p.is_file():continue
 rel=p.relative_to(src)
 if '__pycache__' in rel.parts or rel.parts[:2]==('outputs','site') or (rel.parent==Path('outputs') and (rel.name in old_pages or p.suffix=='.zip')):
  excluded.append({'path':str(rel),'bytes':p.stat().st_size});continue
 target=dst/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
 digest=sha(p);assert digest==sha(target),str(rel);copied.append({'path':str(rel),'sha256':digest,'bytes':p.stat().st_size})
(dst/'work/migration-manifest.json').write_text(json.dumps({'source':str(src),'destination':str(dst),'verified_files':copied,'removed_generated_files':excluded},indent=2))
print('Copied and hash verified',len(copied),'files; omitted',round(sum(p['bytes'] for p in excluded)/1024**3,2),'GiB of generated files.')
