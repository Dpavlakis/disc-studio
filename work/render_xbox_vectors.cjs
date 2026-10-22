const fs=require('fs'),sharp=require('sharp');
(async()=>{
 for(const side of ['front','rear','contours']){
  await sharp(Buffer.from(fs.readFileSync(`work/xbox-vector-${side}.svg`,'utf8'))).resize(4096,4096).greyscale().png().toFile(`work/xbox-vector-${side}.png`);
 }
})().catch(e=>{console.error(e);process.exit(1)});
