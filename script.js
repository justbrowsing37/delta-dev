const SUPABASE_URL = 'https://mrfzhmolmktqlwsuvtdy.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1yZnpobW9sbWt0cWx3c3V2dGR5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODI0MTc0ODUsImV4cCI6MjA5Nzk5MzQ4NX0.yrVXhvhAAwBlDQPxGunayHonZArWYJgjm4outL0JTOQ';

// ── BACKGROUND CANVAS ──────────────────────────────────────────
const canvas = document.getElementById('bg-canvas');
const ctx = canvas.getContext('2d');

function resizeCanvas() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
}
resizeCanvas();
window.addEventListener('resize', resizeCanvas);

const COLS = 28, ROWS = 18;
const nodes = [];
for (let i = 0; i < COLS; i++) {
  for (let j = 0; j < ROWS; j++) {
    nodes.push({
      baseX: i / (COLS - 1), baseY: j / (ROWS - 1),
      ox: (Math.random() - 0.5) * 0.025,
      oy: (Math.random() - 0.5) * 0.025,
      phase: Math.random() * Math.PI * 2,
      speed: 0.004 + Math.random() * 0.003
    });
  }
}

// warp state — epicentre + intensity, decays over time
let warpX = 0.5, warpY = 0.5, warpStrength = 0, warpDecay = 0;

function drawGrid(t) {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  const w = canvas.width, h = canvas.height;

  // decay warp each frame
  if (warpStrength > 0) {
    warpStrength = Math.max(0, warpStrength - warpDecay);
  }

  const pts = nodes.map(n => {
    let nx = n.baseX + n.ox * Math.sin(t * n.speed + n.phase);
    let ny = n.baseY + n.oy * Math.cos(t * n.speed + n.phase + 1);

    if (warpStrength > 0) {
      const dx = nx - warpX;
      const dy = ny - warpY;
      const dist = Math.sqrt(dx * dx + dy * dy) + 0.001;
      const force = warpStrength / (dist * 18);
      nx += dx * force;
      ny += dy * force;
    }

    return { x: nx * w, y: ny * h };
  });

  for (let i = 0; i < COLS; i++) {
    for (let j = 0; j < ROWS; j++) {
      const idx = i * ROWS + j, p = pts[idx];
      if (i < COLS - 1) {
        const r = pts[(i+1)*ROWS+j];
        ctx.beginPath(); ctx.moveTo(p.x,p.y); ctx.lineTo(r.x,r.y);
        ctx.strokeStyle='rgba(34,197,94,0.18)'; ctx.lineWidth=0.5; ctx.stroke();
      }
      if (j < ROWS - 1) {
        const b = pts[i*ROWS+(j+1)];
        ctx.beginPath(); ctx.moveTo(p.x,p.y); ctx.lineTo(b.x,b.y);
        ctx.strokeStyle='rgba(34,197,94,0.18)'; ctx.lineWidth=0.5; ctx.stroke();
      }
      ctx.beginPath(); ctx.arc(p.x,p.y,1.2,0,Math.PI*2);
      ctx.fillStyle='rgba(34,197,94,0.35)'; ctx.fill();
    }
  }
}

let frame = 0;
function animateGrid() { drawGrid(frame++); requestAnimationFrame(animateGrid); }
animateGrid();

function triggerGridWarp() {
  const hero = document.querySelector('.hero');
  const rect = hero.getBoundingClientRect();
  // epicentre as fraction of canvas
  warpX = (rect.left + rect.width / 2) / window.innerWidth;
  warpY = (rect.top + rect.height / 2) / window.innerHeight;
  warpStrength = 0.18;
  warpDecay = 0.0018;
}

// ── TYPING ─────────────────────────────────────────────────────
const line1El   = document.getElementById('line-1');
const cursor1El = document.getElementById('cursor-1');
const line2El   = document.getElementById('line-2');
const cursor2El = document.getElementById('cursor-2');

const LINE1 = "Information isn't the edge.";
const LINE2 = "Understanding is.";

function typeString(el, str, speed, cb) {
  let i = 0;
  function tick() {
    el.textContent = str.slice(0, ++i);
    if (i < str.length) setTimeout(tick, speed);
    else if (cb) cb();
  }
  setTimeout(tick, speed);
}

setTimeout(() => {
  typeString(line1El, LINE1, 65, () => {
    setTimeout(() => {
      cursor1El.classList.add('hidden');
      cursor2El.classList.remove('hidden');
      typeString(line2El, LINE2, 65, null);
    }, 900);
  });
}, 800);

// ── COUNTDOWN ──────────────────────────────────────────────────
function getDaysUntilLaunch() {
  const launch = new Date('2027-01-01T00:00:00');
  const now = new Date();
  return Math.max(0, Math.ceil((launch - now) / (1000 * 60 * 60 * 24)));
}

