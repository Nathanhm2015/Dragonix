// Fish It - simple canvas fishing game
const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
let W, H;
function resize(){
  W = canvas.width = window.innerWidth;
  H = canvas.height = window.innerHeight;
}
window.addEventListener('resize', resize);
resize();

// UI
const scoreEl = document.getElementById('score');
const timeEl = document.getElementById('time');
const startBtn = document.getElementById('startBtn');
const pauseBtn = document.getElementById('pauseBtn');
const resetBtn = document.getElementById('resetBtn');

let score = 0;
let timeLeft = 60;
let running = false;

// Lure / hook
const lure = { x: W/2, y: 120, targetY: 160, dropping:false, length: 140 };

// Fish
const fishes = [];
function spawnFish(){
  const size = 14 + Math.random()*36;
  const side = Math.random() < 0.5 ? -1 : 1;
  const y = 200 + Math.random()*(H-300);
  const speed = (0.5 + Math.random()*1.2) * (side * -1);
  fishes.push({x: side < 0 ? W + 40 : -40, y, vx: speed, size, color: randomColor(), caught:false});
}

function randomColor(){
  const colors = ['#ffb86b','#ffd76b','#6be3ff','#7bff8a','#ff7bb8'];
  return colors[Math.floor(Math.random()*colors.length)];
}

// Input
let pointerX = W/2;
canvas.addEventListener('mousemove', e => { pointerX = e.clientX; });
canvas.addEventListener('touchmove', e=>{ if(e.touches[0]) pointerX = e.touches[0].clientX; });
canvas.addEventListener('click', (e)=>{ toggleLure(); attemptHook(e.clientX, e.clientY); });

function toggleLure(){
  lure.dropping = !lure.dropping;
  lure.targetY = lure.dropping ? H-80 : 120;
}

function attemptHook(px, py){
  // if a fish is near the lure tip, catch it
  const tip = { x: lure.x, y: lure.y + lure.length };
  for(const f of fishes){
    if(f.caught) continue;
    const dx = f.x - tip.x; const dy = f.y - tip.y;
    if(Math.hypot(dx,dy) < f.size + 12){
      f.caught = true; f.vx = 0; // attach
      break;
    }
  }
}

// Game loop
let last = 0; let spawnTimer = 0;
function update(dt){
  // timer
  if(running){
    timeLeft -= dt/1000;
    if(timeLeft <= 0){ timeLeft = 0; running = false; }
  }

  // lure follows pointer x smoothly
  lure.x += (pointerX - lure.x) * 0.12;
  // lure moves toward targetY
  lure.y += (lure.targetY - lure.y) * 0.06;

  // update fishes
  for(let i=fishes.length-1;i>=0;i--){
    const f = fishes[i];
    if(f.caught){
      // pulled up when hooked
      f.y += (lure.y + lure.length - f.y) * 0.12;
      f.x += (lure.x - f.x) * 0.06;
      // if close to boat (top), score and remove
      if(f.y < 140){ score += Math.round(f.size); fishes.splice(i,1); }
    } else {
      f.x += f.vx * dt/16;
      // small vertical bob
      f.y += Math.sin((f.x+f.size)*0.01)*0.5;
      // remove off-screen
      if(f.x < -120 || f.x > W + 120) fishes.splice(i,1);
    }
  }

  // spawn logic
  spawnTimer += dt;
  if(spawnTimer > 800){ spawnFish(); spawnTimer = 0; }
}

function draw(){
  // background
  ctx.clearRect(0,0,W,H);
  // water
  const grad = ctx.createLinearGradient(0,0,0,H);
  grad.addColorStop(0,'#cfeffd'); grad.addColorStop(1,'#4aa3e0');
  ctx.fillStyle = grad; ctx.fillRect(0,H*0.15,W,H*0.85);

  // boat
  const boatY = 100;
  ctx.fillStyle = '#664422'; ctx.fillRect(W*0.5-70, boatY-16, 140, 28);
  ctx.fillStyle = '#fff'; ctx.fillRect(W*0.5-34, boatY-34, 68, 20);

  // fishes
  for(const f of fishes){ drawFish(f); }

  // line and lure
  const tipX = lure.x;
  const tipY = lure.y + lure.length;
  ctx.strokeStyle = '#333'; ctx.lineWidth = 2; ctx.beginPath();
  ctx.moveTo(W*0.5, boatY); ctx.lineTo(tipX, tipY); ctx.stroke();
  // lure tip
  ctx.fillStyle = '#ff3333'; ctx.beginPath(); ctx.arc(tipX, tipY, 8,0,Math.PI*2); ctx.fill();

  // HUD handled in DOM
}

function drawFish(f){
  ctx.save(); ctx.translate(f.x, f.y);
  ctx.rotate(Math.atan2(0,f.vx));
  // body
  ctx.fillStyle = f.color; ctx.beginPath(); ctx.ellipse(0,0,f.size, f.size*0.6, 0, 0, Math.PI*2); ctx.fill();
  // tail
  ctx.fillStyle = shadeColor(f.color, -15);
  ctx.beginPath(); ctx.moveTo(-f.size,0); ctx.lineTo(-f.size-8,-8); ctx.lineTo(-f.size-8,8); ctx.closePath(); ctx.fill();
  ctx.restore();
}

function shadeColor(color, percent) {
  // simple hex shade
  const num = parseInt(color.replace('#',''),16);
  const r = Math.max(0, Math.min(255, (num>>16) + percent));
  const g = Math.max(0, Math.min(255, ((num>>8)&0x00FF) + percent));
  const b = Math.max(0, Math.min(255, (num&0x0000FF) + percent));
  return '#' + (r<<16 | g<<8 | b).toString(16).padStart(6,'0');
}

function loop(ts){
  const dt = Math.min(60, ts - last); last = ts;
  update(dt); draw();
  scoreEl.textContent = score;
  timeEl.textContent = Math.ceil(timeLeft);
  requestAnimationFrame(loop);
}
requestAnimationFrame(loop);

// controls
startBtn.addEventListener('click', ()=>{ if(!running){ running = true; if(timeLeft<=0) timeLeft=60; } });
pauseBtn.addEventListener('click', ()=>{ running = !running; });
resetBtn.addEventListener('click', ()=>{ running = false; score=0; timeLeft=60; fishes.length=0; });

// initial spawn
for(let i=0;i<6;i++) spawnFish();
