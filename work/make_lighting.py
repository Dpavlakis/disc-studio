"""Generate small linear-HDR studio environments with 1–4 softboxes."""
from pathlib import Path
import numpy as np
out=Path(__file__).resolve().parents[1]/'outputs'/'lighting'
out.mkdir(exist_ok=True)
W,H=1024,512
lat=np.linspace(np.pi/2,-np.pi/2,H)[:,None]
lon=np.linspace(-np.pi,np.pi,W)[None,:]
positions=[(-45,30),(125,25),(45,45),(-135,20)]
for count in range(1,5):
 radiance=np.full((H,W,3),.035,dtype=float)
 radiance+=np.maximum(-np.sin(lat),0)[...,None]*.045
 for az,el in positions[:count]:
  dx=np.arctan2(np.sin(lon-np.deg2rad(az)),np.cos(lon-np.deg2rad(az)))
  dy=lat-np.deg2rad(el)
  box=np.exp(-((dx/np.deg2rad(12))**8+(dy/np.deg2rad(27))**8))
  radiance+=box[...,None]*(15/np.sqrt(count))
 maxc=radiance.max(axis=2);mant,exp=np.frexp(maxc)
 rgbe=np.zeros((H,W,4),dtype=np.uint8)
 rgbe[:,:,:3]=np.clip(radiance*(mant*256/maxc)[...,None],0,255).astype(np.uint8)
 rgbe[:,:,3]=(exp+128).astype(np.uint8)
 data=bytearray(b'#?RADIANCE\nFORMAT=32-bit_rle_rgbe\n\n-Y 512 +X 1024\n')
 for row in rgbe:
  data.extend([2,2,W>>8,W&255])
  for channel in range(4):
   values=row[:,channel];i=0
   while i<W:
    run=1
    while i+run<W and run<127 and values[i+run]==values[i]:run+=1
    if run>=4:data.extend([128+run,int(values[i])]);i+=run
    else:
     start=i;i+=1
     while i<W and i-start<128:
      if i+3<W and all(values[i:i+4]==values[i]):break
      i+=1
     data.append(i-start);data.extend(values[start:i].tobytes())
 (out/f'{count}-softbox.hdr').write_bytes(data)
print('Generated four HDR studio light setups')
