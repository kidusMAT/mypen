// Helper to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Deletion Logic
let itemToDeleteId = null;
let itemToDeleteType = null;

function openDeleteModal(type, itemId, itemTitle) {
    itemToDeleteType = type;
    itemToDeleteId = itemId;
    const titleSpan = document.getElementById('delete-book-title');
    if (titleSpan) titleSpan.textContent = itemTitle;
    const modal = document.getElementById('delete-modal');
    if (modal) modal.style.display = 'flex';
}

function closeDeleteModal() {
    itemToDeleteId = null;
    itemToDeleteType = null;
    const modal = document.getElementById('delete-modal');
    if (modal) modal.style.display = 'none';
}

async function confirmDeleteContent() {
    if (!itemToDeleteId || !itemToDeleteType) return;

    // Capture values before closeDeleteModal() nullifies them
    const typeToDelete = itemToDeleteType;
    const idToDelete = itemToDeleteId;

    const csrfToken = getCookie('csrftoken');
    if (!csrfToken) {
        showToast("Error: CSRF token missing. Please refresh the page.", "error");
        return;
    }

    try {
        const response = await fetch(`/ajax/delete-${typeToDelete}/${idToDelete}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
            }
        });

        const data = await response.json();

        if (data.status === 'success') {
            closeDeleteModal();
            showToast(data.message, "success");

            // Remove the card from the DOM using the specific ID we added
            const cardId = `${typeToDelete}-card-${idToDelete}`;
            const card = document.getElementById(cardId);
            if (card) {
                card.style.opacity = '0';
                card.style.transform = 'translateY(-20px) scale(0.95)';
                card.style.transition = 'opacity 0.3s, transform 0.3s';
                setTimeout(() => card.remove(), 300);
            }
        } else {
            showToast(`Failed to delete ${typeToDelete}: ` + data.message, "error");
        }
    } catch (error) {
        console.error("Delete failed:", error);
        showToast("Request failed. Please check your connection.", "error");
    }
}


async function deleteComment(commentId, type) {
    const confirmed = await showCustomConfirm({
        title: 'Delete Comment',
        message: 'Are you sure you want to delete this comment?',
        type: 'danger',
        confirmText: 'Delete'
    });
    if (!confirmed) return;

    const csrfToken = getCookie('csrftoken');
    const url = `/ajax/reviews/${type === 'movie' ? 'movie' : 'book'}/comment/${commentId}/delete/`;

    fetch(url, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken
        }
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const commentEl = document.getElementById(`${type}-comment-${commentId}`);
                if (commentEl) {
                    commentEl.style.transition = 'opacity 0.3s, transform 0.3s';
                    commentEl.style.opacity = '0';
                    commentEl.style.transform = 'translateY(-10px)';
                    setTimeout(() => commentEl.remove(), 300);
                }

                // Update counts (works for both list and detail pages if IDs match)
                const countId = type === 'movie' ? `movie-comment-count-${data.movie_id}` : `book-comment-count-${data.book_review_id}`;
                const countEl = document.getElementById(countId);
                if (countEl) countEl.innerText = data.comment_count;

                const totalCountEl = document.getElementById('comments-total-count');
                if (totalCountEl) totalCountEl.innerText = data.comment_count;

                showToast("Comment deleted", "info");
            }
        })
        .catch(err => console.error('Error deleting comment:', err));
}

async function deleteProfileComment(commentId) {
    const confirmed = await showCustomConfirm({
        title: 'Delete Comment',
        message: 'Are you sure you want to delete this profile comment?',
        type: 'danger',
        confirmText: 'Delete'
    });
    if (!confirmed) return;

    const csrfToken = getCookie('csrftoken');
    fetch(`/ajax/profile/comment/${commentId}/delete/`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken
        }
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const commentEl = document.getElementById(`comment-${commentId}`);
                if (commentEl) {
                    commentEl.style.transition = 'all 0.4s ease';
                    commentEl.style.opacity = '0';
                    commentEl.style.maxHeight = '0';
                    commentEl.style.paddingTop = '0';
                    commentEl.style.paddingBottom = '0';
                    commentEl.style.marginTop = '0';
                    commentEl.style.marginBottom = '0';
                    commentEl.style.overflow = 'hidden';

                    setTimeout(() => {
                        const drawerContainer = document.getElementById('comment-drawer-content');
                        if (drawerContainer) {
                            drawerContainer.innerHTML = data.html;
                        } else {
                            commentEl.remove();
                        }
                    }, 400);
                } else {
                    const container = document.getElementById('comment-drawer-content');
                    if (container) container.innerHTML = data.html;
                }

                if (data.comment_count !== undefined && data.username !== undefined) {
                    const badge = document.getElementById('author-comment-count-' + data.username);
                    if (badge) badge.innerText = data.comment_count;
                }
                showToast("Comment deleted", "info");
            }
        });
}

async function deleteConfession(id) {
    const confirmed = await showCustomConfirm({
        title: 'Delete Confession',
        message: 'Are you sure you want to delete this confession?',
        type: 'danger',
        confirmText: 'Delete'
    });
    if (!confirmed) return;

    const csrfToken = getCookie('csrftoken');
    fetch(`/ajax/confessions/${id}/delete/`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken
        }
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const el = document.getElementById(`confession-${id}`);
                if (el) {
                    el.style.opacity = '0';
                    el.style.transform = 'scale(0.9)';
                    el.style.transition = '0.3s';
                    setTimeout(() => el.remove(), 300);
                }
                showToast("Confession deleted", "info");
            } else {
                showToast(data.message || 'Error deleting confession', 'error');
            }
        });
}

async function deleteConfessionComment(commentId, confessionId) {
    const confirmed = await showCustomConfirm({
        title: 'Delete Comment',
        message: 'Are you sure you want to delete this comment?',
        type: 'danger',
        confirmText: 'Delete'
    });
    if (!confirmed) return;

    const csrfToken = getCookie('csrftoken');
    fetch(`/ajax/confessions/comment/${commentId}/delete/`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken
        }
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const el = document.getElementById(`confession-comment-${commentId}`);
                if (el) {
                    el.style.opacity = '0';
                    el.style.transition = '0.3s';
                    setTimeout(() => el.remove(), 300);
                }
                showToast("Comment deleted", "info");
            } else {
                showToast(data.message || 'Error deleting comment', 'error');
            }
        });
}

async function deleteMovie(id) {
    const confirmed = await showCustomConfirm({
        title: 'Delete Movie',
        message: 'Are you sure you want to delete this movie review?',
        type: 'danger',
        confirmText: 'Delete'
    });
    if (!confirmed) return;

    const csrfToken = getCookie('csrftoken');
    fetch(`/ajax/movie/${id}/delete/`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken
        }
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const el = document.getElementById(`movie-card-${id}`);
                if (el) {
                    el.style.opacity = '0';
                    el.style.transform = 'scale(0.9)';
                    el.style.transition = '0.3s';
                    setTimeout(() => el.remove(), 300);
                } else if (window.location.pathname.includes(`/reviews/movie/${id}/`)) {
                    showToast("Movie deleted. Redirecting...", "info");
                    setTimeout(() => window.location.href = '/reviews/', 1000);
                }
                showToast("Movie deleted", "info");
            } else {
                showToast(data.message || 'Error deleting movie', 'error');
            }
        });
}

async function deleteBookReview(id) {
    const confirmed = await showCustomConfirm({
        title: 'Delete Review',
        message: 'Are you sure you want to delete this book review?',
        type: 'danger',
        confirmText: 'Delete'
    });
    if (!confirmed) return;

    const csrfToken = getCookie('csrftoken');
    fetch(`/ajax/book-review/${id}/delete/`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken
        }
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const el = document.getElementById(`book-card-${id}`);
                if (el) {
                    el.style.opacity = '0';
                    el.style.transform = 'scale(0.9)';
                    el.style.transition = '0.3s';
                    setTimeout(() => el.remove(), 300);
                } else if (window.location.pathname.includes(`/reviews/book/${id}/`)) {
                    showToast("Review deleted. Redirecting...", "info");
                    setTimeout(() => window.location.href = '/reviews/', 1000);
                }
                showToast("Book review deleted", "info");
            } else {
                showToast(data.message || 'Error deleting review', 'error');
            }
        });
}
// --- Global Reveal Animations ---
window.initRevealAnimations = function (container = document) {
    const reveals = container.querySelectorAll('.reveal, .reveal-left, .reveal-right, .reveal-scale');

    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
                revealObserver.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    reveals.forEach(reveal => {
        revealObserver.observe(reveal);
    });
};

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    window.initRevealAnimations();
});

// Global Toast System
window.showToast = function (message, type = 'success', duration = 3000) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    let icon = 'fa-circle-check';
    let iconColor = '#22c55e';
    if (type === 'error') {
        icon = 'fa-circle-exclamation';
        iconColor = '#ef4444';
    } else if (type === 'info') {
        icon = 'fa-circle-info';
        iconColor = '#3b82f6';
    }

    toast.innerHTML = `<i class="fa-solid ${icon}" style="color: ${iconColor};"></i> <span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('fade-out');
        setTimeout(() => toast.remove(), 500);
    }, duration);
}

