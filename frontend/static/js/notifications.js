async function loadNotifications() {
  const badge = document.getElementById('notifBadge');
  const dropdown = document.getElementById('notifDropdown');
  if (!badge || !dropdown) return;

  const { ok, data: count } = await apiFetch('/api/notifications/unread-count');
  if (ok) {
    if (count.count > 0) {
      badge.textContent = count.count > 9 ? '9+' : count.count;
      badge.style.display = 'flex';
    } else {
      badge.style.display = 'none';
    }
  }
}

async function showNotifications() {
  const dropdown = document.getElementById('notifDropdown');
  dropdown.classList.toggle('active');
  if (!dropdown.classList.contains('active')) return;

  dropdown.innerHTML = '<div class="notif-loading"><i class="fas fa-spinner fa-spin"></i></div>';
  const { ok, data } = await apiFetch('/api/notifications');
  if (!ok) { dropdown.innerHTML = '<p class="notif-empty">Failed to load.</p>'; return; }

  if (!data.length) {
    dropdown.innerHTML = '<p class="notif-empty"><i class="fas fa-bell-slash"></i> No notifications</p>';
    return;
  }

  dropdown.innerHTML = `
    <div class="notif-header">
      <span>Notifications</span>
      <button onclick="markAllRead()">Mark all read</button>
    </div>
    <div class="notif-list">
      ${data.map(n => `
        <div class="notif-item ${n.is_read ? '' : 'notif-unread'}" onclick="markRead(${n.id}, this)">
          <div class="notif-icon notif-${n.type}">
            <i class="fas fa-${n.type === 'success' ? 'check' : n.type === 'danger' ? 'times' : n.type === 'warning' ? 'exclamation' : 'info'}"></i>
          </div>
          <div class="notif-content">
            <strong>${n.title}</strong>
            <p>${n.message}</p>
            <small>${formatDate(n.created_at)}</small>
          </div>
        </div>`).join('')}
    </div>`;
  
  await apiFetch('/api/notifications/read-all', 'POST');
  document.getElementById('notifBadge').style.display = 'none';
}

async function markAllRead() {
  await apiFetch('/api/notifications/read-all', 'POST');
  document.querySelectorAll('.notif-unread').forEach(el => el.classList.remove('notif-unread'));
  document.getElementById('notifBadge').style.display = 'none';
}

async function markRead(id, el) {
  await apiFetch(`/api/notifications/${id}/read`, 'POST');
  el.classList.remove('notif-unread');
}

// Bell click
document.addEventListener('DOMContentLoaded', () => {
  const bell = document.getElementById('notifBell');
  if (bell) bell.addEventListener('click', showNotifications);
  loadNotifications();
  // Poll every 30 seconds
  setInterval(loadNotifications, 30000);
});