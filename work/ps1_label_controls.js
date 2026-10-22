const ps1LabelStyle=document.getElementById('ps1-label-style');
function applyPS1LabelStyle(){
  if(activeSystem!=='ps1'||!v.model)return;
  const style=systemState.ps1.labelStyle||'silver';
  const face=v.model.materials.find(m=>m.name==='PS1_FRONT_MASTERING_FOIL');
  if(face){
    const p=face.pbrMetallicRoughness;
    p.setBaseColorFactor(style==='silver'?[.68,.68,.68,1]:[.9,.9,.9,1]);
    p.setMetallicFactor(style==='silver'?1:0);
    p.setRoughnessFactor(style==='silver'?.075:.34);
  }
  const marks=v.model.materials.find(m=>m.name==='PS1_MASTERING_MARKS');
  if(marks){
    marks.setAlphaMode(style==='silver'?'MASK':'BLEND');
    marks.pbrMetallicRoughness.setBaseColorFactor([1,1,1,style==='silver'?1:0]);
  }
  const centre=v.model.materials.find(m=>m.name==='PS1_CENTRE_PRINT');
  const outer=v.model.materials.find(m=>m.name==='TOP_ART_REPLACE_THIS_TEXTURE');
  if(centre&&outer){
    const enabled=style==='centre-print'&&showArt.checked;
    centre.pbrMetallicRoughness.baseColorTexture.setTexture(enabled?artTextures.get(outer)||outer.pbrMetallicRoughness.baseColorTexture.texture:null);
    centre.setAlphaMode(enabled?'MASK':'BLEND');
    centre.pbrMetallicRoughness.setBaseColorFactor(enabled?[1,1,1,1]:[1,1,1,0]);
  }
}
ps1LabelStyle.onchange=()=>{
  systemState.ps1.labelStyle=ps1LabelStyle.value;
  applyPS1LabelStyle();
  s.textContent=ps1LabelStyle.value==='silver'?'Silver face over the black disc.':ps1LabelStyle.value==='white'?'White face with an exposed black centre.':'Extra centre printing enabled. The black rings remain exposed.';
};
