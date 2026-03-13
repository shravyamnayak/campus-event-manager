// bookings.js

document.addEventListener('DOMContentLoaded', function () {
  loadStats();
  loadBookings();

  var statusEl = document.getElementById('filterBookingStatus');
  var searchEl = document.getElementById('searchBookings');
  var roleEl   = document.getElementById('filterBookingRole');
  var sortEl   = document.getElementById('sortBookings');
  var resetBtn = document.getElementById('resetFilters');

  if (statusEl) statusEl.addEventListener('change', loadBookings);
  if (roleEl)   roleEl.addEventListener('change', loadBookings);
  if (sortEl)   sortEl.addEventListener('change', loadBookings);
  if (resetBtn) resetBtn.addEventListener('click', resetFilters);

  if (searchEl) {
    var t;
    searchEl.addEventListener('input', function () {
      clearTimeout(t);
      t = setTimeout(loadBookings, 300);
    });
  }

  // View toggle buttons
  document.querySelectorAll('[data-view]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      document.querySelectorAll('[data-view]').forEach(function (b) { b.classList.remove('active'); });
      btn.classList.add('active');
      renderBookings(window._lastBookings || []);
    });
  });
});


// ── Stats ─────────────────────────────────────────────────────────────────────
async function loadStats() {
  try {
    var res  = await fetch('/api/bookings/stats');
    var data = await res.json();

    setCounter('statTotal',      data.total      != null ? data.total      : '—');
    setCounter('statRegistered', data.registered != null ? data.registered : '—');
    setCounter('statWaitlisted', data.waitlisted != null ? data.waitlisted : '—');
    setCounter('statCancelled',  data.cancelled  != null ? data.cancelled  : '—');
  } catch (e) {
    console.error('Stats failed:', e);
  }
}

function setCounter(id, value) {
  var el = document.getElementById(id);
  if (el) el.textContent = value;
}


// ── Load bookings ─────────────────────────────────────────────────────────────
async function loadBookings() {
  var container = document.getElementById('bookingsTable') || document.getElementById('bookingsContainer');
  if (!container) return;

  container.innerHTML = '<div style="text-align:center;padding:2.5rem;color:var(--color-text-secondary)">Loading bookings…</div>';

  try {
    var res  = await fetch('/api/bookings');
    var data = await res.json();

    // Support both array response and {bookings:[]} response
    var list = Array.isArray(data) ? data : (data.bookings || []);
    window._lastBookings = list;

    // Apply client-side filters
    var statusEl = document.getElementById('filterBookingStatus');
    var searchEl = document.getElementById('searchBookings');
    var roleEl   = document.getElementById('filterBookingRole');
    var sortEl   = document.getElementById('sortBookings');

    var status = statusEl ? statusEl.value : '';
    var search = searchEl ? searchEl.value.toLowerCase() : '';
    var role   = roleEl   ? roleEl.value   : '';
    var sort   = sortEl   ? sortEl.value   : '';

    var filtered = list.filter(function (b) {
      if (status && b.status !== status) return false;
      if (role   && (b.user_role || b.role || '') !== role) return false;
      if (search) {
        var title = (b.event_title || (b.event && b.event.title) || '').toLowerCase();
        var name  = (b.user_name  || (b.user && b.user.name)   || '').toLowerCase();
        if (!title.includes(search) && !name.includes(search)) return false;
      }
      return true;
    });

    if (sort === 'newest') {
      filtered.sort(function(a,b){ return new Date(b.registered_at) - new Date(a.registered_at); });
    } else if (sort === 'oldest') {
      filtered.sort(function(a,b){ return new Date(a.registered_at) - new Date(b.registered_at); });
    }

    renderBookings(filtered);

  } catch (e) {
    container.innerHTML = '<div style="text-align:center;padding:2rem;color:var(--color-text-secondary)">Failed to load bookings.</div>';
    console.error(e);
  }
}


