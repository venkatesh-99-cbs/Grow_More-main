import { initOfferCountdowns } from "./countdown-manager.js";
import { initFloatingBall } from "./floating-ball.js";
import { getEmbeddedOffer } from "./offer-service.js";
import { initOfferPopup } from "./popup-banner.js";
import { initProductOffers } from "./product-offers.js";

class HomepageOfferSlider {
    constructor() {
        this.container = document.getElementById('offer-slides-container');
        if (!this.container) return;

        this.slides = [...this.container.querySelectorAll('.offer-slide-item')];
        this.current = 0;
        this.init();
    }

    init() {
        if (this.slides.length > 1) {
            this.createIndicators();
            this.bindNav();
            this.autoPlay();
        }
        this.initTimers();
    }

    createIndicators() {
        const nav = document.querySelector('.offer-nav');
        if (!nav) return;
        const dotsContainer = document.createElement('div');
        dotsContainer.className = 'offer-dots';
        this.slides.forEach((_, idx) => {
            const dot = document.createElement('span');
            dot.className = 'offer-dot' + (idx === 0 ? ' active' : '');
            dot.addEventListener('click', () => {
                this.showSlide(idx);
                clearInterval(this.playInterval);
                this.autoPlay();
            });
            dotsContainer.appendChild(dot);
        });
        nav.insertBefore(dotsContainer, nav.querySelector('.nav-next'));
    }

    bindNav() {
        document.querySelector('.nav-prev')?.addEventListener('click', () => this.showSlide(this.current - 1));
        document.querySelector('.nav-next')?.addEventListener('click', () => this.showSlide(this.current + 1));
    }

    showSlide(n) {
        this.slides[this.current].classList.remove('active');
        this.current = (n + this.slides.length) % this.slides.length;
        this.slides[this.current].classList.add('active');
        this.updateIndicators();
    }

    autoPlay() {
        this.playInterval = setInterval(() => this.showSlide(this.current + 1), 8000);
    }

    updateIndicators() {
        const dots = document.querySelectorAll('.offer-dot');
        dots.forEach((dot, idx) => {
            dot.classList.toggle('active', idx === this.current);
        });
    }

    initTimers() {
        const update = () => {
            document.querySelectorAll('.offer-timer').forEach(timer => {
                const ends = new Date(timer.dataset.ends);
                const now = new Date();
                const diff = ends - now;

                if (diff <= 0) {
                    timer.innerHTML = 'OFFER EXPIRED';
                    return;
                }

                const hrs = Math.floor(diff / (1000 * 60 * 60));
                const mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
                const secs = Math.floor((diff % (1000 * 60)) / 1000);

                const vals = timer.querySelectorAll('.timer-val');
                if (vals.length === 3) {
                    vals[0].textContent = String(hrs).padStart(2, '0');
                    vals[1].textContent = String(mins).padStart(2, '0');
                    vals[2].textContent = String(secs).padStart(2, '0');
                }
            });
        };

        update();
        setInterval(update, 1000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const offer = getEmbeddedOffer();
    initOfferPopup(offer);
    initFloatingBall(offer);
    initProductOffers();
    initOfferCountdowns();
    new HomepageOfferSlider();
});
