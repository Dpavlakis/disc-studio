const fs=require('fs'),vm=require('vm'),assert=require('assert');
const handlers={};let orbit={theta:Math.PI,phi:Math.PI/2,radius:.23},fov=35,target={x:0,y:.06,z:0},jumps=0,captured=null;
const v={loaded:true,style:{cursor:'grab'},updateComplete:Promise.resolve(),addEventListener(k,f){(handlers[k]??=[]).push(f)},getCameraOrbit:()=>orbit,getCameraTarget:()=>target,getFieldOfView:()=>fov,getBoundingClientRect:()=>({height:600}),setPointerCapture(id){captured=id},hasPointerCapture:id=>captured===id,releasePointerCapture(){captured=null},jumpCameraToGoal(){jumps++}};
vm.runInNewContext(fs.readFileSync('work/middle_mouse_pan.js','utf8'),{v,Math});
function event(button=1,x=0,y=0,id=4){return {button,clientX:x,clientY:y,pointerId:id,preventDefault(){this.prevented=true},stopImmediatePropagation(){this.stopped=true}}}
function fire(type,e){for(const f of handlers[type])f(e);return e}
function goal(){return v.cameraTarget.split(' ').map(parseFloat)}
(async()=>{
 for(const b of [0,2])assert(!fire('pointerdown',event(b)).prevented);
 assert(fire('pointerdown',event()).prevented);assert.equal(captured,4);assert.equal(v.style.cursor,'grabbing');fire('pointermove',event(1,100,60));await Promise.resolve();let p=goal();assert(p[0]>0);assert(p[1]>.06);assert(Math.abs(p[2])<1e-12);assert(jumps>0);
 const original=v.cameraTarget;fire('pointermove',event(1,200,0,9));assert.equal(v.cameraTarget,original);fire('pointerup',event());assert.equal(captured,null);assert.equal(v.style.cursor,'grab');fire('pointermove',event(1,500,0));assert.equal(v.cameraTarget,original);
 fov=10;fire('pointerdown',event());fire('pointermove',event(1,100,60));assert(goal()[0]<p[0]);fire('pointercancel',event());assert.equal(captured,null);
 orbit={theta:0,phi:Math.PI/2,radius:.23};fire('pointerdown',event());fire('pointermove',event(1,100,0));assert(goal()[0]<0);fire('lostpointercapture',event());
 assert(fire('auxclick',event()).prevented);assert(!fire('auxclick',event(2)).prevented);v.loaded=false;assert(!fire('pointerdown',event()).prevented);
 console.log('Verified middle-drag direction on both faces, zoom-scaled movement, pointer capture/cancel, browser autoscroll prevention and untouched left/right input.');
})().catch(e=>{console.error(e);process.exitCode=1});
