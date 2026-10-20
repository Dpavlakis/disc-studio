"""Deterministic cleanup of the supplied uniform 1280px optical-disc template.
No generation, OCR, recoloring or text replacement. Radial alignment uses bilinear
sampling; untouched source content is retained apart from this small remapping.
"""
from pathlib import Path
from PIL import Image, PngImagePlugin
import argparse, numpy as np, csv, hashlib, os, concurrent.futures, json, time

VERSION='ps2-label-annulus-v1'
ap=argparse.ArgumentParser();ap.add_argument('--source',required=True);ap.add_argument('--report',required=True)
ap.add_argument('--apply',action='store_true');ap.add_argument('--samples');args=ap.parse_args()
root=Path(args.source).resolve(); report=Path(args.report).resolve()
assert root.is_dir() and root.name=='Disc','Expected the explicitly selected Disc folder'
files=sorted(root.rglob('*.png'))
S=1280; cy=cx=639.5
yy,xx=np.mgrid[:S,:S].astype(np.float32);dx=xx-cx;dy=yy-cy;rr=np.hypot(dx,dy)
target_inner=S*.095;target_outer=S*(.0587/.12)
source_inner=129.0;source_outer=610.0
sr=source_inner+(rr-target_inner)*(source_outer-source_inner)/(target_outer-target_inner)
factor=sr/np.maximum(rr,1);sx=np.clip(cx+dx*factor,0,S-1.001);sy=np.clip(cy+dy*factor,0,S-1.001)
x0=sx.astype(np.int32);y0=sy.astype(np.int32);wx=sx-x0;wy=sy-y0
weights=[((1-wx)*(1-wy))[...,None],(wx*(1-wy))[...,None],((1-wx)*wy)[...,None],(wx*wy)[...,None]]
alpha=np.uint8(np.clip(np.minimum(rr-target_inner,target_outer-rr)+.5,0,1)*255)
mask=alpha>0

def clean(path,destination=None):
 assert path.resolve().is_relative_to(root),'Path outside selected folder'
 original=path.read_bytes();before=hashlib.sha256(original).hexdigest()
 with Image.open(path) as im:
  if im.info.get('ps2_disc_studio_cleanup')==VERSION:
   return {'file':str(path.relative_to(root)),'status':'already-cleaned','original_sha256':before,'cleaned_sha256':before}
  if im.size!=(S,S):raise ValueError(f'Unexpected size {im.size}')
  src=np.asarray(im.convert('RGBA'));icc=im.info.get('icc_profile')
 result=np.zeros_like(src,dtype=np.float32)
 for (xs,ys),weight in zip([(x0,y0),(x0+1,y0),(x0,y0+1),(x0+1,y0+1)],weights):
  result+=src[ys,xs]*weight
 result=np.rint(result).clip(0,255).astype(np.uint8)
 result[:,:,3]=np.minimum(result[:,:,3],alpha)
 result[~mask,:3]=0
 image=Image.fromarray(result)
 metadata=PngImagePlugin.PngInfo();metadata.add_text('ps2_disc_studio_cleanup',VERSION)
 metadata.add_text('cleanup','Deterministic radial alignment; no generated pixels or text replacement')
 target=destination or path
 target.parent.mkdir(parents=True,exist_ok=True)
 if destination is None:
  assert args.apply,'Overwrite requires --apply'
  assert path.resolve().is_relative_to(root)
 temporary=target.with_name(target.stem+'.codex-cleaning.tmp.png')
 try:
  image.save(temporary,format='PNG',compress_level=3,pnginfo=metadata,icc_profile=icc)
  with Image.open(temporary) as check:
   check.load();assert check.mode=='RGBA' and check.size==(S,S)
   assert check.getpixel((0,0))[3]==0 and check.getpixel((640,640))[3]==0
   assert np.array_equal(np.asarray(check),result),'Saved image differs from processed pixels'
  after=hashlib.sha256(temporary.read_bytes()).hexdigest()
  os.replace(temporary,target)
 finally:
  if temporary.exists():temporary.unlink()
 return {'file':str(path.relative_to(root)),'status':'cleaned','original_sha256':before,'cleaned_sha256':after}

if args.samples:
 dest=Path(args.samples); picks=[0,100,400,800,1200,1700,1800,1823]
 for idx in picks:
  path=files[min(idx,len(files)-1)];clean(path,dest/path.name)
 print('Created',len(picks),'sample textures; original files unchanged',flush=True)
elif args.apply:
 report.parent.mkdir(parents=True,exist_ok=True)
 start=time.time();counts={};rows=[]
 with report.open('w',newline='',encoding='utf-8-sig') as f:
  writer=csv.DictWriter(f,fieldnames=['file','status','original_sha256','cleaned_sha256','error']);writer.writeheader()
  def attempt(path):
   try:return clean(path)
   except Exception as e:return {'file':str(path.relative_to(root)),'status':'error','error':str(e)}
  with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
   for i,row in enumerate(pool.map(attempt,files),1):
    writer.writerow(row);f.flush();counts[row['status']]=counts.get(row['status'],0)+1
    if i%50==0 or i==len(files):print(json.dumps({'done':i,'total':len(files),'counts':counts,'seconds':round(time.time()-start)}),flush=True)
 print('Complete:',json.dumps(counts),flush=True)
else:print('Use --samples to inspect results or --apply to overwrite the selected library.')
