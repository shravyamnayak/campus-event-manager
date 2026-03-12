let allVenues = [];

async function loadVenuesGrid() {
  const grid = document.getElementById('venuesGrid');
  if (!grid) return;
  const { ok, data } = await apiFetch('/api/venues');
  if (!ok) { grid.innerHTML = '<p class="text-danger">Failed to load venues.</p>'; return; }
  allVenues = data;
  renderVenuesGrid(allVenues);
}

function renderVenuesGrid(venues) {
  const grid = document.getElementById('venuesGrid');
  if (!venues.length) {
    grid.innerHTML = '<div class="empty-state"><i class="fas fa-map-marker-alt"></i><p>No venues found.</p></div>';
    return;
  }
  grid.innerHTML = venues.map(v => `
    <div class="venue-card ${v.is_available ? '' : 'venue-unavailable'}">
      <div class="venue-card-header">
        <h3>${v.name}</h3>
        <span class="status-badge ${v.is_available ? 'status-approved' : 'status-cancelled'}">
          ${v.is_available ? 'Available' : 'Unavailable'}
        </span>
      </div>
      <div class="venue-meta">
        <span><i class="fas fa-map-marker-alt"></i> ${v.location || 'N/A'}</span>
        <span><i class="fas fa-users"></i> Capacity: ${v.capacity}</span>
      </div>
      ${v.amenities ? `<p class="venue-amenities"><i class="fas fa-star"></i> ${v.amenities}</p>` : ''}
      ${isAdmin() ? `
        <div class="venue-actions">
          <button class="btn btn-sm btn-outline" onclick="editVenue(${v.id})">
            <i class="fas fa-edit"></i> Edit
          </button>
          <button class="btn btn-sm btn-danger" onclick="deleteVenue(${v.id})">
            <i class="fas fa-trash"></i> Delete
          </button>
        </div>` : ''}
    </div>
  `).join('');
}

function isAdmin() {
  return document.querySelector('.role-badge.role-admin') !== null;
}

function openAddVenueModal() {
  document.getElementById('venueModalTitle').innerHTML = '<i class="fas fa-plus"></i> Add Venue';
  document.getElementById('editVenueId').value = '';
  document.getElementById('venueName').value = '';
  document.getElementById('venueLocation').value = '';
  document.getElementById('venueCapacity').value = '';
  document.getElementById('venueAmenities').value = '';
  document.getElementById('venueAvailable').checked = true;
  document.getElementById('venueSubmitBtn').textContent = 'Add Venue';
  openModal('addVenueModal');
}

function editVenue(id) {
  const venue = allVenues.find(v => v.id === id);
  if (!venue) return;
  document.getElementById('venueModalTitle').innerHTML = '<i class="fas fa-edit"></i> Edit Venue';
  document.getElementById('editVenueId').value = id;
  document.getElementById('venueName').value = venue.name;
  document.getElementById('venueLocation').value = venue.location || '';
  document.getElementById('venueCapacity').value = venue.capacity;
  document.getElementById('venueAmenities').value = venue.amenities || '';
  document.getElementById('venueAvailable').checked = venue.is_available;
  document.getElementById('venueSubmitBtn').textContent = 'Update Venue';
  openModal('addVenueModal');
}

async function submitVenue() {
  const id = document.getElementById('editVenueId')?.value;
  const payload = {
    name: document.getElementById('venueName').value.trim(),
    location: document.getElementById('venueLocation').value.trim(),
    capacity: document.getElementById('venueCapacity').value,
    amenities: document.getElementById('venueAmenities').value.trim(),
    is_available: document.getElementById('venueAvailable').checked,
  };
  if (!payload.name || !payload.capacity) {
    showToast('Name and capacity are required.', 'warning');
    return;
  }
  const url = id ? `/api/venues/${id}` : '/api/venues';
  const method = id ? 'PUT' : 'POST';
  const { ok, data } = await apiFetch(url, method, payload);
  if (ok) {
    closeModal('addVenueModal');
    showToast(id ? 'Venue updated!' : 'Venue added!', 'success');
    setTimeout(() => location.reload(), 800);
  } else {
    showToast(data.error || 'Failed to save venue.', 'danger');
  }
}

async function deleteVenue(id) {
  if (!confirm('Delete this venue? This cannot be undone.')) return;
  const { ok } = await apiFetch(`/api/venues/${id}`, 'DELETE');
  if (ok) {
    showToast('Venue deleted.', 'success');
    loadVenuesGrid();
  } else {
    showToast('Failed to delete venue.', 'danger');
  }
}

async function submitAddVenue() {
  await submitVenue();
}