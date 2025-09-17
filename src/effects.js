import * as THREE from 'three';

export function makeExplosion(scene, position, color=0xffcc66, count=24){
  const geom = new THREE.BufferGeometry();
  const positions = new Float32Array(count*3);
  const velocities = new Float32Array(count*3);
  for(let i=0;i<count;i++){
    positions[i*3+0]=position.x;
    positions[i*3+1]=position.y;
    positions[i*3+2]=position.z;
    const dir = new THREE.Vector3((Math.random()-0.5)*2,(Math.random()-0.5)*2,(Math.random()-0.5)*2).normalize().multiplyScalar(0.5+Math.random()*1.2);
    velocities[i*3+0]=dir.x; velocities[i*3+1]=dir.y; velocities[i*3+2]=dir.z;
  }
  geom.setAttribute('position', new THREE.BufferAttribute(positions,3));
  geom.setAttribute('velocity', new THREE.BufferAttribute(velocities,3));
  const mat = new THREE.PointsMaterial({color, size:0.2});
  const pts = new THREE.Points(geom, mat);
  pts.userData.life = 60;
  pts.userData.update = function(){
    const pos = pts.geometry.attributes.position;
    const vel = pts.geometry.attributes.velocity;
    for(let i=0;i<pos.count;i++){
      pos.array[i*3+0] += vel.array[i*3+0];
      pos.array[i*3+1] += vel.array[i*3+1];
      pos.array[i*3+2] += vel.array[i*3+2];
      // apply gravity
      vel.array[i*3+1] -= 0.02;
    }
    pos.needsUpdate = true;
    pts.userData.life -= 1;
    if(pts.userData.life <= 0){ if(pts.parent) pts.parent.remove(pts); }
  };
  scene.add(pts);
  return pts;
}
