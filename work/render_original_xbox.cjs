const fs=require('fs'),sharp=require('sharp');
(async()=>{
 for(const [file,target] of [['xbox-original-symbol.svg','symbol'],['xbox-original-wordmark.svg','wordmark']]){
  let svg=fs.readFileSync('outputs/branding-source/'+file,'utf8');
  svg=svg.replace('</svg>','<style>path{fill:#ffffff!important;fill-opacity:1!important;stroke:none!important}circle{display:none!important}</style></svg>');
  await sharp(Buffer.from(svg),{density:300}).resize({width:1200}).png().toFile('work/xbox-original-'+target+'.png');
 }
})().catch(e=>{console.error(e);process.exit(1)});
