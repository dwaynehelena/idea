import * as THREE from 'three';
import { makeExplosion } from './effects.js';

class Galaga3D {
  constructor(container, opts={}){
    this.container = (typeof container === 'string') ? document.querySelector(container) : (container || document.body);
    this.opts = Object.assign({width:0,height:0}, opts);
    this.score = 0;
    this.running = false;
    this._init();
  }

  // ... keep the implementation minimal here and reuse from the single-file demo
  _init(){
    this.renderer = new THREE.WebGLRenderer({antialias:true});
    this.renderer.setPixelRatio(window.devicePixelRatio || 1);
    this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
    this.container.appendChild(this.renderer.domElement);
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x000000);
    const aspect = this.container.clientWidth / Math.max(1,this.container.clientHeight);
    this.camera = new THREE.PerspectiveCamera(60, aspect, 0.1, 1000);
    this.camera.position.set(0, 8, 18);
    const dir = new THREE.DirectionalLight(0xffffff, 0.8);
    dir.position.set(5,10,7);
    this.scene.add(dir);
    this.scene.add(new THREE.AmbientLight(0x888888));
    this.player = this._makePlayer();
    this.scene.add(this.player);
    this.enemies = new THREE.Group();
    this.scene.add(this.enemies);
  this.bullets = [];
  this._makeStarfield();
  this.effects = [];
    this.keys = {};
    this.lastShot = 0;
    this.spawnEnemies();
    this._onResize = this._onResize.bind(this);
    this._onKey = this._onKey.bind(this);
    window.addEventListener('resize', this._onResize);
    window.addEventListener('keydown', e=>this._onKey(e,true));
    window.addEventListener('keyup', e=>this._onKey(e,false));
    this._tick = this._tick.bind(this);
    this._lastTime = performance.now();
    this.onScore = this.opts.onScore || function(){};
  }

  _makeStarfield(){
    const stars = new THREE.BufferGeometry();
    const count = 200;
    const positions = new Float32Array(count*3);
    for(let i=0;i<count;i++){
      positions[i*3+0] = (Math.random()-0.5)*80;
      positions[i*3+1] = (Math.random()-0.5)*40;
      positions[i*3+2] = -Math.random()*200;
    }
    stars.setAttribute('position', new THREE.BufferAttribute(positions,3));
    const material = new THREE.PointsMaterial({color:0xffffff,size:0.6,transparent:true,opacity:0.9});
    const p = new THREE.Points(stars, material);
    this.scene.add(p);
  }

  _makePlayer(){
    const g = new THREE.ConeGeometry(0.6,1.6,3);
    g.rotateX(Math.PI/2);
    const m = new THREE.MeshStandardMaterial({color:0x00c2ff,metalness:0.2,roughness:0.6});
    const mesh = new THREE.Mesh(g,m);
    mesh.name = 'player';
    mesh.userData.radius = 1.0;
    mesh.position.set(0,0,0);
    return mesh;
  }

  spawnEnemies(){
    while(this.enemies.children.length) this.enemies.remove(this.enemies.children[0]);
    this.enemyList = [];
    const rows = 3; const cols = 6;
    const spacingX = 2.6; const spacingY = 1.6;
    const startX = -((cols-1)/2)*spacingX;
    const startY = 6;
    for(let r=0;r<rows;r++){
      for(let c=0;c<cols;c++){
        const e = this._makeEnemy();
        e.position.set(startX + c*spacingX, startY - r*spacingY, -10 - r*2);
        e.userData.hit = false;
        this.enemies.add(e);
        this.enemyList.push(e);
      }
    }
    this.enemySweep = {dir:1,limit:10,speed:0.03};
  }

  _makeEnemy(){
    const g = new THREE.BoxGeometry(1,1,1);
    const m = new THREE.MeshStandardMaterial({color:0xff7ab6,metalness:0.1,roughness:0.6});
    const mesh = new THREE.Mesh(g,m);
    mesh.userData.radius = 0.85;
    return mesh;
  }

  _onKey(e,down){ if(e.code==='Space') e.preventDefault(); this.keys[e.code]=down; }
  _onResize(){ const w=this.container.clientWidth,h=this.container.clientHeight; this.camera.aspect=Math.max(0.1,w/h); this.camera.updateProjectionMatrix(); this.renderer.setSize(w,h); }
  start(){ if(this.running) return; this.running=true; this._lastTime=performance.now(); this._tick(); }
  pause(){ this.running=false; }
  reset(){ this.score=0; this.onScore(this.score); this.spawnEnemies(); }

  _tick(){ if(!this.running) return; const now=performance.now(); const dt=Math.min(40,(now-this._lastTime)); this._lastTime=now; this._update(dt/16); this.renderer.render(this.scene,this.camera); requestAnimationFrame(this._tick); }

  _update(dt){ const speed=0.2*dt; if(this.keys['ArrowLeft']) this.player.position.x -= speed; if(this.keys['ArrowRight']) this.player.position.x += speed; if(this.keys['ArrowUp']) this.player.position.y += speed*0.6; if(this.keys['ArrowDown']) this.player.position.y -= speed*0.6; this.player.position.x = THREE.MathUtils.clamp(this.player.position.x,-8,8); this.player.position.y = THREE.MathUtils.clamp(this.player.position.y,-3,8); if(this.keys['Space']){ if(performance.now()-this.lastShot>220){ this.shoot(); this.lastShot=performance.now(); } }
    for(let i=this.bullets.length-1;i>=0;i--){
      const b=this.bullets[i];
      b.position.addScaledVector(b.userData.vel, dt*0.5);
      if(b.position.z < -200) { this._removeBullet(b); continue; }
      for(let j=this.enemyList.length-1;j>=0;j--){
        const e=this.enemyList[j];
        if(!e||e.userData.hit) continue;
        const d=b.position.distanceTo(e.position);
        if(d < (b.userData.radius + e.userData.radius)){
          e.userData.hit=true; this.scene.remove(e); this.enemyList.splice(j,1);
          this._removeBullet(b);
          this._addScore(100);
          try{ const ex = makeExplosion(this.scene, e.position.clone()); this.effects.push(ex);}catch(ei){}
          break;
        }
      }
    }

    const sweep=this.enemySweep; sweep.offset=(sweep.offset||0)+sweep.dir*sweep.speed*dt; if(Math.abs(sweep.offset)>sweep.limit) sweep.dir*=-1; this.enemies.position.x = sweep.offset; if(this.enemyList.length===0) this.spawnEnemies();

    // update effects
    for(let k=this.effects.length-1;k>=0;k--){ const ef=this.effects[k]; if(ef.userData){ ef.userData.update(); if(ef.userData.life<=0){ this.effects.splice(k,1); } } }
  }

  shoot(){ const b=new THREE.Mesh(new THREE.SphereGeometry(0.18,8,8), new THREE.MeshBasicMaterial({color:0xffff66})); b.position.copy(this.player.position).add(new THREE.Vector3(0,0,-2)); b.userData={vel:new THREE.Vector3(0,0,-0.9),radius:0.18}; this.scene.add(b); this.bullets.push(b); }
  _removeBullet(b){ const idx=this.bullets.indexOf(b); if(idx>=0) this.bullets.splice(idx,1); this.scene.remove(b); }
  _addScore(n){ this.score+=n; this.onScore(this.score); }
  dispose(){ this.pause(); window.removeEventListener('resize', this._onResize); window.removeEventListener('keydown', this._onKey); window.removeEventListener('keyup', this._onKey); if(this.renderer&&this.renderer.domElement&&this.renderer.domElement.parentNode) this.renderer.domElement.parentNode.removeChild(this.renderer.domElement); }
}

export default Galaga3D;
