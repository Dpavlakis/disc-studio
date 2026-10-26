"""Fetch matching CC0 panoramas; keep HDR reflection lighting unchanged."""
import concurrent.futures,hashlib,io,json
from PIL import Image
from fetch_environments import DEST,get

def download(item):
 key,preset=item
 info=json.loads(get('https://api.polyhaven.com/files/'+preset['asset']))['tonemapped']
 payload=get(info['url'])
 assert hashlib.md5(payload).hexdigest()==info['md5']
 image=Image.open(io.BytesIO(payload)).convert('RGB')
 assert image.width>=8192 and image.width==image.height*2
 image=image.resize((8192,4096),Image.Resampling.LANCZOS)
 name=key+'-background.jpg'
 image.save(DEST/name,quality=90,subsampling=0,optimize=True)
 preset['background']={'file':name,'width':8192,'height':4096,'source':info['url'],'sha256':hashlib.sha256((DEST/name).read_bytes()).hexdigest()}
 print(key,(DEST/name).stat().st_size,flush=True)
 return key,preset

if __name__=='__main__':
 presets=json.loads((DEST/'environments.json').read_text())
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  presets=dict(pool.map(download,presets.items()))
 (DEST/'environments.json').write_text(json.dumps(presets,indent=2),encoding='utf-8')
 p=DEST/'ENVIRONMENT-CREDITS.txt'
 text=p.read_text(encoding='utf-8')
 text+='\nBackground panoramas: matching Poly Haven tonemapped photographs, resized to 8192 x 4096 (8K), JPEG quality 90. HDR lighting files unchanged.\n'
 p.write_text(text,encoding='utf-8')
