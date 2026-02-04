/* ========== NAVIGATION SYSTEM ========== */
/* Version: 1.0 */

/**
 * Navigate to a specific screen
 */
function navigateTo(screenId) {
  // Hide all screens
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));

  // Show target screen
  const target = document.getElementById(screenId);
  if (target) {
    target.classList.add('active');
  }

  // Reset scroll position
  const screen = document.getElementById('deviceScreen');
  if (screen) {
    screen.scrollTop = 0;
    requestAnimationFrame(() => screen.scrollTop = 0);
  }
}

/**
 * Switch tab bar tabs
 */
function switchTab(btn, screenId) {
  // Update active state on all tab items
  document.querySelectorAll('.tab-item').forEach(t => t.classList.remove('active'));
  btn.classList.add('active');

  // Navigate to screen
  navigateTo(screenId);
}

/**
 * Show popup/modal
 */
function showPopup(id) {
  const popup = document.getElementById(id);
  if (popup) {
    popup.classList.add('active');
  }
}

/**
 * Hide popup/modal
 */
function hidePopup(id, event) {
  // Only hide if clicking overlay (not popup content)
  if (!event || event.target.classList.contains('popup-overlay')) {
    const popup = document.getElementById(id);
    if (popup) {
      popup.classList.remove('active');
    }
  }
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
  // Remove existing toast
  const existing = document.querySelector('.toast');
  if (existing) existing.remove();

  // Create new toast
  const toast = document.createElement('div');
  toast.className = 'toast' + (type !== 'info' ? ' ' + type : '');
  toast.textContent = message;

  // Add to device screen
  const screen = document.querySelector('.device-screen');
  if (screen) {
    screen.appendChild(toast);
  } else {
    document.body.appendChild(toast);
  }

  // Animate in
  setTimeout(() => toast.classList.add('show'), 10);

  // Remove after delay
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 300);
  }, 2500);
}

/**
 * Select radio button in a group
 */
function selectRadio(item, groupId) {
  const group = document.getElementById(groupId);
  if (group) {
    group.querySelectorAll('.radio').forEach(r => r.classList.remove('active'));
    const radio = item.querySelector('.radio');
    if (radio) radio.classList.add('active');
  }
}

/**
 * Toggle checkbox
 */
function toggleCheckbox(el) {
  const checkbox = el.querySelector('.checkbox');
  if (checkbox) {
    checkbox.classList.toggle('checked');
  }
}

/* ========== NAVIGATION MAP ========== */

function openNavMap() {
  const overlay = document.getElementById('navMapOverlay');
  if (overlay) overlay.classList.add('active');
}

function closeNavMap() {
  const overlay = document.getElementById('navMapOverlay');
  if (overlay) overlay.classList.remove('active');
}

function closeNavMapOnOverlay(event) {
  if (event.target.id === 'navMapOverlay') {
    closeNavMap();
  }
}

function toggleSection(headerEl) {
  const section = headerEl.parentElement;
  if (section) section.classList.toggle('collapsed');
}

function navMapGo(screenId) {
  closeNavMap();
  navigateTo(screenId);
  showToast('→ ' + screenId.replace('screen-', ''), 'info');
}

function navMapTab(name, parentScreen) {
  closeNavMap();
  if (parentScreen) {
    navigateTo(parentScreen);
  }
  setTimeout(() => {
    showToast('🟡 Таб "' + name + '" — переключает контент', 'info');
  }, 300);
}

function navMapEndpoint(name, parentScreen) {
  closeNavMap();
  if (parentScreen) {
    navigateTo(parentScreen);
  }
  setTimeout(() => {
    showToast('📌 ' + name + ' — финальная точка', 'info');
  }, 300);
}