// Global Custom Alert/Confirm System
window.showCustomConfirm = function (options) {
    const overlay = document.getElementById('custom-alert-overlay');
    const modal = document.getElementById('custom-alert-modal');
    const titleEl = document.getElementById('custom-alert-title');
    const messageEl = document.getElementById('custom-alert-message');
    const cancelBtn = document.getElementById('custom-alert-cancel');
    const confirmBtn = document.getElementById('custom-alert-confirm');
    const iconBox = document.getElementById('custom-alert-icon');

    // If the overlay doesn't exist on the page (e.g. write.html without it), fallback
    if (!overlay) {
        return new Promise((resolve) => {
            const result = confirm(options.title + '\n' + options.message);
            resolve(result);
        });
    }

    titleEl.textContent = options.title || 'Are you sure?';
    messageEl.textContent = options.message || 'This action cannot be undone.';
    confirmBtn.textContent = options.confirmText || 'Confirm';
    cancelBtn.textContent = options.cancelText || 'Cancel';

    if (options.type === 'danger') {
        iconBox.style.background = 'rgba(239, 68, 68, 0.1)';
        iconBox.style.color = '#ef4444';
        iconBox.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i>';
        confirmBtn.style.background = '#ef4444';
    } else {
        iconBox.style.background = 'rgba(17, 17, 17, 0.1)';
        iconBox.style.color = '#111';
        iconBox.innerHTML = '<i class="fa-solid fa-circle-question"></i>';
        confirmBtn.style.background = '#111';
    }

    overlay.style.display = 'flex';
    setTimeout(() => {
        overlay.style.opacity = '1';
        modal.style.transform = 'scale(1)';
    }, 10);

    const close = () => {
        overlay.style.opacity = '0';
        modal.style.transform = 'scale(0.9)';
        setTimeout(() => {
            overlay.style.display = 'none';
        }, 300);
    };

    return new Promise((resolve) => {
        confirmBtn.onclick = () => {
            close();
            resolve(true);
        };
        cancelBtn.onclick = () => {
            close();
            resolve(false);
        };
        overlay.onclick = (e) => {
            if (e.target === overlay) {
                close();
                resolve(false);
            }
        };
    });
};
