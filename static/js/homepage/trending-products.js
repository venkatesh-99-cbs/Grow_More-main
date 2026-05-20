document.addEventListener("DOMContentLoaded", () => {
  const wrap = document.getElementById("hero-stat-tabs");
  if (!wrap) return;
  const subtitle = document.getElementById("hero-subtitle");
  const subtitles = [
    "Performance-ready summer essentials for energetic daily wear.",
    "Crafted with breathable natural fibers for cool all-day comfort.",
    "Fast and reliable delivery to keep your season moving.",
  ];
  [...wrap.querySelectorAll(".stat-tab")].forEach((tab, index) => {
    tab.addEventListener("click", () => {
      wrap.querySelectorAll(".stat-tab").forEach((item) => item.classList.remove("active"));
      tab.classList.add("active");
      if (subtitle) subtitle.textContent = subtitles[index] || subtitles[0];
    });
  });
});
