/**
 * Premium Global Notification System
 * Auto-dismissing, glassmorphism toast notifications with progress bars.
 */

class NotificationManager {
  constructor() {
    this.container = null;
    this.init();
  }

  init() {
    if (!document.querySelector('.toast-container')) {
      this.container = document.createElement('div');
      this.container.className = 'toast-container';
      document.body.appendChild(this.container);
    } else {
      this.container = document.querySelector('.toast-container');
    }
  }

  show(message, options = {}) {
    const {
      type = 'info',
      duration = this.getDuration(type),
      dismissible = true,
      title = this.getDefaultTitle(type)
    } = options;

    const id = Date.now();
    this.renderNotification({ id, message, type, title, duration, dismissible });

    if (duration > 0) {
      setTimeout(() => this.remove(id), duration);
    }

    return id;
  }

  success(message, options = {}) {
    return this.show(message, { ...options, type: 'success' });
  }

  error(message, options = {}) {
    return this.show(message, { ...options, type: 'error' });
  }

  warning(message, options = {}) {
    return this.show(message, { ...options, type: 'warning' });
  }

  info(message, options = {}) {
    return this.show(message, { ...options, type: 'info' });
  }

  getDuration(type) {
    const durations = {
      success: 4000,
      warning: 5000,
      error: 7000,
      info: 4000
    };
    return durations[type] || 4000;
  }

  getDefaultTitle(type) {
    return type.charAt(0).toUpperCase() + type.slice(1);
  }

  getIcon(type) {
    const icons = {
      success: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>',
      error: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>',
      warning: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>',
      info: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>'
    };
    return icons[type] || icons.info;
  }

  renderNotification(n) {
    const el = document.createElement('div');
    el.className = `toast-notification ${n.type}`;
    el.dataset.id = n.id;

    el.innerHTML = `
      <div class="toast-icon">${this.getIcon(n.type)}</div>
      <div class="toast-content">
        <div class="toast-title">${n.title}</div>
        <div class="toast-message">${n.message}</div>
      </div>
      ${n.dismissible ? '<button class="toast-close">✕</button>' : ''}
      <div class="toast-progress" style="animation-duration: ${n.duration}ms"></div>
    `;

    this.container.prepend(el);

    requestAnimationFrame(() => el.classList.add('show'));

    if (n.dismissible) {
      el.querySelector('.toast-close').onclick = () => this.remove(n.id);
    }
  }

  remove(id) {
    const el = this.container.querySelector(`.toast-notification[data-id="${id}"]`);
    if (el) {
      el.classList.add('removing');
      el.addEventListener('animationend', () => el.remove(), { once: true });
    }
  }
}

const notifications = new NotificationManager();
window.notifications = notifications;

document.addEventListener('DOMContentLoaded', () => {
  // Capture Django messages
  const msgEl = document.getElementById('django-messages');
  if (msgEl) {
    msgEl.querySelectorAll('div').forEach(m => {
      notifications.show(m.textContent.trim(), { type: m.dataset.messageType });
    });
  }
});
