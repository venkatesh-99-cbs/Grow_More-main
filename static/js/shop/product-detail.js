function setDetailImage(index, images, thumbs, dots, main) {
  const next = (index + images.length) % images.length;
  main.classList.add("changing");
  main.src = images[next];
  setTimeout(() => main.classList.remove("changing"), 120);
  thumbs.forEach((thumb) => thumb.classList.toggle("active", Number(thumb.dataset.index) === next));
  dots.forEach((dot) => dot.classList.toggle("active", Number(dot.dataset.dotIndex) === next));
  return next;
}

function initProductSwipe() {
  const main = document.getElementById("detail-main-img");
  if (!main) return;
  const thumbs = [...document.querySelectorAll(".thumb-btn")];
  const dots = [...document.querySelectorAll(".swipe-dot")];
  const images = thumbs.map((thumb) => thumb.dataset.img).filter(Boolean);
  let current = 0;
  let startX = 0;
  let startY = 0;
  thumbs.forEach((thumb) => thumb.addEventListener("click", () => {
    current = setDetailImage(Number(thumb.dataset.index || 0), images, thumbs, dots, main);
  }));
  document.querySelectorAll(".img-nav").forEach((btn) => btn.addEventListener("click", () => {
    let dir = 1;
    if (btn.classList.contains('prev')) dir = -1;
    current = setDetailImage(current + dir, images, thumbs, dots, main);
  }));
  main.addEventListener("touchstart", (event) => {
    startX = event.changedTouches[0].clientX;
    startY = event.changedTouches[0].clientY;
  }, { passive: true });
  main.addEventListener("touchend", (event) => {
    const delta = event.changedTouches[0].clientX - startX;
    if (Math.abs(delta) < 30 || Math.abs(event.changedTouches[0].clientY - startY) > 40) return;
    current = setDetailImage(delta < 0 ? current + 1 : current - 1, images, thumbs, dots, main);
  }, { passive: true });
}

function initQuantity() {
  document.querySelectorAll(".qty-btn").forEach((button) => {
    button.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      const input = document.getElementById("detail-qty");
      const value = Number(input.value || 1);
      const newValue = button.dataset.action === "plus" ? value + 1 : Math.max(1, value - 1);
      input.value = newValue;
      // Also update any other quantity inputs if they exist (though on detail there should only be one)
    });
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initProductSwipe();
  initQuantity();
});
