/**
 * Skeleton UI Loading System
 */

class SkeletonManager {
    static show(containerId, count = 4) {
        const container = document.getElementById(containerId);
        if (!container) return;

        container.dataset.originalContent = container.innerHTML;
        let skeletonHTML = '';

        for (let i = 0; i < count; i++) {
            skeletonHTML += `
            <div class="product-card skeleton-card">
                <div class="product-media skeleton"></div>
                <div class="product-body">
                    <div class="skeleton-line title"></div>
                    <div class="skeleton-line short"></div>
                    <div class="skeleton-line"></div>
                </div>
            </div>`;
        }

        container.innerHTML = skeletonHTML;
    }

    static hide(containerId) {
        const container = document.getElementById(containerId);
        if (container && container.dataset.originalContent) {
            container.innerHTML = container.dataset.originalContent;
        }
    }
}

window.SkeletonManager = SkeletonManager;
