/* ========== DEVICE PREVIEW SHELL ========== */
/* Version: 1.0 */

const DevicePreview = {
  devices: {
    phone: { width: 390, height: 844 },
    tablet: { width: 820, height: 600 },
    desktop: { width: 1280, height: 800 }
  },
  currentDevice: 'phone',
  currentZoom: 100,
  frame: null,
  screen: null,

  init() {
    this.frame = document.getElementById('deviceFrame');
    this.screen = document.getElementById('deviceScreen');

    // Device switcher buttons
    document.querySelectorAll('[data-device]').forEach(btn => {
      btn.addEventListener('click', () => this.setDevice(btn.dataset.device));
    });

    // Zoom buttons
    document.querySelectorAll('[data-zoom]').forEach(btn => {
      btn.addEventListener('click', () => this.changeZoom(parseInt(btn.dataset.zoom)));
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => this.handleKeyboard(e));

    // Set initial device
    this.setDevice('phone');
  },

  setDevice(type) {
    if (!this.devices[type]) return;

    this.currentDevice = type;
    this.frame.className = 'device-frame ' + type;

    // Update button states
    document.querySelectorAll('[data-device]').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.device === type);
    });

    // Reset scroll
    this.resetScroll();
  },

  changeZoom(delta) {
    this.currentZoom = Math.min(150, Math.max(50, this.currentZoom + delta));
    this.frame.style.transform = `scale(${this.currentZoom / 100})`;
    this.frame.style.transformOrigin = 'center top';

    const zoomValue = document.querySelector('.zoom-value');
    if (zoomValue) {
      zoomValue.textContent = this.currentZoom + '%';
    }
  },

  resetScroll() {
    if (!this.screen) return;

    const reset = () => {
      this.screen.scrollTop = 0;
      this.screen.scrollTo({ top: 0, behavior: 'instant' });
    };

    reset();
    requestAnimationFrame(reset);
    setTimeout(reset, 100);
  },

  handleKeyboard(e) {
    // Ignore if typing in input
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

    switch(e.key) {
      case '1': this.setDevice('phone'); break;
      case '2': this.setDevice('tablet'); break;
      case '3': this.setDevice('desktop'); break;
      case '+':
      case '=': this.changeZoom(10); break;
      case '-': this.changeZoom(-10); break;
      case '0':
        this.currentZoom = 100;
        this.changeZoom(0);
        break;
      case 'm':
      case 'M':
        if (typeof openNavMap === 'function') openNavMap();
        break;
    }
  }
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => DevicePreview.init());
