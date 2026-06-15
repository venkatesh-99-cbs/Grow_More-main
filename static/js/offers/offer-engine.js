/**
 * Grow More — Global Countdown Engine
 */

// ─── TIMER STORAGE ───────────────────────────────────────
// Saves the end timestamp to localStorage so it survives
// page navigation and refreshes

function initGlobalDealTimer() {
  // End time is managed by the server injecting OFFER_END_MS in base.html
}

function getGlobalCountdownSeconds() {
  const endTime = Number(localStorage.getItem("gm_deal_end_time") || 0);
  return Math.max(0, Math.floor((endTime - Date.now()) / 1000));
}

// ─── CALLBACK REGISTRY ───────────────────────────────────
let globalCountdownInterval = null;
let badgeUpdateInterval = null;
let countdownCallbacks = [];

function registerCountdownCallback(callback) {
  if (!callback || typeof callback !== "function") return;
  if (!countdownCallbacks.includes(callback)) {
    countdownCallbacks.push(callback);
    callback(getGlobalCountdownSeconds()); // immediate first call
  }
}

function startGlobalCountdownTick() {
  if (globalCountdownInterval) return; // already running
  globalCountdownInterval = setInterval(() => {
    const secondsLeft = getGlobalCountdownSeconds();
    countdownCallbacks.forEach((cb) => {
      try { cb(secondsLeft); } catch (err) { console.error(err); }
    });
  }, 1000);

  const secondsLeft = getGlobalCountdownSeconds();
  countdownCallbacks.forEach((cb) => {
    try { cb(secondsLeft); } catch (err) { console.error(err); }
  });
}

// ─── FORMATTER ───────────────────────────────────────────
function formatCountdown(totalSeconds) {
  const hours = Math.floor(totalSeconds / 3600);
  const mins  = Math.floor((totalSeconds % 3600) / 60);
  const secs  = totalSeconds % 60;
  return [hours, mins, secs]
    .map((n) => String(n).padStart(2, "0"))
    .join(":");
}

/**
 * Step 2 — Popup Banner + Floating Ball
 */
function initPopupBanner() {
  const container = document.getElementById("deal-popup-container");
  if (!container) return;

  const banner = container.querySelector(".deal-popup-banner");
  const floatingBall = document.getElementById("floating-deal-ball");
  if (!banner || !floatingBall) return;

  let bannerClosed = localStorage.getItem("gm_popup_closed") === "1";
  let permanentlyClosed = localStorage.getItem("gm_popup_permanently_closed") === "1";

  const countdownEl = banner.querySelector(".popup-countdown");
  const ballCountdownEl = floatingBall.querySelector(".ball-countdown");

  const showBanner = () => {
    banner.style.display = "grid";
    floatingBall.style.display = "none";
    container.style.display = "flex";

    // Smooth entry
    banner.style.animation = 'slideDownIn 0.5s ease-out';

    localStorage.setItem("gm_popup_closed", "0");
    bannerClosed = false;
  };

  const showFloatingBall = () => {
    banner.style.display = "none";
    floatingBall.style.display = "flex";
    container.style.display = "flex";

    // Bouncing entry for ball
    floatingBall.style.animation = 'floatBallIn 0.4s ease-out';

    localStorage.setItem("gm_popup_closed", "1");
    bannerClosed = true;
  };

  const bannerCountdownCallback = (secondsLeft) => {
    if (countdownEl) countdownEl.textContent = formatCountdown(secondsLeft);
    if (ballCountdownEl) ballCountdownEl.textContent = formatCountdown(secondsLeft);

    if (permanentlyClosed || secondsLeft <= 0) {
      container.style.display = "none";
      floatingBall.style.display = "none";
    } else {
        // Keep current state visibility
    }
  };

  registerCountdownCallback(bannerCountdownCallback);
  startGlobalCountdownTick();

  const closeBtn = banner.querySelector(".popup-close");
  if (closeBtn) {
    closeBtn.addEventListener("click", () => {
      showFloatingBall();
    });
  }

  const expandBtn = floatingBall.querySelector(".ball-expand");
  if (expandBtn) {
    expandBtn.addEventListener("click", () => {
      showBanner();
    });
  }

  const ballCloseBtn = floatingBall.querySelector(".ball-close");
  if (ballCloseBtn) {
    ballCloseBtn.addEventListener("click", () => {
      floatingBall.style.display = "none";
      container.style.display = "none";
      localStorage.setItem("gm_popup_permanently_closed", "1");
      permanentlyClosed = true;
    });
  }

  // Restore state
  if (permanentlyClosed || getGlobalCountdownSeconds() <= 0) {
    container.style.display = "none";
    floatingBall.style.display = "none";
  } else if (bannerClosed) {
    banner.style.display = "none";
    floatingBall.style.display = "flex";
    container.style.display = "flex";
  } else {
    banner.style.display = "grid";
    floatingBall.style.display = "none";
    container.style.display = "flex";
  }
}

const DEAL_ENDED_FADE_SECONDS = 60;

function getBadgeEndTime(badge) {
  const endIso = badge.dataset.offerEnd;
  if (endIso) {
    const endTime = new Date(endIso).getTime();
    if (!isNaN(endTime)) return endTime;
  }
  const endsSeconds = Number(badge.dataset.endsSeconds || 0);
  return endsSeconds > 0 ? Date.now() + endsSeconds * 1000 : null;
}

function initLimitedBadges() {
  const updateBadges = () => {
    document.querySelectorAll(".limited-badge").forEach((badge) => {
      const endTime = getBadgeEndTime(badge);

      if (endTime === null) {
        // No offer data at all - hide immediately
        badge.style.display = "none";
        return;
      }

      const now = Date.now();
      const secondsLeft = Math.max(0, Math.floor((endTime - now) / 1000));

      if (secondsLeft > 0) {
        // Offer still active
        badge.textContent = `Ends in ${formatCountdown(secondsLeft)}`;
        badge.style.display = "";
        badge.style.opacity = "1";
        badge.style.transition = "";
        badge.classList.remove("expired");
        delete badge.dataset.endedAt;
      } else {
        // Offer just ended (or already ended) - show "Deal ended" and
        // smoothly fade it out over DEAL_ENDED_FADE_SECONDS, then hide.
        if (!badge.dataset.endedAt) {
          badge.dataset.endedAt = String(endTime);
          badge.textContent = "Deal ended";
          badge.style.display = "";
          badge.style.opacity = "1";
          badge.style.transition = `opacity ${DEAL_ENDED_FADE_SECONDS}s ease-out`;
          badge.classList.add("expired");
          // Trigger fade on next frame so the transition applies
          requestAnimationFrame(() => {
            requestAnimationFrame(() => {
              badge.style.opacity = "0";
            });
          });
        }

        const secondsSinceEnd = Math.floor((now - Number(badge.dataset.endedAt)) / 1000);
        if (secondsSinceEnd >= DEAL_ENDED_FADE_SECONDS) {
          badge.style.display = "none";
        }
      }
    });
  };

  updateBadges();

  if (!badgeUpdateInterval) {
    badgeUpdateInterval = setInterval(updateBadges, 1000);
  }

  // Watch for new badges (lazy-loading)
  const observer = new MutationObserver(() => updateBadges());

  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
}

/**
 * Step 4 — Call Everything
 */
document.addEventListener("DOMContentLoaded", () => {
  initGlobalDealTimer();
  initPopupBanner();
  initLimitedBadges();
});
