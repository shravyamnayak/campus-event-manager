// ── Utility Functions ────────────────────────────────────────────

async function apiFetch(url, method = 'GET', body = null) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
  };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(url, opts);
  const data = await res.json();
  return { ok: res.ok, status: res.status, data };
}

function showToast(message, type = 'info', duration = 3500) {
  const container = document.querySelector('.flash-container') || (() => {
    const el = document.createElement('div');
    el.className = 'flash-container';
    document.body.prepend(el);
    return el;
  })();
  const alert = document.createElement('div');
  alert.className = `alert alert-${type}`;
  alert.innerHTML = `<span>${message}</span><button onclick="this.parentElement.remove()">×</button>`;
  container.appendChild(alert);
  setTimeout(() => alert.remove(), duration);
}

function openModal(id) {
  document.getElementById(id).classList.add('active');
}

function closeModal(id) {
  document.getElementById(id).classList.remove('active');
}

function togglePwd(inputId, icon) {
  const input = document.getElementById(inputId);
  if (input.type === 'password') {
    input.type = 'text';
    icon.classList.replace('fa-eye', 'fa-eye-slash');
  } else {
    input.type = 'password';
    icon.classList.replace('fa-eye-slash', 'fa-eye');
  }
}

function formatDate(iso) {
  const d = new Date(iso);
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
}

function formatDateTime(iso) {
  const d = new Date(iso);
  return d.toLocaleString('en-IN', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}

// Close modal on backdrop click
document.addEventListener('click', (e) => {
  if (e.target.classList.contains('modal')) {
    e.target.classList.remove('active');
  }
});

// Auto-dismiss alerts after 4s
// IMPORTANT: only target alerts inside .flash-container (server flash messages)
// Do NOT touch #loginError, #regError etc. — those are controlled by JS logic
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.flash-container .alert').forEach(a => {
    setTimeout(() => a.remove(), 4000);
  });
});