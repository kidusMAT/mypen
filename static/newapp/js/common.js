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
let bookToDelete = null;

function openDeleteModal(bookId, bookTitle) {
    bookToDelete = bookId;
    const titleSpan = document.getElementById('delete-book-title');
    if (titleSpan) titleSpan.textContent = bookTitle;
    const modal = document.getElementById('delete-modal');
    if (modal) modal.style.display = 'flex';
}

function closeDeleteModal() {
    bookToDelete = null;
    const modal = document.getElementById('delete-modal');
    if (modal) modal.style.display = 'none';
}

async function confirmDeleteBook() {
    if (!bookToDelete) return;

    const csrfToken = getCookie('csrftoken');
    if (!csrfToken) {
        showToast("Error: CSRF token missing. Please refresh the page.", "error");
        return;
    }

    try {
        const response = await fetch(`/ajax/delete-book/${bookToDelete}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
            }
        });

        const data = await response.json();

        if (data.status === 'success') {
            closeDeleteModal();
            showToast(data.message, "success");

            // Remove the book card from the DOM
            const bookCard = document.querySelector(`button[onclick*="${bookToDelete}"]`)?.closest('.dashboard-story-card');
            if (bookCard) {
                bookCard.style.opacity = '0';
                bookCard.style.transform = 'translateY(-20px)';
                setTimeout(() => bookCard.remove(), 300);
            }

            bookToDelete = null;
        } else {
            showToast("Failed to delete book: " + data.message, "error");
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
                // Profile comment deletion returns the updated HTML of the comment list
                const container = document.getElementById('drawer-comments-list');
                if (container) {
                    container.innerHTML = data.html;
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