function updateCountdown() {
  document.getElementById('days-count').textContent = getDaysUntilLaunch();
}
updateCountdown();

// ── SCROLL REVEAL ──────────────────────────────────────────────
const reveals = document.querySelectorAll('.reveal');
const observer = new IntersectionObserver((entries) => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.12 });
reveals.forEach(el => observer.observe(el));

// ── SUCCESS ANIMATION ──────────────────────────────────────────
function launchSuccessAnimation() {
  const form = document.getElementById('signup-form');
  const formLabel = document.querySelector('.form-label');

  // 1. Trigger grid warp immediately
  triggerGridWarp();

  // 2. Fade out form
  [form, formLabel].forEach(el => {
    if (el) { el.style.transition = 'opacity 0.4s ease'; el.style.opacity = '0'; }
  });

  setTimeout(() => {
    [form, formLabel].forEach(el => { if (el) el.style.display = 'none'; });

    // Build success container — no sonar rings
    const container = document.createElement('div');
    container.className = 'success-container';
    container.innerHTML = `
      <div class="success-counter-wrap">
        <span class="counter-number" id="counter-num">0</span>
        <span class="counter-label mono">days until launch</span>
      </div>
      <p class="success-tagline mono" id="success-tagline"></p>
    `;

    const heroContent = document.querySelector('.hero-content');
    const countdown = document.querySelector('.countdown');
    heroContent.insertBefore(container, countdown);

    // Fade container in
    container.style.opacity = '0';
    container.style.transition = 'opacity 0.5s ease';
    requestAnimationFrame(() => requestAnimationFrame(() => { container.style.opacity = '1'; }));

    const target = getDaysUntilLaunch();
    const numEl = document.getElementById('counter-num');
    const CHARS = '0123456789';

    // Phase 1: scramble for 900ms
    const scrambleDuration = 900;
    const scrambleStart = performance.now();

    // persistent glow throughout
    numEl.style.textShadow = '0 0 24px rgba(74,222,128,0.55)';

    function scramble(now) {
      const elapsed = now - scrambleStart;
      if (elapsed < scrambleDuration) {
        // random number same digit-length as target
        const digits = String(target).length;
        let rand = '';
        for (let i = 0; i < digits; i++) rand += CHARS[Math.floor(Math.random() * 10)];
        numEl.textContent = rand;

        // subtle horizontal jitter
        numEl.style.transform = `translateX(${(Math.random()-0.5)*4}px)`;
        // flicker glow
        const g = 0.4 + Math.random() * 0.4;
        numEl.style.textShadow = `0 0 ${20 + Math.random()*20}px rgba(74,222,128,${g})`;

        requestAnimationFrame(scramble);
      } else {
        // Phase 2: lock in with a hard snap
        numEl.textContent = target;
        numEl.style.transform = 'translateX(0)';
        numEl.style.textShadow = '0 0 40px rgba(74,222,128,0.95), 0 0 80px rgba(74,222,128,0.4)';

        // brief scale punch on lock
        numEl.style.transition = 'transform 0.15s cubic-bezier(0.34,1.56,0.64,1)';
        numEl.style.transform = 'scale(1.08)';
        setTimeout(() => {
          numEl.style.transform = 'scale(1)';
          // settle glow
          numEl.style.textShadow = '0 0 30px rgba(74,222,128,0.8), 0 0 60px rgba(74,222,128,0.3)';
        }, 160);

        // Fade in tagline
        setTimeout(() => {
          const tagline = document.getElementById('success-tagline');
          tagline.textContent = "we're not stopping. see you then.";
          tagline.style.opacity = '0';
          tagline.style.transition = 'opacity 0.8s ease';
          requestAnimationFrame(() => { tagline.style.opacity = '1'; });
        }, 400);
      }
    }

    setTimeout(() => requestAnimationFrame(scramble), 150);
  }, 420);
}

// ── FORM SUBMISSION ────────────────────────────────────────────
document.getElementById('signup-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const email = document.getElementById('email-input').value.trim();
  const btn = document.getElementById('submit-btn');
  const msg = document.getElementById('form-message');
  btn.disabled = true; btn.textContent = 'Joining...';
  msg.className = 'form-message hidden'; msg.textContent = '';
  try {
    const res = await fetch(`${SUPABASE_URL}/rest/v1/waitlist`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
        'Prefer': 'return=minimal'
      },
      body: JSON.stringify({ email })
    });
    if (res.status === 201) {
      launchSuccessAnimation();
    } else if (res.status === 409) {
      launchSuccessAnimation();
    } else { throw new Error(); }
  } catch {
    msg.textContent = 'Something went wrong. Try again.';
    msg.className = 'form-message error';
    btn.disabled = false; btn.textContent = 'Join Waitlist';
  }
});
