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

// Toast Notification System
function showToast(message, type = 'success', duration = 3000) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    let icon = 'checkmark-circle';
    if (type === 'error') icon = 'alert-circle';
    if (type === 'info') icon = 'information-circle';

    toast.innerHTML = `
        <ion-icon name="${icon}"></ion-icon>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    // Auto remove
    setTimeout(() => {
        toast.classList.add('fade-out');
        setTimeout(() => toast.remove(), 300);
    }, duration);
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
