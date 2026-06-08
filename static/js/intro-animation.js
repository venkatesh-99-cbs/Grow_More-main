/**
 * Cinematic Website Intro Animation
 */

class IntroAnimation {
    constructor() {
        this.intro = document.getElementById('intro-animation');
        this.hasSeenIntro = sessionStorage.getItem('hasSeenIntro');
        this.init();
    }

    init() {
        if (!this.intro) return;

        if (this.hasSeenIntro) {
            this.intro.remove();
            document.body.style.overflow = '';
            return;
        }

        this.animate();
    }

    animate() {
        document.body.style.overflow = 'hidden';

        setTimeout(() => {
            if (this.intro) this.intro.classList.add('phase-2');
        }, 1500);

        setTimeout(() => {
            this.finishAnimation();
        }, 3000);

        const skipBtn = this.intro.querySelector('.intro-skip');
        if (skipBtn) {
            skipBtn.onclick = (e) => {
                e.preventDefault();
                this.finishAnimation();
            };
        }
    }

    finishAnimation() {
        if (!this.intro) return;

        this.intro.classList.add('intro-exit-process');
        document.body.style.overflow = '';
        sessionStorage.setItem('hasSeenIntro', 'true');

        setTimeout(() => {
            this.intro.remove();
        }, 1000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new IntroAnimation();
});
