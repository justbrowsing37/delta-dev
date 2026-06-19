(function(){
  const t = document.querySelector('[data-theme-toggle]');
  const r = document.documentElement;
  let d = r.getAttribute('data-theme') || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  r.setAttribute('data-theme', d);
  function setIcon(mode) {
    if (!t) return;
    t.innerHTML = mode === 'dark'
      ? '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>'
      : '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
    t.setAttribute('aria-label', 'Switch to ' + (mode === 'dark' ? 'light' : 'dark') + ' mode');
  }
  setIcon(d);
  if (t) t.addEventListener('click', () => {
    d = d === 'dark' ? 'light' : 'dark';
    r.setAttribute('data-theme', d);
    setIcon(d);
  });
})();

document.getElementById('waitlist-form').addEventListener('submit', function(e) {
  e.preventDefault();
  const email = document.getElementById('email-input').value.trim();
  if (!email || !email.includes('@')) return;
  const btn = this.querySelector('.waitlist-submit');
  const origText = btn.textContent;
  btn.disabled = true;
  btn.textContent = 'submitting...';
  fetch('/waitlist', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({email: email})
  })
  .then(function(r) { return r.json(); })
  .then(function(data) {
    if (data.ok) {
      e.target.style.display = 'none';
      document.getElementById('success-msg').style.display = 'block';
    } else {
      btn.disabled = false;
      btn.textContent = origText;
      alert(data.error || 'Something went wrong.');
    }
  })
  .catch(function() {
    btn.disabled = false;
    btn.textContent = origText;
    alert('Network error. Please try again.');
  });
});

const observer = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.style.opacity = '1';
      e.target.style.transform = 'translateY(0)';
      observer.unobserve(e.target);
    }
  });
}, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

document.querySelectorAll('.step-card, .pricing-card, .features-layout, .stat-card').forEach(el => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(20px)';
  el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
  observer.observe(el);
});
