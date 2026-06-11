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

/**
 * Step 3 — Limited Badges on Product Cards
 * Uses MutationObserver to handle dynamically loaded or lazy-loaded cards
 */
function initLimitedBadges() {
  let badges = [...document.querySelectorAll(".limited-badge")];

  const updateBadges = (secondsLeft) => {
    // Re-query badges in case DOM changed
    badges = [...document.querySelectorAll(".limited-badge")];
    badges.forEach((badge) => {
      badge.textContent = secondsLeft
        ? `Ends in ${formatCountdown(secondsLeft)}`
        : "Deal ended";
      badge.classList.toggle("expired", secondsLeft === 0);
    });
  };

  registerCountdownCallback(updateBadges);
  startGlobalCountdownTick();

  // Watch for new badges (lazy-loading)
  const observer = new MutationObserver(() => {
    const newBadges = [...document.querySelectorAll(".limited-badge")];
    if (newBadges.length !== badges.length) {
      updateBadges(getGlobalCountdownSeconds());
    }
  });

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
