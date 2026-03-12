// ─────────────────────────────────────────────
//  auth.js  –  CampusConnect
//  Login & Register helpers
//  NOTE: doLogin() lives in login.html (inline).
//        This file only handles register logic
//        and shared utilities.
// ─────────────────────────────────────────────


// ── Shared utility ────────────────────────────
async function apiFetch(url, method = 'GET', body = null) {
  const opts = {
    method,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    }
  };
  if (body) opts.body = JSON.stringify(body);

  try {
    const res  = await fetch(url, opts);
    const data = await res.json();
    return { ok: res.ok, status: res.status, data };
  } catch (err) {
    console.error('apiFetch error:', err);
    return { ok: false, status: 0, data: { error: 'Network error' } };
  }
}


// ── Register ──────────────────────────────────
async function doRegister() {
  const nameEl  = document.getElementById('regName');
  const emailEl = document.getElementById('regEmail');
  const passEl  = document.getElementById('regPassword');
  const roleEl  = document.getElementById('regRole');
  const deptEl  = document.getElementById('regDept');
  const errEl   = document.getElementById('regError');
  const btn     = document.getElementById('regBtn');

  if (!nameEl || !emailEl || !passEl || !errEl) return; // not on register page

  errEl.style.display = 'none';

  const name       = nameEl.value.trim();
  const email      = emailEl.value.trim();
  const password   = passEl.value;
  const role       = roleEl?.value || 'student';
  const department = deptEl?.value.trim() || '';

  if (!name || !email || !password) {
    errEl.innerHTML = '<i class="fas fa-exclamation-circle"></i> Please fill all required fields.';
    errEl.style.display = 'block';
    return;
  }
  if (password.length < 6) {
    errEl.innerHTML = '<i class="fas fa-exclamation-circle"></i> Password must be at least 6 characters.';
    errEl.style.display = 'block';
    return;
  }

  if (btn) {
    btn.disabled  = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Registering…';
  }

  const { ok, data } = await apiFetch('/register', 'POST', { name, email, password, role, department });

  if (ok && data.success) {
    if (btn) btn.innerHTML = '<i class="fas fa-check"></i> Done!';
    window.location.href = data.redirect || '/dashboard';
  } else {
    errEl.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${data.error || 'Registration failed.'}`;
    errEl.style.display = 'block';
    if (btn) {
      btn.disabled  = false;
      btn.innerHTML = '<i class="fas fa-user-plus"></i> Register';
    }
  }
}


// ── DOM ready: wire up register page only ─────
document.addEventListener('DOMContentLoaded', () => {

  // Register button
  const regBtn = document.getElementById('regBtn');
  if (regBtn) {
    regBtn.addEventListener('click', doRegister);
  }

  // Enter key on register fields
  ['regName', 'regEmail', 'regPassword', 'regDept'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('keydown', e => { if (e.key === 'Enter') doRegister(); });
  });

  // NOTE: Login wiring (loginBtn + Enter) is handled
  // inside login.html's own <script> block.
  // Do NOT query loginEmail / loginPassword here —
  // this file loads on every page and those elements
  // won't exist outside /login.
});