// ── Render ────────────────────────────────────────────────────────────────────
function renderBookings(bookings) {
  var container = document.getElementById('bookingsTable') || document.getElementById('bookingsContainer');
  if (!container) return;

  var viewBtn = document.querySelector('[data-view].active');
  var view    = viewBtn ? viewBtn.dataset.view : 'table';

  if (!bookings.length) {
    container.innerHTML = [
      '<div style="text-align:center;padding:3rem;color:var(--color-text-secondary)">',
      '<i class="fas fa-ticket-alt" style="font-size:2rem;margin-bottom:.75rem;display:block"></i>',
      '<p style="font-weight:500">No bookings found.</p>',
      '</div>'
    ].join('');
    return;
  }

  if (view === 'grid') {
    renderGrid(bookings, container);
  } else {
    renderTable(bookings, container);
  }
}

function renderTable(bookings, container) {
  var rows = bookings.map(function (b, i) {
    var title  = b.event_title || (b.event && b.event.title) || 'N/A';
    var uname  = b.user_name   || (b.user  && b.user.name)  || 'N/A';
    var date   = formatDate(b.registered_at);
    return [
      '<tr>',
      '<td>' + (i+1) + '</td>',
      '<td>' + esc(title) + '</td>',
      '<td>' + esc(uname) + '</td>',
      '<td><span class="status-badge status-' + esc(b.status) + '">' + esc(b.status) + '</span></td>',
      '<td>' + date + '</td>',
      '<td>',
      b.status !== 'cancelled'
        ? '<button class="btn btn-sm btn-danger" onclick="cancelBooking(' + b.id + ')">Cancel</button>'
        : '<span style="color:var(--color-text-tertiary)">—</span>',
      '</td>',
      '</tr>'
    ].join('');
  }).join('');

  container.innerHTML = [
    '<table class="data-table">',
    '<thead><tr><th>#</th><th>Event</th><th>User</th><th>Status</th><th>Registered At</th><th>Action</th></tr></thead>',
    '<tbody>' + rows + '</tbody>',
    '</table>'
  ].join('');
}

function renderGrid(bookings, container) {
  var cards = bookings.map(function (b) {
    var title = b.event_title || (b.event && b.event.title) || 'N/A';
    return [
      '<div class="booking-card">',
      '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.5rem">',
      '<span class="status-badge status-' + esc(b.status) + '">' + esc(b.status) + '</span>',
      '</div>',
      '<h3 style="font-size:.95rem;font-weight:600;margin-bottom:.4rem">' + esc(title) + '</h3>',
      '<p style="font-size:.8rem;color:var(--color-text-secondary)">' + formatDate(b.registered_at) + '</p>',
      b.status !== 'cancelled'
        ? '<button class="btn btn-sm btn-danger" style="margin-top:.75rem;width:100%" onclick="cancelBooking(' + b.id + ')">Cancel</button>'
        : '',
      '</div>'
    ].join('');
  }).join('');
  container.innerHTML = '<div class="bookings-grid">' + cards + '</div>';
}


// ── Cancel booking ────────────────────────────────────────────────────────────
async function cancelBooking(bookingId, redirect) {
  if (!confirm('Cancel this registration?')) return;
  try {
    var res  = await fetch('/api/bookings/' + bookingId + '/cancel', { method: 'POST' });
    var data = await res.json();
    if (data.success) {
      if (typeof showToast === 'function') showToast('Registration cancelled.', 'warning');
      if (redirect) { setTimeout(function(){ location.reload(); }, 800); }
      else { loadStats(); loadBookings(); }
    } else {
      alert(data.error || 'Failed to cancel.');
    }
  } catch (e) {
    alert('Network error. Please try again.');
  }
}

function resetFilters() {
  ['filterBookingStatus','filterBookingRole','sortBookings'].forEach(function(id){
    var el = document.getElementById(id);
    if (el) el.value = '';
  });
  var s = document.getElementById('searchBookings');
  if (s) s.value = '';
  loadStats();
  loadBookings();
}

function esc(s) {
  return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function formatDate(iso) {
  if (!iso) return '—';
  try {
    return new Date(iso).toLocaleDateString('en-IN', {
      day:'numeric', month:'short', year:'numeric', hour:'2-digit', minute:'2-digit'
    });
  } catch(e) { return iso; }
}