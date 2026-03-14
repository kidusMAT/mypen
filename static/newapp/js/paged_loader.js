function initPagedLoader() {
    console.log("Paged Loader: Initializing listeners...");
    const loaderBtns = document.querySelectorAll('[data-paged-loader]');
    console.log("Paged Loader: Found " + loaderBtns.length + " loader buttons.");

    loaderBtns.forEach(btn => {
        // Prevent double binding
        if (btn.dataset.isBound) return;
        btn.dataset.isBound = "true";

        console.log("Paged Loader: Attaching listener to button:", btn.id || btn.innerText);
        
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log("Paged Loader: Button clicked!", this);

            if (this.classList.contains('is-loading')) {
                console.log("Paged Loader: Already loading, ignoring.");
                return;
            }
            this.classList.add('is-loading');

            const page = parseInt(this.getAttribute('data-page') || '2');
            const targetSelector = this.getAttribute('data-append-target');
            const targetContainer = document.querySelector(targetSelector);
            const hideSelector = this.getAttribute('data-hide-selector');
            const hideContainer = hideSelector ? document.querySelector(hideSelector) : this.parentElement;
            const loadingText = this.getAttribute('data-loading-text') || 'Loading...';
            const originalText = this.getAttribute('data-done-text') || this.innerText;
            const extraParams = this.getAttribute('data-extra-params') || '';
            const genre = this.getAttribute('data-genre') || '';

            if (!targetContainer) {
                console.error("Paged Loader: Target container not found:", targetSelector);
                this.classList.remove('is-loading');
                return;
            }

            this.innerText = loadingText;

            let currentPath = window.location.pathname;
            let urlParams = new URLSearchParams(window.location.search);
            urlParams.set('page', page);
            urlParams.set('ajax', '1');
            if (genre) urlParams.set('genre', genre);

            let finalUrl = `${currentPath}?${urlParams.toString()}${extraParams}`;
            console.log("Paged Loader: Fetching:", finalUrl);

            fetch(finalUrl, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok');
                const hasNext = response.headers.get('X-Has-Next');
                if (hasNext === 'false') {
                    if (hideContainer) hideContainer.style.display = 'none';
                    else this.style.display = 'none';
                }
                return response.text();
            })
            .then(html => {
                if (!html.trim()) {
                    if (hideContainer) hideContainer.style.display = 'none';
                    else this.style.display = 'none';
                    return;
                }

                targetContainer.insertAdjacentHTML('beforeend', html);
                this.setAttribute('data-page', page + 1);
                
                // Re-trigger reveal animations if function exists
                if (typeof window.initRevealAnimations === 'function') {
                    window.initRevealAnimations(targetContainer);
                }
            })
            .catch(err => {
                console.error('Paged Loader: Error:', err);
                if (window.showToast) window.showToast('Failed to load more items.', 'error');
            })
            .finally(() => {
                this.classList.remove('is-loading');
                this.innerText = originalText;
            });
        });
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPagedLoader);
} else {
    initPagedLoader();
}

