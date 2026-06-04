/**
 * Premium Global Notification System
 * Lightweight glassmorphism toasts with queue limiting and pause-on-hover.
 */

class NotificationManager {
  constructor() {
    this.container = null;
    this.active = new Map();
    this.maxVisible = 4;
    this.init();
  }

  init() {
    this.container = document.querySelector(".toast-container");
    if (!this.container) {
      this.container = document.createElement("div");
      this.container.className = "toast-container";
      document.body.appendChild(this.container);
    }
  }

  show(message, options = {}) {
    const type = options.type || "info";
    const notification = {
      id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
      message,
      type,
      duration: options.duration ?? this.getDuration(type),
      dismissible: options.dismissible ?? true,
      title: options.title || this.getDefaultTitle(type),
    };
    this.render(notification);
    return notification.id;
  }

  success(message, options = {}) {
    return this.show(message, { ...options, type: "success" });
  }

  error(message, options = {}) {
    return this.show(message, { ...options, type: "error" });
  }

  warning(message, options = {}) {
    return this.show(message, { ...options, type: "warning" });
  }

  info(message, options = {}) {
    return this.show(message, { ...options, type: "info" });
  }

  getDuration(type) {
    return { success: 3800, info: 4200, warning: 5600, error: 7200 }[type] || 4200;
  }

  getDefaultTitle(type) {
    return { success: "Success", error: "Action needed", warning: "Heads up", info: "Update" }[type] || "Update";
  }

  getIcon(type) {
    const icons = {
      success: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>',
      error: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>',
      warning: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>',
      info: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>',
    };
    return icons[type] || icons.info;
  }

  render(notification) {
    const el = document.createElement("div");
    el.className = `toast-notification ${notification.type}`;
    el.dataset.id = notification.id;
    el.setAttribute("role", notification.type === "error" ? "alert" : "status");

    const icon = document.createElement("div");
    icon.className = "toast-icon";
    icon.innerHTML = this.getIcon(notification.type);

    const content = document.createElement("div");
    content.className = "toast-content";
    const title = document.createElement("div");
    title.className = "toast-title";
    title.textContent = notification.title;
    const message = document.createElement("div");
    message.className = "toast-message";
    message.textContent = notification.message;
    content.append(title, message);

    el.append(icon, content);

    if (notification.dismissible) {
      const close = document.createElement("button");
      close.className = "toast-close";
      close.type = "button";
      close.setAttribute("aria-label", "Dismiss notification");
      close.textContent = "x";
      close.addEventListener("click", () => this.remove(notification.id));
      el.appendChild(close);
    }

    const progress = document.createElement("div");
    progress.className = "toast-progress";
    progress.style.animationDuration = `${notification.duration}ms`;
    el.appendChild(progress);

    this.container.prepend(el);
    this.trimVisible();
    requestAnimationFrame(() => el.classList.add("show"));

    if (notification.duration > 0) {
      const state = {
        remaining: notification.duration,
        startedAt: Date.now(),
        timer: setTimeout(() => this.remove(notification.id), notification.duration),
        progress,
      };
      this.active.set(notification.id, state);
      el.addEventListener("mouseenter", () => this.pause(notification.id));
      el.addEventListener("mouseleave", () => this.resume(notification.id));
    }
  }

  trimVisible() {
    const items = [...this.container.querySelectorAll(".toast-notification")];
    items.slice(this.maxVisible).forEach((item) => this.remove(item.dataset.id));
  }

  pause(id) {
    const state = this.active.get(id);
    if (!state) return;
    clearTimeout(state.timer);
    state.remaining = Math.max(0, state.remaining - (Date.now() - state.startedAt));
    state.progress.style.animationPlayState = "paused";
  }

  resume(id) {
    const state = this.active.get(id);
    if (!state) return;
    state.startedAt = Date.now();
    state.timer = setTimeout(() => this.remove(id), state.remaining);
    state.progress.style.animationPlayState = "running";
  }

  remove(id) {
    const el = this.container.querySelector(`.toast-notification[data-id="${id}"]`);
    if (!el) return;
    const state = this.active.get(id);
    if (state) clearTimeout(state.timer);
    this.active.delete(id);
    el.classList.add("removing");
    el.addEventListener("animationend", () => el.remove(), { once: true });
  }
}

const notifications = new NotificationManager();
window.notifications = notifications;

document.addEventListener("DOMContentLoaded", () => {
  const msgEl = document.getElementById("django-messages");
  if (!msgEl) return;
  msgEl.querySelectorAll("div").forEach((message) => {
    notifications.show(message.textContent.trim(), { type: message.dataset.messageType || "info" });
  });
});
