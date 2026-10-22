"""Separate editable panel and reflective branding overlay; preserve disc body."""
from pathlib import Path
import json,struct,math,copy,os,subprocess
import numpy as np
root=Path(__file__).resolve().parents[1]/'outputs';assets=json.loads((root/'branding-source/gamecube-label/assets.json').read_text())
def insert(key,x,y,w,h):
 svg=assets[key];return '<svg x="%s" y="%s" width="%s" height="%s" '%(x,y,w,h)+svg.split('<svg ',1)[1]
clip='<defs><clipPath id="disc"><path fill-rule="evenodd" d="M1266.4,640 A626.4,626.4 0 1,0 13.6,640 A626.4,626.4 0 1,0 1266.4,640 M824,640 A184,184 0 1,0 456,640 A184,184 0 1,0 824,640"/></clipPath></defs>'
prefix='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 1280">'+clip+'<g clip-path="url(#disc)">'
panel=prefix+'<rect x="0" y="770" width="1280" height="510" fill="white"/></g></svg>'
foil=prefix+insert('logo',390,850,520,130)+insert('seal',128,825,230,177)+insert('rating-e',937,793,161,224)+'<g fill="white" font-family="Arial" text-anchor="middle"><rect x="298" y="1058" width="688" height="48" fill="none" stroke="white" stroke-width="3"/><text x="642" y="1090" font-size="20">FOR USE ONLY IN USA, CANADA, MEXICO AND LATIN AMERICA</text><text x="640" y="1150" font-size="31">DL • DOL • GZWE • USA</text><path id="model" d="M435,1190 Q640,1280 845,1190" fill="none"/><text font-size="30"><textPath href="#model" startOffset="50%">MODEL No. DOL-006(USA)</textPath></text></g></g></svg>'
for name,svg in [('panel',panel),('foil',foil)]:
 (root/f'branding-source/gamecube-label/default-{name}.svg').write_text(svg,encoding='utf-8')
env=os.environ.copy();env['NODE_PATH']='C:/Users/dimit/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules'
for name in ['panel','foil']:
 subprocess.run(['node','-e',f"require('sharp')('outputs/branding-source/gamecube-label/default-{name}.svg').resize(8192,8192).png().toFile('outputs/gamecube-label-{name}.png').catch(e=>{{console.error(e);process.exit(1)}})"],cwd=root.parent,env=env,check=True)
raw=(root/'gamecube-disc.glb').read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);blob=bytearray(raw[28+n:])
if any(m['name']=='GAMECUBE_LABEL_FOIL' for m in g['materials']):print('Layer already exists.');raise SystemExit
def view(data):
 while len(blob)%4:blob.append(0)
 g['bufferViews'].append({'buffer':0,'byteOffset':len(blob),'byteLength':len(data)});blob.extend(data);return len(g['bufferViews'])-1
def acc(a):
 a=np.array(a,dtype='<f4');g['accessors'].append({'bufferView':view(a.tobytes()),'componentType':5126,'count':len(a),'type':'VEC'+str(a.shape[1]),'min':a.min(axis=0).tolist(),'max':a.max(axis=0).tolist()});return len(g['accessors'])-1
