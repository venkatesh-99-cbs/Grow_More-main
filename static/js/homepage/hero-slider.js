function initHeroSlider() {
  const slides = [...document.querySelectorAll(".hero-slide")];
  if (!slides.length) return;

  let i = 0;

  setInterval(() => {
    slides[i].classList.remove("active");
    i = (i + 1) % slides.length;
    slides[i].classList.add("active");
  }, 4200); // change interval here (milliseconds)
}

function initHeroStatTabs() {
  const wrap = document.getElementById("hero-stat-tabs");
  if (!wrap) return;

  const subtitle = document.getElementById("hero-subtitle");

  // One entry per stat tab — must match tab order in HTML
  const subtitleMap = [
    "Performance-ready summer essentials for energetic daily wear.",
    "Crafted with breathable natural fibers for cool all-day comfort.",
    "Fast and reliable delivery to keep your season moving.",
  ];

  const tabs = [...wrap.querySelectorAll(".stat-tab")];

  tabs.forEach((tab, index) => {
    tab.addEventListener("click", () => {
      tabs.forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");
      if (subtitle) subtitle.textContent = subtitleMap[index] || subtitleMap[0];
    });
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initHeroSlider();      // starts the auto-slide
  initHeroStatTabs();    // wires the stat tab clicks
});
