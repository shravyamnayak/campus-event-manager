let allEvents = [];

async function loadEventsGrid() {
  const grid = document.getElementById('eventsGrid');
  if (!grid) return;

  const { ok, data } = await apiFetch('/api/events');
  if (!ok) { grid.innerHTML = '<p class="text-danger">Failed to load events.</p>'; return; }
  
  allEvents = data;
  renderEventsGrid(allEvents);
}

function renderEventsGrid(events) {
  const grid = document.getElementById('eventsGrid');
  const countEl = document.getElementById('eventsCount');
  if (countEl) countEl.textContent = `${events.length} event${events.length !== 1 ? 's' : ''} found`;

  if (!events.length) {
    grid.innerHTML = `
      <div class="empty-state" style="grid-column:1/-1">
        <i class="fas fa-calendar-times"></i>
        <p>No events found. Try adjusting your filters.</p>
      </div>`;
    return;
  }
  grid.innerHTML = events.map(ev => `
    <div class="event-card event-card-${ev.status}"
         data-type="${ev.event_type}"
         data-status="${ev.status}"
         data-title="${ev.title.toLowerCase()}">
      <div class="event-card-header">
        <span class="badge badge-${ev.event_type}">${ev.event_type}</span>
        <span class="status-badge status-${ev.status}">${ev.status}</span>
      </div>
      <h3><a href="/events/${ev.id}">${ev.title}</a></h3>
      <p class="event-desc">
        ${ev.description ? ev.description.substring(0, 100) + '…' : 'No description provided.'}
      </p>
      <div class="event-card-meta">
        <span><i class="fas fa-calendar"></i> ${formatDateTime(ev.start_datetime)}</span>
        ${ev.venue_name ? `<span><i class="fas fa-map-marker-alt"></i> ${ev.venue_name}</span>` : ''}
        <span><i class="fas fa-users"></i> ${ev.attendee_count}/${ev.max_attendees}</span>
        <span><i class="fas fa-user"></i> ${ev.organizer_name}</span>
      </div>
      <div class="event-card-footer">
        <a href="/events/${ev.id}" class="btn btn-sm btn-outline">
          <i class="fas fa-eye"></i> View Details
        </a>
        ${ev.status === 'approved'
          ? `<button class="btn btn-sm btn-primary" onclick="registerEvent(${ev.id})">
               <i class="fas fa-ticket-alt"></i> Register
             </button>`
          : ''}
      </div>
    </div>
  `).join('');
}

function filterEvents() {
  const status = document.getElementById('filterStatus')?.value || '';
  const type = document.getElementById('filterType')?.value || '';
  const search = document.getElementById('searchEvents')?.value.toLowerCase() || '';

  const filtered = allEvents.filter(ev => {
    return (!status || ev.status === status)
        && (!type || ev.event_type === type)
        && (!search || ev.title.toLowerCase().includes(search));
  });
  renderEventsGrid(filtered);
}

function openCreateEventModal() {
  loadVenuesForSelect();
  openModal('createEventModal');
}

async function loadVenuesForSelect() {
  const sel = document.getElementById('evVenue');
  if (!sel) return;
  const { ok, data } = await apiFetch('/api/venues');
  if (ok) {
    sel.innerHTML = '<option value="">-- No Venue --</option>' +
      data.filter(v => v.is_available).map(v => `<option value="${v.id}">${v.name} (cap: ${v.capacity})</option>`).join('');
  }
}

async function submitCreateEvent() {
  const errEl = document.getElementById('createEventError');
  const payload = {
    title: document.getElementById('evTitle').value.trim(),
    description: document.getElementById('evDesc').value.trim(),
    event_type: document.getElementById('evType').value,
    start_datetime: document.getElementById('evStart').value,
    end_datetime: document.getElementById('evEnd').value,
    venue_id: document.getElementById('evVenue').value || null,
    max_attendees: document.getElementById('evMax').value,
    is_public: document.getElementById('evPublic').checked,
  };

  if (!payload.title || !payload.start_datetime || !payload.end_datetime) {
    errEl.textContent = 'Please fill in all required fields.';
    errEl.style.display = 'block';
    return;
  }

  const { ok, data } = await apiFetch('/api/events', 'POST', payload);
  if (ok) {
    closeModal('createEventModal');
    showToast('Event submitted for approval!', 'success');
    setTimeout(() => location.reload(), 1000);
  } else {
    errEl.textContent = data.error || 'Failed to create event.';
    errEl.style.display = 'block';
  }
}

async function approveEvent(eventId, action) {
  const { ok, data } = await apiFetch(`/api/events/${eventId}/approve`, 'POST', { action });
  if (ok) {
    showToast(`Event ${action}d successfully!`, action === 'approve' ? 'success' : 'danger');
    const el = document.getElementById(`pending-${eventId}`);
    if (el) el.remove();
    setTimeout(() => location.reload(), 1200);
  } else {
    showToast(data.error || 'Action failed.', 'danger');
  }
}

async function cancelEvent(eventId, redirect = false) {
  if (!confirm('Are you sure you want to cancel this event?')) return;
  const { ok, data } = await apiFetch(`/api/events/${eventId}/cancel`, 'POST');
  if (ok) {
    showToast('Event cancelled.', 'warning');
    if (redirect) setTimeout(() => window.location.href = '/events', 1000);
    else setTimeout(() => location.reload(), 1000);
  } else {
    showToast(data.error || 'Failed to cancel.', 'danger');
  }
}

async function registerEvent(eventId) {
  const { ok, data } = await apiFetch('/api/bookings', 'POST', { event_id: eventId });
  if (ok) {
    showToast(data.booking.status === 'registered' ? 'Successfully registered!' : 'Added to waitlist!',
      data.booking.status === 'registered' ? 'success' : 'warning');
    setTimeout(() => location.reload(), 1000);
  } else {
    showToast(data.error || 'Registration failed.', 'danger');
  }
}