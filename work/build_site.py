"""Build the hosted studio from approved assets without rebuilding native models."""
from pathlib import Path
import ast,base64,gzip,hashlib,json,re,shutil
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'outputs'
DEST=SOURCE/'site'

def build():
 DEST.mkdir(parents=True,exist_ok=True)
 assets=DEST/'assets';assets.mkdir(exist_ok=True)
 used=set()
 def publish(path):
  data=path.read_bytes();name=hashlib.sha256(data).hexdigest()[:16]+path.suffix.lower()
  target=assets/name
  if not target.exists():target.write_bytes(data)
  used.add(name);return 'assets/'+name
 tree=ast.parse((ROOT/'work/package.py').read_text(encoding='utf-8'))
 values={}
 for node in tree.body:
  if isinstance(node,ast.Assign):
   for target in node.targets:
    if isinstance(target,ast.Name) and target.id in ['html','header_cuts']:
     try:values[target.id]=ast.literal_eval(node.value)
     except (ValueError,TypeError):pass
 html=values['html']
 def compressed_model(path):
  data=gzip.compress(path.read_bytes(),compresslevel=6,mtime=0)
  name=hashlib.sha256(data).hexdigest()[:16]+'.gz'
  (assets/name).write_bytes(data);used.add(name)
  return 'gzip-url:assets/'+name
 models={p.stem:compressed_model(p) for p in sorted((SOURCE/'optimized-models').glob('*.glb'))}
 assert len(models)==12
 presets=json.loads((SOURCE/'lighting/environments.json').read_text(encoding='utf-8'))
 lightmaps={str(i):publish(SOURCE/'lighting'/f'{i}-softbox.hdr') for i in range(1,5)}
 for key,preset in presets.items():lightmaps[key]=publish(SOURCE/'lighting'/preset['webLighting']['file'])
 backgrounds={key:publish(SOURCE/'lighting'/preset['background']['file']) for key,preset in presets.items()}
 headers={key:{'url':publish(SOURCE/'xbox360-headers'/f'{key}.png'),'cut':cut} for key,cut in values['header_cuts'].items()}
 def script(name):return (ROOT/'work'/name).read_text(encoding='utf-8')
 environment=script('environment_controls.js').replace('LIGHTMAPS',json.dumps(lightmaps)).replace('BACKGROUNDS',json.dumps(backgrounds)).replace('ENVIRONMENT_PRESETS',json.dumps(presets))
 header=script('xbox360_headers.js').replace('XBOX_HEADERS',json.dumps(headers)).replace('XBOX_DEFAULT_ART',json.dumps(publish(SOURCE/'default-labels/x360.png')))
 gc=script('gamecube_label_controls.js').replace('GC_BRANDING_ASSETS',(SOURCE/'branding-source/gamecube-label/assets.json').read_text(encoding='utf-8'))
 html=re.sub(r'<header>.*?</header>',lambda _:script('studio_header.html'),html,count=1,flags=re.S)
 html=html.replace('<div class="disc-viewport">','<div class="disc-viewport"><div class="stage-help">Drag to rotate<span>·</span>Scroll to zoom<span>·</span>Middle-drag: disc rotation<span>·</span>Right-drag: pan</div>')
 html=html.replace('<script>const models=','<style>'+script('studio.css')+'</style><script>const models=')
 replacements={'MODELS':json.dumps(models),'MODEL_LOADING_SCRIPT':script('model_loading.js'),'ENVIRONMENT_CONTROLS_SCRIPT':environment,'DISC_OBJECT_ROTATION_SCRIPT':script('disc_object_rotation.js'),'XBOX_HEADER_SCRIPT':header,'PS1_LABEL_CONTROLS_SCRIPT':script('ps1_label_controls.js'),'GAMECUBE_LABEL_SCRIPT':gc,'ARTWORK_CONTROLS_SCRIPT':script('artwork_controls.js')}
 for token,value in replacements.items():html=html.replace(token,value)
 # Artwork and console marks that remain embedded in source become cached files.
 def externalize(match):
  mime,payload=match.groups();suffix={'image/png':'.png','image/svg+xml':'.svg','image/jpeg':'.jpg'}[mime]
  data=base64.b64decode(payload);name=hashlib.sha256(data).hexdigest()[:16]+suffix
  (assets/name).write_bytes(data);used.add(name);return 'assets/'+name
 html=re.sub(r'data:(image/(?:png|svg\+xml|jpeg));base64,([A-Za-z0-9+/=]+)',externalize,html)
 for token in replacements:assert token not in html,token
 assert 'id="export"' not in html and 'v.exportScene(' not in html
 assert 'value="living-room" selected' in html and "chooseSystem('ps1');" in html
 # Drop only stale generated files inside this builder's exact asset directory.
 for p in assets.iterdir():
  if p.is_file() and p.name not in used:p.unlink()
 (DEST/'index.html').write_text(html,encoding='utf-8')
 (DEST/'.nojekyll').write_text('')
 shutil.copy2(SOURCE/'lighting/ENVIRONMENT-CREDITS.txt',DEST/'ENVIRONMENT-CREDITS.txt')
 manifest={'files':{str(p.relative_to(DEST)).replace('\\','/'):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [DEST/'index.html',*sorted(assets.iterdir())]}}
 (DEST/'build-manifest.json').write_text(json.dumps(manifest,indent=2))
 assert (DEST/'index.html').stat().st_size<2_000_000
 assert sum(v['bytes'] for v in manifest['files'].values())<1_000_000_000
 print('Hosted studio:',(DEST/'index.html').stat().st_size,'byte page;',len(used),'lazy assets;',sum(v['bytes'] for v in manifest['files'].values()),'bytes total')
 return DEST
if __name__=='__main__':build()
