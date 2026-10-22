// Move the framing target in the camera's screen plane; geometry stays fixed.
let middleMousePan=null;
function stopMiddleMousePan(event){
 if(!middleMousePan||event&&event.pointerId!==undefined&&event.pointerId!==middleMousePan.id)return;
 const previous=middleMousePan;middleMousePan=null;v.style.cursor=previous.cursor;
 if(v.hasPointerCapture?.(previous.id))v.releasePointerCapture(previous.id);
}
v.addEventListener('pointerdown',event=>{
 if(event.button!==1||!v.loaded)return;
 event.preventDefault();event.stopImmediatePropagation();
 const orbit=v.getCameraOrbit(),target=v.getCameraTarget(),bounds=v.getBoundingClientRect();
 const scale=2*orbit.radius*Math.tan(v.getFieldOfView()*Math.PI/360)/Math.max(1,bounds.height);
 middleMousePan={id:event.pointerId,x:event.clientX,y:event.clientY,target:{x:target.x,y:target.y,z:target.z},scale,
  right:[Math.cos(orbit.theta),0,-Math.sin(orbit.theta)],
  up:[-Math.sin(orbit.theta)*Math.cos(orbit.phi),Math.sin(orbit.phi),-Math.cos(orbit.theta)*Math.cos(orbit.phi)],cursor:v.style.cursor};
 v.style.cursor='grabbing';v.setPointerCapture?.(event.pointerId);
},true);
v.addEventListener('pointermove',event=>{
 const pan=middleMousePan;if(!pan||event.pointerId!==pan.id)return;
 event.preventDefault();event.stopImmediatePropagation();
 const dx=(event.clientX-pan.x)*pan.scale,dy=(event.clientY-pan.y)*pan.scale;
 const goal=['x','y','z'].map((axis,i)=>pan.target[axis]-dx*pan.right[i]+dy*pan.up[i]);
 v.cameraTarget=goal.map(value=>value+'m').join(' ');
 v.updateComplete.then(()=>v.jumpCameraToGoal());
},true);
for(const type of ['pointerup','pointercancel','lostpointercapture'])v.addEventListener(type,event=>{
 if(!middleMousePan||event.pointerId!==middleMousePan.id)return;
 event.preventDefault();event.stopImmediatePropagation();stopMiddleMousePan(event);
},true);
v.addEventListener('auxclick',event=>{if(event.button===1){event.preventDefault();event.stopImmediatePropagation()}},true);
v.addEventListener('load',()=>stopMiddleMousePan());
