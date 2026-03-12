let allBookings = [];

async function loadBookingsTable() {
  const container = document.getElementById('bookingsTable');
  if (!container) return;
  const { ok, data } = await apiFetch('/api/bookings');
  if (!ok) { container.innerHTML = '<p class="text-danger">Failed to load bookings.</p>'; return; }
  allBookings = data;
  renderBookingsTable(allBookings);
}

function renderBookingsTable(bookings) {
  const container = document.getElementById('bookingsTable');
  if (!bookings.length) {
    container.innerHTML = '<div class="empty-state"><i class="fas fa-ticket-alt"></i><p>No bookings found.</p></div>';
    return;
  }
  container.innerHTML = `
    <table class="data-table">
      <thead>
        <tr>
          <th>#</th>
          <th>Event</th>
          <th>User</th>
          <th>Status</th>
          <th>Registered At</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        ${bookings.map((b, i) => `
          <tr class="booking-row" data-status="${b.status}" data-title="${(b.event_title||'').toLowerCase()}">
            <td>${i+1}</td>
            <td>${b.event_title || 'N/A'}</td>
            <td>${b.user_name || 'N/A'}</td>
            <td><span class="status-badge status-${b.status}">${b.status}</span></td>
            <td>${formatDate(b.registered_at)}</td>
            <td>
              ${b.status !== 'cancelled' ? 
                `<button class="btn btn-sm btn-danger" onclick="cancelBooking(${b.id})">Cancel</button>` : 
                '<span class="text-muted">—</span>'}
            </td>
          </tr>
        `).join('')}
      </tbody>
    </table>`;
}

function filterBookings() {
  const status = document.getElementById('filterBookingStatus')?.value || '';
  const search = document.getElementById('searchBookings')?.value.toLowerCase() || '';
  const filtered = allBookings.filter(b =>
    (!status || b.status === status) &&
    (!search || (b.event_title||'').toLowerCase().includes(search))
  );
  renderBookingsTable(filtered);
}

async function cancelBooking(bookingId, redirect = false) {
  if (!confirm('Cancel this registration?')) return;
  const { ok, data } = await apiFetch(`/api/bookings/${bookingId}/cancel`, 'POST');
  if (ok) {
    showToast('Registration cancelled.', 'warning');
    if (redirect) setTimeout(() => location.reload(), 1000);
    else loadBookingsTable();
  } else {
    showToast(data.error || 'Failed to cancel.', 'danger');
  }
}