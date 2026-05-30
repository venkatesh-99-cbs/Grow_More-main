/**
 * Premium Toast Notification System
 * Auto-dismissing, stackable, type-based notifications
 */

class NotificationManager {
  constructor() {
    this.notifications = [];
    this.container = null;
    this.init();
  }

  init() {
    // Create container if not exists
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
      title = this.getDefaultTitle(type),
      duration = this.getDuration(type),
      dismissible = true
    } = options;

    const id = Date.now();
    const notification = { id, message, type, title, duration, dismissible };

    this.notifications.push(notification);
    this.renderNotification(notification);

    if (duration > 0) {
      setTimeout(() => this.remove(id), duration);
    }

    return id;
  }

  success(message, options = {}) {
    return this.show(message, { type: 'success', title: 'Success', ...options });
  }

  error(message, options = {}) {
    return this.show(message, { type: 'error', title: 'Error', ...options });
  }

  warning(message, options = {}) {
    return this.show(message, { type: 'warning', title: 'Warning', ...options });
  }

  info(message, options = {}) {
    return this.show(message, { type: 'info', title: 'Info', ...options });
  }

  getIcon(type) {
    const icons = {
      success: '✓',
      error: '✕',
      warning: '⚠',
      info: 'ℹ'
    };
    return icons[type] || icons.info;
  }

  getDefaultTitle(type) {
    const titles = {
      success: 'Success',
      error: 'Error',
      warning: 'Warning',
      info: 'Info'
    };
    return titles[type] || 'Notification';
  }

  getDuration(type) {
    const durations = {
      success: 3500,
      error: 6500,
      warning: 5500,
      info: 4000
    };
    return durations[type] || 4000;
  }

  renderNotification(notification) {
    const element = document.createElement('div');
    element.className = `toast-notification ${notification.type}`;
    element.dataset.id = notification.id;

    const progressDuration = notification.duration > 0 ? notification.duration : 4000;

    element.innerHTML = `
      <div class="toast-icon">${this.getIcon(notification.type)}</div>
      <div class="toast-content">
        <div class="toast-title">${this.escapeHtml(notification.title)}</div>
        <div class="toast-message">${this.escapeHtml(notification.message)}</div>
      </div>
      ${notification.dismissible ? '<button class="toast-close" aria-label="Close">✕</button>' : ''}
      ${notification.duration > 0 ? `<div class="toast-progress" style="animation-duration: ${progressDuration}ms;"></div>` : ''}
    `;

    this.container.appendChild(element);

    // Trigger animation
    requestAnimationFrame(() => {
      element.classList.add('show');
    });

    // Close button listener
    if (notification.dismissible) {
      const closeBtn = element.querySelector('.toast-close');
      if (closeBtn) {
        closeBtn.addEventListener('click', () => this.remove(notification.id));
      }
    }

    // Auto remove on mouse leave (for manual interaction)
    element.addEventListener('mouseenter', () => {
      const progressBar = element.querySelector('.toast-progress');
      if (progressBar) {
        progressBar.style.animationPlayState = 'paused';
      }
    });

    element.addEventListener('mouseleave', () => {
      const progressBar = element.querySelector('.toast-progress');
      if (progressBar) {
        progressBar.style.animationPlayState = 'running';
      }
    });
  }

  remove(id) {
    const element = document.querySelector(`.toast-notification[data-id="${id}"]`);
    if (element) {
      element.classList.add('removing');
      setTimeout(() => {
        element.remove();
      }, 400);
    }
    this.notifications = this.notifications.filter(n => n.id !== id);
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  clear() {
    this.container.innerHTML = '';
    this.notifications = [];
  }
}

// Create global instance
const notifications = new NotificationManager();

// Override Django message display to use premium toast system
document.addEventListener('DOMContentLoaded', function() {
  const messageElements = document.querySelectorAll('[data-message-type]');
  messageElements.forEach(el => {
    const type = el.dataset.messageType;
    const message = el.textContent.trim();
    if (message) {
      notifications.show(message, { type });
    }
  });

  // Handle form submission messages via data attributes
  document.querySelectorAll('form[data-success-message]').forEach(form => {
    form.addEventListener('submit', function() {
      const message = this.dataset.successMessage;
      const type = this.dataset.messageType || 'success';
      if (message) {
        // Store for display after redirect
        sessionStorage.setItem('pendingNotification', JSON.stringify({ message, type }));
      }
    });
  });

  // Check for pending notification from previous page
  const pending = sessionStorage.getItem('pendingNotification');
  if (pending) {
    try {
      const { message, type } = JSON.parse(pending);
      notifications.show(message, { type });
      sessionStorage.removeItem('pendingNotification');
    } catch (e) {
      console.warn('Failed to parse pending notification:', e);
    }
  }
});

// Export for external use
window.notifications = notifications;
