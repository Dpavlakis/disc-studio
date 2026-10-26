from pathlib import Path
import re,base64
root=Path(__file__).resolve().parents[1]
out=root/'mockups/menu-polish';out.mkdir(parents=True,exist_ok=True)
header=(root/'work/studio_header.html').read_text(encoding='utf-8')
header=header.replace('class="studio-brand"','class="studio-brand"').replace('<h1>Disc Studio</h1>','<h1>Disc Studio</h1>')
header=re.sub(r'(<button type="button" data-system="([^"]+)"[^>]*>)(.*?)(</button>)',lambda m:m[1]+m[3]+'<span>'+{'ps1':'PlayStation','ps2':'PS2','ps3':'PS3','ps4':'PS4','xbox':'Xbox','xbox360':'Xbox 360','gamecube':'GameCube'}[m[2]]+'</span>'+m[4],header)
header=re.sub(r'<p id="system-context".*?</p>','<p id="system-context">GameCube <span>80 mm mini disc</span></p>',header)
header=header.replace('Console &amp; finish','Console').replace('Printed artwork','Artwork').replace('Light &amp; reflection','Lighting').replace('Choose artwork','Upload artwork').replace('Save transparent PNG','Save PNG <span aria-hidden="true">↓</span>')
header=header.replace('Loading your disc…','Transparent background · PNG')
# Keep only the first two sections open in the review.
header=re.sub(r'<details class="control-section"', '<details class="control-section"',header)
images={k:'data:image/png;base64,'+base64.b64encode((root/'outputs/default-labels'/f'{v}.png').read_bytes()).decode() for k,v in {'ps1':'ps1','ps2':'ps2','ps3':'ps3','ps4':'ps4','xbox':'xbox','xbox360':'x360','gamecube':'gc'}.items()}
css='''
:root{--panel:#181c21;--line:#30363e;--text:#eef1ed;--muted:#a0a8af;--accent:#d0ef9b}
body{grid-template-columns:354px minmax(0,1fr);background:#e4e2dc}
.studio-panel{width:354px;padding:25px 22px 0;display:flex;flex-direction:column;background:#181c21;box-shadow:8px 0 32px #00000009}
.studio-brand{margin-bottom:25px;gap:12px}.disc-mark{width:34px;height:34px}.disc-mark:after{inset:11px}h1{font-size:23px;letter-spacing:-.8px}.brand-subtitle{font-size:11px;color:#a0a8af;margin:5px 0 0}
.studio-panel .control-section{flex-shrink:0}.studio-panel .control-section>summary{padding:19px 0}.studio-panel .control-section>summary h2 span{font-size:13px;letter-spacing:0;font-weight:600}
.studio-panel .system-nav{grid-template-columns:repeat(4,minmax(0,1fr));gap:7px}
.studio-panel .system-nav button{height:76px;min-height:76px;border-radius:10px;background:#21262c;border-color:#353b42;padding:10px 3px;gap:6px}
.studio-panel .system-nav button img{height:29px;width:38px;opacity:.75}.studio-panel .system-nav button span{font-size:10px;color:#c1c7cb;white-space:nowrap}
.studio-panel .system-nav button[aria-pressed=true]{background:#d0ef9b;border-color:#d0ef9b;box-shadow:0 0 0 2px #d0ef9b16}.studio-panel .system-nav button[aria-pressed=true] img{filter:brightness(0);opacity:.9}.studio-panel .system-nav button[aria-pressed=true] span{color:#26301d;font-weight:600}
.studio-panel #system-context{display:flex;justify-content:space-between;font-size:12px;font-weight:600;margin:17px 0 11px;color:#e1e6e2}.studio-panel #system-context span{font-size:11px;font-weight:400;color:#929ba3}
.studio-panel [data-finish]{text-align:left;border-radius:8px;font-size:11px;min-height:36px;margin:0 0 6px}
.studio-panel .upload-control{border:1px dashed #5b6654;background:#262e24;border-radius:9px;min-height:61px;padding:15px;color:#e6efd9;font-size:12px}.studio-panel .upload-control span{font-size:9px;color:#a1ae91}
.studio-panel select{min-height:39px;border-radius:8px;background:#22272d;color:#d5dbe0;border-color:#394149;font-size:12px}.studio-panel .check-control{font-size:12px;color:#c1c9cd}.studio-panel input[type=range]{accent-color:#d0ef9b;height:4px}.studio-panel .angle-number input{background:#22272d;border-radius:7px;width:70px}
.studio-panel .environment-hint{color:#929ca4;font-size:11px}.studio-panel .art-angle-control{margin-top:16px}.studio-panel .button-row button{border-radius:7px;background:#22272d;border-color:#394149}.studio-panel .export-section{position:sticky;bottom:0;margin-top:auto;padding:18px 0 11px;background:#181c21;border-top:1px solid #343b42;box-shadow:0 -15px 18px #181c21;flex-shrink:0}
.studio-panel .primary-action{display:flex;justify-content:center;gap:100px;align-items:center;width:100%;min-height:44px;border:0;border-radius:9px;background:#d0ef9b;color:#243019;font-size:13px;font-weight:600}.studio-panel #status{margin:9px 0 0;text-align:center;font-size:10px;color:#949e91;min-height:16px}
.mock-stage{position:relative;display:flex;align-items:center;justify-content:center;min-width:0;height:100dvh;background:radial-gradient(ellipse at 50% 40%,#f4f2ec,#deddd6);overflow:hidden;color:#303935}
.stage-top{position:absolute;inset:28px 30px auto;display:flex;align-items:center;justify-content:space-between;font-size:12px;color:#707873}.stage-top b{font-size:13px;font-weight:500;color:#414b44}.mock-badge{border:1px solid #bfc6b9;border-radius:20px;padding:6px 10px;font-size:10px;letter-spacing:.2px}
.disc-demo{position:relative;width:min(68%,620px);aspect-ratio:1;border-radius:50%;box-shadow:0 1px 0 2px #aaa99e,0 2px 0 4px #f5f5ed,18px 30px 54px #34412b22;transform:rotate(-7deg);overflow:hidden;transition:transform .25s}
.disc-demo img{width:100%;height:100%;object-fit:cover}.hub{position:absolute;inset:40%;border-radius:50%;background:#d9d8cfda;border:1px solid #aaa99e;box-shadow:inset 0 0 0 6px #ffffff2b,inset 0 0 0 8px #aaa99e33}.hub:after{content:'';position:absolute;inset:25%;border:1px solid #a6a79d;border-radius:50%;background:#e8e7e0}
.stage-toolbar{position:absolute;bottom:32px;display:flex;gap:5px;padding:6px;background:#f6f6f0e6;border:1px solid #c9cec3;border-radius:12px;box-shadow:0 8px 24px #33412b0b}.stage-toolbar button{border:0;background:transparent;color:#586250;font-size:12px;padding:9px 19px;border-radius:7px}.stage-toolbar button[aria-pressed=true]{background:#e2e7db;color:#25341d}.stage-help-mock{position:absolute;bottom:100px;color:#7a8278;font-size:11px}
[hidden]{display:none!important}@media(max-width:850px){body{grid-template-columns:310px minmax(0,1fr)}.studio-panel{width:310px;padding:22px 17px 0}.disc-demo{width:82%}}@media(max-width:620px){body{display:flex;flex-direction:column}.mock-stage{order:-1;height:43vh;min-height:280px}.studio-panel{width:100%;height:auto;overflow:visible}.disc-demo{width:48%;max-width:260px}.stage-toolbar{bottom:12px}.stage-top{inset:15px 16px auto}.stage-help-mock{display:none}.studio-panel .system-nav{grid-template-columns:repeat(4,1fr)}.studio-panel .export-section{margin-top:20px}}
@media(prefers-reduced-motion:reduce){.disc-demo{transition:none}}
'''
js='''const art=IMAGES;let selected='gamecube',uploaded=null;const image=document.querySelector('.disc-demo img');const label=document.getElementById('stage-console');const names={ps1:'PlayStation',ps2:'PlayStation 2',ps3:'PlayStation 3',ps4:'PlayStation 4',xbox:'Xbox',xbox360:'Xbox 360',gamecube:'GameCube'};
function select(key){selected=key;uploaded=null;image.src=art[key];label.textContent=names[key];document.getElementById('system-context').innerHTML=names[key]+'<span>'+(key==='gamecube'?'80 mm mini disc':'120 mm disc')+'</span>';document.querySelectorAll('[data-system]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.system===key)));document.querySelectorAll('[data-platform]').forEach(b=>b.hidden=b.dataset.platform!==key||b.dataset.reference==='true');document.querySelector('.gamecube-label-section')?.removeAttribute('open');}
document.querySelectorAll('[data-system]').forEach(b=>b.onclick=()=>select(b.dataset.system));document.querySelectorAll('[data-finish]').forEach(b=>b.onclick=()=>{document.querySelectorAll('[data-finish]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));});
document.getElementById('download-png').disabled=false;document.getElementById('download-png').onclick=()=>{const a=document.createElement('a');a.href=uploaded||art[selected];a.download='menu-concept-'+selected+'.png';a.click()};
document.getElementById('art').onchange=e=>{if(!e.target.files[0])return;const reader=new FileReader();reader.onload=()=>{uploaded=reader.result;image.src=uploaded};reader.readAsDataURL(e.target.files[0]);};
document.querySelectorAll('.stage-toolbar button').forEach((b,i)=>b.onclick=()=>{document.querySelectorAll('.stage-toolbar button').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));document.querySelector('.disc-demo').style.transform=i===1?'rotate(-7deg) rotateY(30deg)':'rotate('+ (i===2?0:-7)+'deg)';});
document.getElementById('show-art').onchange=e=>image.style.visibility=e.target.checked?'visible':'hidden';
select('gamecube');'''
import json
html='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Disc Studio · Menu concept</title><style>'+(root/'work/studio.css').read_text(encoding='utf-8')+css+'</style><body>'+header+'''<main class="mock-stage"><div class="stage-top"><b id="stage-console">GameCube</b><span class="mock-badge">Menu concept</span></div><div class="disc-demo"><img alt="Starter cover preview"><span class="hub"></span></div><nav class="stage-toolbar" aria-label="Preview angle"><button aria-pressed="true">Front</button><button aria-pressed="false">Angle</button><button aria-pressed="false">Fit</button></nav></main>'''+ '<script>'+js.replace('IMAGES',json.dumps(images))+'</script></body></html>'
(out/'review.html').write_text(html,encoding='utf-8')
print(out/'review.html')
