async function doLogin() {
  const email = document.getElementById('loginEmail').value.trim();
  const password = document.getElementById('loginPassword').value;
  const errEl = document.getElementById('loginError');

  if (!email || !password) {
    errEl.textContent = 'Please fill in all fields.';
    errEl.style.display = 'block';
    return;
  }

  const { ok, data } = await apiFetch('/login', 'POST', { email, password });

  if (ok && data.success) {
    window.location.href = '/dashboard';
  } else {
    errEl.textContent = data.error || 'Login failed.';
    errEl.style.display = 'block';
  }
}

async function doRegister() {
  const name = document.getElementById('regName').value.trim();
  const email = document.getElementById('regEmail').value.trim();
  const password = document.getElementById('regPassword').value;
  const role = document.getElementById('regRole').value;
  const department = document.getElementById('regDept').value.trim();
  const errEl = document.getElementById('regError');

  if (!name || !email || !password) {
    errEl.textContent = 'Please fill all required fields.';
    errEl.style.display = 'block';
    return;
  }
  if (password.length < 6) {
    errEl.textContent = 'Password must be at least 6 characters.';
    errEl.style.display = 'block';
    return;
  }

  const { ok, data } = await apiFetch('/register', 'POST', { name, email, password, role, department });

  if (ok && data.success) {
    window.location.href = '/dashboard';
  } else {
    errEl.textContent = data.error || 'Registration failed.';
    errEl.style.display = 'block';
  }
}

// Enter key support
document.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') {
    if (document.getElementById('loginEmail')) doLogin();
    if (document.getElementById('regName')) doRegister();
  }
});