for name,y in [('panel',.00105),('foil',.00108)]:
 g['images'].append({'bufferView':view((root/f'gamecube-label-{name}.png').read_bytes()),'mimeType':'image/png'});g['textures'].append({'source':len(g['images'])-1,'sampler':0});tex=len(g['textures'])-1
 if name=='foil':
  mat=copy.deepcopy(next(m for m in g['materials'] if m['name']=='GAMECUBE_SILVER_DATA_UNDERSIDE'));mat['name']='GAMECUBE_LABEL_FOIL';mat['pbrMetallicRoughness']['baseColorTexture']={'index':tex}
 else:mat={'name':'GAMECUBE_LABEL_PANEL','pbrMetallicRoughness':{'baseColorFactor':[0,0,0,1],'baseColorTexture':{'index':tex},'metallicFactor':0,'roughnessFactor':.36}}
 mat['alphaMode']='MASK';mat['alphaCutoff']=.4;g['materials'].append(mat);material=len(g['materials'])-1
 p=[];uv=[]
 for i in range(1024):
  for r,k in [(.03915,i),(.0115,i),(.0115,i+1),(.03915,i),(.0115,i+1),(.03915,i+1)]:
   a=math.tau*k/1024;x=r*math.cos(a);z=r*math.sin(a);p.append((x,y,z));uv.append((.5-x/.08,.5-z/.08))
 attrs={'POSITION':acc(p),'NORMAL':acc([(0,1,0)]*len(p)),'TEXCOORD_0':acc(uv),'TANGENT':acc([(1,0,0,-1)]*len(p))}
 g['meshes'].append({'name':mat['name'],'primitives':[{'attributes':attrs,'material':material}]});g['nodes'].append({'name':mat['name'],'mesh':len(g['meshes'])-1,'rotation':[-math.sqrt(.5),0,0,math.sqrt(.5)],'translation':[0,.06,0]});g['scenes'][0]['nodes'].append(len(g['nodes'])-1)
g['buffers'][0]['byteLength']=len(blob);g['extras']['editableGameCubeBranding']=True
j=json.dumps(g,separators=(',',':')).encode();j+=b' '*((-len(j))%4)
(root/'gamecube-disc.glb').write_bytes(struct.pack('<III',0x46546c67,2,28+len(j)+len(blob))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(blob),0x004e4942)+blob)
# Review sheet uses the same native SVG masks as the actual layer.
preview='<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="550" viewBox="0 0 1280 550"><rect width="1280" height="850" fill="#e9ece6"/><text x="40" y="52" font-family="Arial" font-size="28" fill="#26312b">GAMECUBE — REUSABLE BRANDING LAYER</text><text x="40" y="88" font-family="Arial" font-size="19" fill="#667366">Two seal wordings · Fixed traced logo · E / T ratings · Editable four-character code · Panel colour</text>'
for x,color,seal,rating,code in [(15,'#090909','quality','rating-t','GAHE'),(655,'#263d9b','seal','rating-e','GZWE')]:
 content=insert('logo',390,850,520,130)+insert(seal,128,825,230,177)+insert(rating,937,793,161,224)
 preview+=f'<g transform="translate({x},-260) scale(.48)"><circle cx="640" cy="640" r="626" fill="#a6aaa6"/><g clip-path="url(#disc)"><rect x="0" y="770" width="1280" height="510" fill="{color}"/>{content}<g fill="#d8ddd5" font-family="Arial" text-anchor="middle"><rect x="298" y="1058" width="688" height="48" fill="none" stroke="#d8ddd5" stroke-width="3"/><text x="642" y="1090" font-size="20">FOR USE ONLY IN USA, CANADA, MEXICO AND LATIN AMERICA</text><text x="640" y="1150" font-size="31">DL • DOL • {code} • USA</text><text x="640" y="1220" font-size="29">MODEL No. DOL-006(USA)</text></g></g></g>'
preview+='<rect x="0" y="0" width="1280" height="100" fill="#e9ece6"/><text x="40" y="42" font-family="Arial" font-size="28" fill="#26312b">GAMECUBE — REUSABLE BRANDING LAYER</text><text x="40" y="78" font-family="Arial" font-size="19" fill="#667366">Two seals · Fixed logo · E / T ratings · Editable code · Panel colour</text>'+clip+'<text x="40" y="420" font-family="Arial" font-size="21" fill="#26312b">Seal of Quality / Teen</text><text x="680" y="420" font-family="Arial" font-size="21" fill="#26312b">Seal / Everyone</text><text x="40" y="485" font-family="Arial" font-size="20" fill="#667366">Fixed elements rotate together. Foil is shown flat here; the studio supplies moving reflections.</text></svg>'
(root/'branding-source/gamecube-label/layer-preview.svg').write_text(preview,encoding='utf-8')
subprocess.run(['node','-e',"require('sharp')('outputs/branding-source/gamecube-label/layer-preview.svg').png().toFile('outputs/gamecube-branding-layer-preview.png')"],cwd=root.parent,env=env,check=True)
print('Added independent panel and rainbow foil meshes; generated branding review sheet.')
