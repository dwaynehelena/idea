function distance(a, b){
  const dx = a.x - b.x; const dy = a.y - b.y; const dz = (a.z||0) - (b.z||0);
  return Math.sqrt(dx*dx + dy*dy + dz*dz);
}

function collides(a, b){
  return distance(a,b) < ((a.radius||0) + (b.radius||0));
}

function clamp(v, min, max){
  return Math.max(min, Math.min(max, v));
}

module.exports = { distance, collides, clamp };
