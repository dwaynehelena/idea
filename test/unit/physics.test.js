const { distance, collides, clamp } = require('../../src/physics');

test('distance between points', ()=>{
  expect(distance({x:0,y:0,z:0},{x:3,y:4,z:0})).toBeCloseTo(5);
});

test('collides returns true when distance < sum radii', ()=>{
  const a = {x:0,y:0,z:0, radius:1};
  const b = {x:1.5,y:0,z:0, radius:1};
  expect(collides(a,b)).toBe(true);
});

test('collides returns false when distance >= sum radii', ()=>{
  const a = {x:0,y:0,z:0, radius:1};
  const b = {x:3,y:0,z:0, radius:1};
  expect(collides(a,b)).toBe(false);
});

test('clamp works', ()=>{
  expect(clamp(10, -5, 5)).toBe(5);
  expect(clamp(-10, -5, 5)).toBe(-5);
  expect(clamp(2, -5, 5)).toBe(2);
});
