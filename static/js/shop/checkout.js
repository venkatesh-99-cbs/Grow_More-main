import { validateStep, preventDoubleSubmit } from "../services/validation-service.js";

function initCheckoutSteps() {
  const form = document.getElementById("checkout-form");
  if (!form) return;
  const steps = [...document.querySelectorAll(".step")];
  const showStep = (n) => {
    steps.forEach((step) => step.classList.toggle("active", Number(step.dataset.step) === n));
    document.querySelectorAll(".step-dot").forEach((dot) => {
      const value = Number(dot.dataset.step);
      dot.classList.toggle("active", value === n);
      dot.classList.toggle("done", value < n);
    });
  };
  document.getElementById("to-payment")?.addEventListener("click", () => {
    if (validateStep(form.querySelector(".step[data-step='1']"))) showStep(2);
  });
  document.getElementById("to-review")?.addEventListener("click", () => {
    if (!validateStep(form.querySelector(".step[data-step='2']"))) return;
    const review = document.getElementById("review-block");
    const method = form.payment_method.value === 'razorpay' ? 'Razorpay (Online)' : 'Cash on Delivery';
    review.innerHTML = `
      <div class="review-details">
        <div class="review-group">
          <label>Contact Info</label>
          <p><strong>${form.full_name.value}</strong></p>
          <p>${form.email.value}</p>
          <p>${form.phone.value}</p>
        </div>
        <div class="review-group">
          <label>Shipping To</label>
          <p>${form.shipping_address.value}</p>
          <p>${form.shipping_city.value}, ${form.shipping_state.value} ${form.shipping_postal_code.value}</p>
        </div>
        <div class="review-group">
          <label>Payment Method</label>
          <p>${method}</p>
        </div>
      </div>
    `;
    showStep(3);
  });
  document.getElementById("back-shipping")?.addEventListener("click", () => showStep(1));
  document.getElementById("back-payment")?.addEventListener("click", () => showStep(2));
  preventDoubleSubmit(form);
}

function initRazorpay() {
  const button = document.getElementById("pay-button");
  if (!button || !window.Razorpay) return;
  button.addEventListener("click", () => {
    const options = {
      key: button.dataset.key,
      amount: Math.round(Number(button.dataset.amount) * 100),
      currency: "INR",
      name: "Grow More",
      description: "Premium menswear order",
      order_id: button.dataset.order,
      prefill: { name: button.dataset.name, email: button.dataset.email, contact: button.dataset.phone },
      handler(response) {
        document.getElementById("razorpay_payment_id").value = response.razorpay_payment_id;
        document.getElementById("razorpay_signature").value = response.razorpay_signature;
        document.getElementById("razorpay-form").submit();
      },
    };
    new window.Razorpay(options).open();
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initCheckoutSteps();
  initRazorpay();
});
