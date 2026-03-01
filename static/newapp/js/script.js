// Variable to track which mode is currently active (story, poem, script)
let currentMode = 'story';
// Variable to track current active chapter ID (for story mode)
let activeChapterId = null;

document.addEventListener('DOMContentLoaded', () => {
    activeChapterId = document.querySelector('input[name="chapter_id"]')?.value;
    console.log("DEBUG: Initial activeChapterId:", activeChapterId);

    // Prevent focus loss on toolbar buttons
    document.querySelectorAll('.customize label').forEach(label => {
        label.addEventListener('mousedown', (e) => {
            e.preventDefault();
        });
    });
});


// Function to switch between Story, Poem, and Script
function switchMode(type) {
    currentMode = type;

    // Toggle Form Visibility
    document.querySelectorAll('.formcont form').forEach(form => {
        form.classList.remove('active');
        form.style.display = 'none';
    });

    const targetForm = document.getElementById('Form-' + type);
    if (targetForm) {
        targetForm.classList.add('active');
        targetForm.style.display = 'flex';
    }

    // Update Tab Styling
    document.querySelectorAll('.mode-tab').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.btn-mode-' + type).forEach(btn => btn.classList.add('active'));

    // Toggle Chapter Controls & Separators (Story Only)
    const chapterControls = document.querySelector('.chapterc');
    const chapterSeparators = document.querySelectorAll('.chapter-separator');

    if (type === 'story') {
        if (chapterControls) chapterControls.style.display = 'flex';
        chapterSeparators.forEach(s => s.style.display = 'flex');
    } else {
        if (chapterControls) chapterControls.style.display = 'none';
        chapterSeparators.forEach(s => s.style.display = 'none');
    }

    updatePageIndicators();

    // Initialize poem editor if empty
    if (type === 'poem') {
        const editor = document.getElementById('editor-poem');
        if (editor && editor.innerText.trim() === '') {
            editor.innerHTML = '<div class="poem-line"><br></div>';
        }
        document.body.classList.add('poem-mode');
        document.body.classList.remove('script-mode');
    } else if (type === 'script') {
        document.body.classList.add('script-mode');
        document.body.classList.remove('poem-mode');
    } else {
        document.body.classList.remove('poem-mode');
        document.body.classList.remove('script-mode');
    }
}




// Function to format text (Bold, Italic, Underline, Strikethrough)
function formatText(command) {
    // Ensure the correct editor is focused before executing
    const activeForm = document.querySelector('.formcont form.active');
    if (activeForm) {
        const editor = activeForm.querySelector('.editor-content');
        if (editor) {
            // Restore selection if lost (optional, but focus helps)
            editor.focus();
        }
    }
    document.execCommand(command, false, null);
    updateToolbarState();
}

// Function to align text
function alignText(alignment) {
    document.execCommand('justify' + alignment.charAt(0).toUpperCase() + alignment.slice(1), false, null);


    const activeForm = document.querySelector('.formcont form.active');
    if (activeForm) {
        const activeEditor = activeForm.querySelector('.editor-content');
        if (activeEditor) activeEditor.focus();
    }
    updateToolbarState();
}

// Helper to save selection state
function saveSelection(containerEl) {
    const range = window.getSelection().getRangeAt(0);
    const preSelectionRange = range.cloneRange();
    preSelectionRange.selectNodeContents(containerEl);
    preSelectionRange.setEnd(range.startContainer, range.startOffset);
    return preSelectionRange.toString().length;
}

// Helper to restore selection state
function restoreSelection(containerEl, savedSelection) {
    let charIndex = 0;
    const range = document.createRange();
    range.setStart(containerEl, 0);
    range.collapse(true);
    const nodeStack = [containerEl];
    let node, foundStart = false, stop = false;

    while (!stop && (node = nodeStack.pop())) {
        if (node.nodeType === 3) {
            const nextCharIndex = charIndex + node.length;
            if (!foundStart && savedSelection >= charIndex && savedSelection <= nextCharIndex) {
                range.setStart(node, savedSelection - charIndex);
                range.setEnd(node, savedSelection - charIndex);
                stop = true;
            }
            charIndex = nextCharIndex;
        } else {
            let i = node.childNodes.length;
            while (i--) {
                nodeStack.push(node.childNodes[i]);
            }
        }
    }

    const sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(range);
}

// Sync contenteditable div to hidden input for saving
function syncEditor(editorId, hiddenId) {
    const editor = document.getElementById(editorId);
    const hidden = document.getElementById(hiddenId);
    if (editor && hidden) {
        // Clone and strip dividers before saving
        const clone = editor.cloneNode(true);
        clone.querySelectorAll('.page-divider').forEach(d => d.remove());
        hidden.value = clone.innerHTML;
    }
    updatePageIndicators();
}

// Global variable to track consecutive enters for Poem mode
let poemEnterSessionCount = 0;

function getActiveEditor() {
    if (currentMode === 'script') return document.getElementById('editor-script');
    if (currentMode === 'poem') return document.getElementById('editor-poem');
    return document.querySelector('.Story.active .editor-content') || document.querySelector('.editor-content');
}

// Helper to update all page indicators
function updatePageIndicators() {
    let totalPages = 1;

    const editor = getActiveEditor();
    if (!editor) return;

    // Use a clean text for counting
    const text = (editor.innerText || "").trim();

    if (currentMode === 'script') {
        const lines = text.split(/\r\n|\r|\n/).filter(l => l.trim().length > 0 || l === '').length;
        const blocks = editor.querySelectorAll('div, p').length;
        const totalLines = Math.max(lines, blocks);
        totalPages = Math.max(1, Math.ceil(totalLines / 55)); // Screenplay ~55 lines/page (A4)
        console.log(`DEBUG: Script Page Count - Lines: ${lines}, Blocks: ${blocks}, Total: ${totalPages}`);
    } else if (currentMode === 'poem') {
        const sections = editor.querySelectorAll('.poem-sub-name').length;
        const lines = text.split('\n').length;
        totalPages = Math.max(1, Math.max(sections, Math.ceil(lines / 40)));
    } else {
        const words = text.split(/\s+/).filter(w => w.length > 0).length;
        totalPages = Math.max(1, Math.ceil(words / 300)); // 300 words/page
        console.log(`DEBUG: Story Page Count - Words: ${words}, Total: ${totalPages}`);
    }

    // Update Indicators
    const headerVal = document.getElementById('page-count-val');
    if (headerVal) headerVal.innerText = `Page ${totalPages}`;

    const floatVal = document.getElementById('floating-page-val');
    if (floatVal) floatVal.innerText = `Page ${totalPages}`;

    const floatContainer = document.getElementById('floating-page-indicator');
    if (floatContainer) {
        floatContainer.style.display = 'flex';
        floatContainer.style.opacity = '1';
    }

    // Debounce the divider check to avoid cursor jumping
    clearTimeout(dividerTimer);
    dividerTimer = setTimeout(checkPageDividers, 1500);
}

let dividerTimer = null;

// Function to insert visual dividers
function checkPageDividers() {
    const editor = getActiveEditor();
    if (!editor) return;

    // Remove existing dividers to recalculate
    editor.querySelectorAll('.page-divider').forEach(d => d.remove());

    const children = Array.from(editor.children);
    let lineCount = 0;
    let wordCount = 0;
    const linesPerPage = 55;
    const wordsPerPage = 300;

    children.forEach((child, index) => {
        if (currentMode === 'script') {
            lineCount++;
            if (lineCount >= linesPerPage) {
                const divider = document.createElement('div');
                divider.className = 'page-divider';
                divider.contentEditable = "false";
                child.after(divider);
                lineCount = 0;
            }
        } else if (currentMode === 'poem') {
            // Poems divide by sections or length
            if (child.classList.contains('poem-sub-name') && index > 0) {
                const divider = document.createElement('div');
                divider.className = 'page-divider';
                divider.contentEditable = "false";
                child.before(divider);
            }
        } else {
            // Story / Book
            const words = (child.innerText || "").trim().split(/\s+/).length;
            wordCount += words;
            if (wordCount >= wordsPerPage) {
                const divider = document.createElement('div');
                divider.className = 'page-divider';
                divider.contentEditable = "false";
                child.after(divider);
                wordCount = 0;
            }
        }
    });
}

// Update toolbar button highlights based on current selection
function updateToolbarState() {
    const states = {
        'bold': document.queryCommandState('bold'),
        'italic': document.queryCommandState('italic'),
        'underline': document.queryCommandState('underline'),
        'strike': document.queryCommandState('strikeThrough'),
        'justifyLeft': document.queryCommandState('justifyLeft'),
        'justifyCenter': document.queryCommandState('justifyCenter'),
        'justifyRight': document.queryCommandState('justifyRight')
    };

    // Sync formatting checkboxes
    if (document.getElementById('check-bold')) document.getElementById('check-bold').checked = states.bold;
    if (document.getElementById('check-italic')) document.getElementById('check-italic').checked = states.italic;
    if (document.getElementById('check-underline')) document.getElementById('check-underline').checked = states.underline;
    if (document.getElementById('check-strike')) document.getElementById('check-strike').checked = states.strike;

    // Sync alignment radio buttons
    if (states.justifyLeft && document.getElementById('align-left')) document.getElementById('align-left').checked = true;
    if (states.justifyCenter && document.getElementById('align-center')) document.getElementById('align-center').checked = true;
    if (states.justifyRight && document.getElementById('align-right')) document.getElementById('align-right').checked = true;
}

// Listen for selection and typing to update toolbar
document.addEventListener('selectionchange', updateToolbarState);
document.addEventListener('keyup', updateToolbarState);
document.addEventListener('mouseup', updateToolbarState);

// Function to activate a specific chapter section (Story mode only)
function activateChapter(id) {
    if (currentMode !== 'story') return;
    activeChapterId = id;
    document.querySelectorAll('.Story').forEach(form => {
        form.classList.remove('active');
        if (form.querySelector(`input[name="chapter_id"][value="${id}"]`)) {
            form.classList.add('active');
        }
    });
}

// Global click listener to track active chapter based on focus
document.addEventListener('focusin', (e) => {
    if (currentMode !== 'story') return;
    if (e.target.classList.contains('editor-content') || e.target.tagName === 'INPUT') {
        const form = e.target.closest('form.Story');
        if (form) {
            const id = form.querySelector('input[name="chapter_id"]')?.value;
            if (id && id !== activeChapterId) {
                activateChapter(id);
            }
        }
    }
});

async function saveChapterAjax(chapterId, status = 'DRAFT') {
    console.log("DEBUG: saveChapterAjax for:", chapterId, status);
    const selector = currentMode === 'story'
        ? `form.Story input[name="chapter_id"][value="${chapterId}"]`
        : `form.${currentMode.charAt(0).toUpperCase() + currentMode.slice(1)}`;

    const form = document.querySelector(selector)?.closest('form');
    if (!form) return false;

    // Explicitly sync before saving to ensure we have the latest content
    const editor = form.querySelector('.editor-content');
    const hidden = form.querySelector('input[name="thestory"]');
    if (editor && hidden) {
        hidden.value = editor.innerHTML;
    }
    const hiddenInput = form.querySelector('input[name="thestory"]');
    const content = hiddenInput ? hiddenInput.value : "";
    const titleInput = form.querySelector('input.cn');
    const title = titleInput ? titleInput.value : null;

    const csrfToken = getCookie('csrftoken');
    if (!csrfToken) {
        console.error("CSRF token not found!");
        showToast("Error: CSRF token missing. Please refresh the page.", "error");
        return false;
    }

    console.log(`DEBUG: Saving chapter ${chapterId} with status ${status}...`);

    try {
        const response = await fetch(`/ajax/save-chapter/${chapterId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify({ content, title, status })
        });
        const data = await response.json();
        if (data.status === 'success') {
            console.log(`DEBUG: Chapter ${chapterId} saved successfully.`);
            if (status === 'DRAFT') {
                showToast("Your work is saved");
            }
            return true;
        } else {
            console.error(`DEBUG: Save failed for chapter ${chapterId}:`, data.message);
            showToast(`Save failed: ${data.message}`, "error");
            return false;
        }
    } catch (error) {
        console.error(`Save failed:`, error);
        showToast(`Request failed. Check console for details.`, "error");
    }
    return false;
}

async function endChapter() {
    if (!activeChapterId) return;
    const success = await saveChapterAjax(activeChapterId, 'DRAFT');
    if (success) {
        const form = document.querySelector(`form.Story input[name="chapter_id"][value="${activeChapterId}"]`)?.closest('form');
        if (form) {
            const separator = document.createElement('div');
            separator.className = 'chapter-separator';
            separator.innerHTML = '<span>Chapter Saved & Closed</span>';
            form.after(separator);
            form.classList.add('finished');
            showToast("Chapter ended and saved successfully!", "success");
        }
    }
}

async function nextChapter(bookId) {
    if (!activeChapterId) {
        console.error("No activeChapterId found for nextChapter");
        return;
    }

    console.log(`DEBUG: nextChapter called for book ${bookId}, current chapter ${activeChapterId}`);

    // 1. Save current chapter
    const saveSuccess = await saveChapterAjax(activeChapterId, 'DRAFT');
    if (!saveSuccess) {
        console.error("Failed to save current chapter before adding next one.");
        return;
    }

    // 2. Add visual marker
    const currentForm = document.querySelector(`form.Story input[name="chapter_id"][value="${activeChapterId}"]`)?.closest('form');
    if (!currentForm) {
        console.error("Could not find current form to append next chapter after.");
        return;
    }

    // 3. Create new chapter in DB
    try {
        const csrfToken = getCookie('csrftoken');
        const response = await fetch(`/ajax/add-chapter/${bookId}/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': csrfToken }
        });
        const data = await response.json();
        if (data.status === 'success') {
            console.log("DEBUG: New chapter created:", data.chapter_id);
            const separator = document.createElement('div');
            separator.className = 'chapter-separator';
            separator.innerHTML = '<span>Previous Chapter Ends Here</span>';
            currentForm.after(separator);

            // 4. Append new form
            const newForm = createChapterForm(data.chapter_id, data.title);
            separator.after(newForm);

            // 5. Activate and focus
            activateChapter(data.chapter_id);
            newForm.querySelector('.editor-content').focus();
            newForm.scrollIntoView({ behavior: 'smooth', block: 'center' });
            showToast("New chapter created successfully!", "success");
        } else {
            console.error("Failed to create next chapter:", data.message);
            showToast(`Could not create next chapter: ${data.message}`, "error");
        }
    } catch (error) {
        console.error('Failed to add chapter:', error);
        showToast("Request to add chapter failed. See console.", "error");
    }
}

function createChapterForm(id, title) {
    const form = document.createElement('form');
    form.className = 'Story active dynamic-form';
    form.id = `Form-chapter-${id}`;
    form.innerHTML = `
        <input type="hidden" name="chapter_id" value="${id}">
        <input type="text" class="titlee" value="${document.querySelector('.titlee')?.value || 'New Book'}" readonly>
        <input type="text" class="cn" value="${title}">
        <input type="hidden" name="thestory" id="hidden-story-${id}">
        <div contenteditable="true" class="editor-content" id="editor-story-${id}" 
             oninput="syncEditor('editor-story-${id}', 'hidden-story-${id}')"
             placeholder="Tell your story..."></div>
    `;
    return form;
}

// function submitActiveForm(actionName) version with Script support
function submitActiveForm(actionName) {
    console.log("DEBUG: submitActiveForm called. Mode:", currentMode, "Action:", actionName);

    if (currentMode === 'script') {
        const title = document.querySelector('form.Script input[name="title"]')?.value;
        if (!title || title === 'Untitled Script') {
            openNameModal(actionName);
        } else {
            saveScript(actionName);
        }
        return;
    }

    if (currentMode === 'poem') {
        const title = document.querySelector('form.Poem input[name="title"]')?.value;
        if (!title || title === 'Untitled Poem') {
            openNameModal(actionName);
        } else {
            savePoem(actionName);
        }
        return;
    }

    const status = actionName === 'publish' ? 'PUBLISHED' : 'DRAFT';
    const modeClass = currentMode.charAt(0).toUpperCase() + currentMode.slice(1);
    const activeForm = document.querySelector(`form.${modeClass}`);

    // Add status to form for standard submissions
    let statusInput = activeForm?.querySelector('input[name="status"]');
    if (!statusInput && activeForm) {
        statusInput = document.createElement('input');
        statusInput.type = 'hidden';
        statusInput.name = 'status';
        activeForm.appendChild(statusInput);
    }
    if (statusInput) statusInput.value = status;

    if (actionName === 'publish' && currentMode === 'story') {
        const hasMetadataField = document.getElementById('book-has-metadata');
        const hasMetadata = hasMetadataField && hasMetadataField.value === 'true';

        console.log("DEBUG: Publish clicked. hasMetadata:", hasMetadata);

        if (!hasMetadata) {
            console.log("DEBUG: Showing metadata modal for first-time publish.");
            openPublishModal();
            return; // Wait for modal completion
        }
    }

    if (currentMode === 'story') {
        if (actionName === 'end_chapter') {
            endChapter();
        } else if (actionName === 'next_chapter') {
            const bookId = document.querySelector('input[name="book_id"]')?.value;
            if (bookId) nextChapter(bookId);
            else {
                showToast("Please save the story first before adding chapters.", "info");
                activeForm?.submit();
            }
        } else {
            const id = activeChapterId || document.querySelector('input[name="chapter_id"]')?.value;
            if (id) {
                saveChapterAjax(id, status).then(success => {
                    if (success) {
                        if (status === 'PUBLISHED') {
                            showToast("Your chapter has been published!", "success");
                        } else if (actionName === 'save_draft') {
                            // Note: "Your work is saved" toast is already shown in saveChapterAjax
                            // No need to show duplicate
                        }
                    }
                });
            } else {
                console.log("No activeChapterId, submitting form normally for new story.");
                if (actionName === 'publish') {
                    const publishInput = document.createElement('input');
                    publishInput.type = 'hidden';
                    publishInput.name = 'publish';
                    publishInput.value = 'true';
                    activeForm.appendChild(publishInput);
                }
                activeForm?.submit();
            }
        }
    } else {
        const id = activeForm?.querySelector('input[name="chapter_id"]')?.value;
        if (id) {
            saveChapterAjax(id, status).then(success => {
                if (success) {
                    if (status === 'PUBLISHED') {
                        showToast("Your work has been published!", "success");
                    }
                    // Save toast is already shown in saveChapterAjax
                }
            });
        } else {
            console.log(`No chapter ID for ${currentMode}, submitting form.`);
            if (actionName === 'publish') {
                const publishInput = document.createElement('input');
                publishInput.type = 'hidden';
                publishInput.name = 'publish';
                publishInput.value = 'true';
                activeForm.appendChild(publishInput);
            }
            activeForm?.submit();
        }
    }
}

// Modal Control Functions
// Modal Control Functions
function openPublishModal() {
    let currentTitle = '';
    const modeClass = currentMode.charAt(0).toUpperCase() + currentMode.slice(1);

    // Get title based on mode
    if (currentMode === 'story') {
        currentTitle = document.querySelector('form.Story input.titlee')?.value;
    } else {
        // Script or Poem
        const form = document.getElementById('Form-' + currentMode);
        currentTitle = form?.querySelector('input[name="title"]')?.value;
    }

    const modalTitleInput = document.getElementById('publish-title');
    if (modalTitleInput) {
        modalTitleInput.value = currentTitle || '';
    }

    // Show/Hide fields based on mode
    const genreGroup = document.getElementById('genre-group');
    const descGroup = document.querySelector('#publish-metadata-form textarea[name="description"]')?.closest('.modal-field');

    if (currentMode === 'script' || currentMode === 'poem') {
        if (genreGroup) genreGroup.style.display = 'none';
        // Script/Poem might not need description in this modal if it's just title/content
        // But let's keep description for now if the model supports it (Poem has subtitle/desc)
    } else {
        if (genreGroup) genreGroup.style.display = 'block';
    }

    const modal = document.getElementById('publish-modal');
    if (modal) modal.style.display = 'flex';
}

function closePublishModal() {
    const modal = document.getElementById('publish-modal');
    if (modal) modal.style.display = 'none';
}

function updateModalTitle(val) {
    // Keep internal title inputs in sync if necessary
    // Currently just ensures the modal knows the latest title name if it opens
}

// Name Project Modal
let pendingAction = null;

function openNameModal(action) {
    pendingAction = action;
    const modal = document.getElementById('name-modal');
    const modalTitle = document.getElementById('name-modal-title');
    const nameInput = document.getElementById('project-name-input');

    if (modalTitle) modalTitle.innerText = `Name Your ${currentMode.charAt(0).toUpperCase() + currentMode.slice(1)}`;

    // Pre-populate with current title if it exists
    const currentTitle = document.querySelector(`form#Form-${currentMode} input[name="title"]`)?.value;
    if (nameInput && currentTitle && currentTitle !== 'Untitled Script' && currentTitle !== 'Untitled Poem') {
        nameInput.value = currentTitle;
    } else if (nameInput) {
        nameInput.value = '';
    }

    if (modal) modal.style.display = 'flex';
}

function closeNameModal() {
    const modal = document.getElementById('name-modal');
    if (modal) modal.style.display = 'none';
    pendingAction = null;
}

function confirmProjectName() {
    const nameInput = document.getElementById('project-name-input');
    const name = nameInput?.value.trim();
    if (!name) {
        showToast("Please enter a name", "info");
        return;
    }

    // Explicitly target the title input within the specific active form
    const modeClass = currentMode.charAt(0).toUpperCase() + currentMode.slice(1);
    const activeForm = document.getElementById('Form-' + currentMode);
    if (activeForm) {
        const titleInput = activeForm.querySelector('input[name="title"]');
        if (titleInput) {
            titleInput.value = name;
            console.log(`DEBUG: Set ${currentMode} title to:`, name);
        } else {
            console.warn(`DEBUG: Could not find title input in Form-${currentMode}`);
        }
    }

    closeNameModal();
    if (pendingAction === 'save_draft') {
        if (currentMode === 'script') saveScript('save_draft');
        else if (currentMode === 'poem') savePoem('save_draft');
    } else if (pendingAction === 'publish') {
        if (currentMode === 'script') saveScript('publish');
        else if (currentMode === 'poem') savePoem('publish');
    }
}


// Handle Metadata Form Submission
// Handle Metadata Form Submission
document.addEventListener('DOMContentLoaded', () => {
    const metadataForm = document.getElementById('publish-metadata-form');
    if (metadataForm) {
        metadataForm.addEventListener('submit', async (e) => {
            e.preventDefault();


            // Grab values using correct IDs from write.html (publish-)
            const genreInput = document.getElementById('publish-genre');
            const descInput = document.getElementById('publish-description');
            const coverInput = document.getElementById('publish-cover');

            const genre = genreInput ? genreInput.value : '';
            const description = descInput ? descInput.value : '';

            // Only validate description length for Stories (Books)
            if (currentMode === 'story') {
                // Description validation: minimum 10 words for testing
                const wordCount = description.trim().split(/\s+/).filter(word => word.length > 0).length;
                if (wordCount < 10) {
                    showToast("Description is too short (min 10 words)", "info");
                    return;
                }
            }

            const formData = new FormData();
            formData.append('genre', genre);
            formData.append('description', description);
            if (coverInput && coverInput.files[0]) formData.append('cover_image', coverInput.files[0]);


            // --- SCRIPT SAVE ---
            if (currentMode === 'script') {
                const scriptIdInput = document.querySelector('#Form-script input[name="script_id"]');
                const scriptId = scriptIdInput?.value;

                if (scriptId) {
                    const scriptTitleInput = document.querySelector('#Form-script input[name="title"]');
                    formData.append('title', scriptTitleInput?.value || "Untitled Script");
                    formData.append('content', document.getElementById('editor-script').innerHTML);
                    formData.append('page_count', calculatePageCount());
                    formData.append('status', 'PUBLISHED');

                    console.log(`DEBUG: Publishing script ${scriptId}...`);

                    try {
                        const response = await fetch(`/ajax/save-script/${scriptId}/`, {
                            method: 'POST',
                            headers: { 'X-CSRFToken': getCookie('csrftoken') },
                            body: formData
                        });
                        const data = await response.json();
                        if (data.status === 'success') {
                            const metaInput = document.getElementById('script-has-metadata');
                            if (metaInput) metaInput.value = 'true';
                            closePublishModal();
                            showToast("Script published successfully!", "success");
                        } else {
                            console.error("Script save failed:", data.message);
                            showToast(data.message, 'error');
                        }
                    } catch (e) {
                        console.error("Script publish exception:", e);
                        showToast("Failed to publish script. Check console.", 'error');
                    }
                } else {
                    console.error("DEBUG: Script ID missing during publish.");
                    showToast("Error: Script ID missing. Please save as draft first.", "error");
                }
                return;
            }

            // --- POEM SAVE ---
            if (currentMode === 'poem') {
                const poemId = document.querySelector('input[name="poem_id"]')?.value;
                if (poemId) {
                    formData.append('title', document.querySelector('form.Poem input[name="title"]')?.value || "Untitled Poem");
                    formData.append('content', document.getElementById('editor-poem').innerHTML);
                    formData.append('status', 'PUBLISHED');

                    try {
                        const response = await fetch(`/ajax/save-poem/${poemId}/`, {
                            method: 'POST',
                            headers: { 'X-CSRFToken': getCookie('csrftoken') },
                            body: formData
                        });
                        const data = await response.json();
                        if (data.status === 'success') {
                            document.getElementById('poem-has-metadata').value = 'true';
                            closePublishModal();
                            showToast("Poem published successfully!", "success");
                        } else {
                            showToast(data.message, 'error');
                        }
                    } catch (e) { console.error(e); }
                }
                return;
            }

            // --- BOOK SAVE ---
            const bookId = document.querySelector('input[name="book_id"]')?.value;
            if (!bookId) {
                // New Book: Submit the metadata form directly
                console.log("DEBUG: New book publish. Submitting metadata form.");

                // Sync story content from editor to hidden input in metadata form
                const storyEditor = document.querySelector('form.Story .editor-content');
                const publishContent = document.getElementById('publish-content');
                if (storyEditor && publishContent) {
                    publishContent.value = storyEditor.innerHTML;
                }

                // Sync Chapter Name if present
                const storyForm = document.getElementById('Form-story');
                if (storyForm) {
                    const chapterNameInput = storyForm.querySelector('input[name="chaptername"]');
                    if (chapterNameInput && chapterNameInput.value) {
                        // Check if hidden input already exists to avoid duplicates (though submit refreshes page)
                        let hiddenChapter = metadataForm.querySelector('input[name="chaptername"]');
                        if (!hiddenChapter) {
                            hiddenChapter = document.createElement('input');
                            hiddenChapter.type = 'hidden';
                            hiddenChapter.name = 'chaptername';
                            metadataForm.appendChild(hiddenChapter);
                        }
                        hiddenChapter.value = chapterNameInput.value;
                    }
                }

                // Submit the metadata form directly (handles file upload correctly)
                metadataForm.submit();
                return;
            }

            try {
                const response = await fetch(`/ajax/update-book-metadata/${bookId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    body: formData
                });
                const data = await response.json();
                if (data.status === 'success') {
                    document.getElementById('book-has-metadata').value = 'true';
                    closePublishModal();
                    // Now proceed with normal publish
                    const id = activeChapterId || document.querySelector('input[name="chapter_id"]')?.value;
                    if (id) {
                        saveChapterAjax(id, 'PUBLISHED').then(() => {
                            showToast("Your book details have been saved and chapter published!", "success");
                        });
                    } else {
                        document.querySelector('form.Story')?.submit();
                    }
                } else {
                    showToast("Failed to save book details: " + data.message, "error");
                }
            } catch (error) {
                console.error("Metadata save failed:", error);
                showToast("Request failed. Please check your connection.", "error");
            }
        });
    }
});

// --- SCRIPT FUNCTIONS ---

function calculatePageCount() {
    const editor = document.getElementById('editor-script');
    if (!editor) return 0;
    // more robust estimation: lines and characters
    const text = (editor.innerText || "").trim();
    if (!text) return 1;
    const lines = text.split('\n').length;
    const blocks = editor.querySelectorAll('div, p').length;
    const totalLines = Math.max(lines, blocks);
    return Math.max(1, Math.ceil(totalLines / 55)); // standard screenplay is ~55 lines/page
}

async function saveScriptAjax(scriptId, status) {
    const editor = document.getElementById('editor-script');
    const content = editor ? editor.innerHTML : "";

    // Scope search to the Script form to avoid getting Poem title
    const form = document.getElementById('Form-script');
    const title = form?.querySelector('input[name="title"]')?.value || "Untitled Script";

    const pageCount = calculatePageCount();
    const csrfToken = getCookie('csrftoken');

    try {
        const response = await fetch(`/ajax/save-script/${scriptId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify({ content, title, status, page_count: pageCount })
        });
        const data = await response.json();
        if (data.status === 'success') {
            if (status === 'DRAFT') showToast("Script saved successfully", "success");
            return true;
        } else {
            showToast(`Save failed: ${data.message}`, "error");
            return false;
        }
    } catch (error) {
        console.error(error);
        return false;
    }
}

async function saveScript(actionName) {
    console.log("DEBUG: saveScript called with action:", actionName);
    let scriptId = document.querySelector('input[name="script_id"]')?.value;
    console.log("DEBUG: Found scriptId:", scriptId);

    // 1. Auto-create if missing
    if (!scriptId) {
        console.log("DEBUG: No script ID, creating new script...");
        try {
            const editor = document.getElementById('editor-script');
            const content = editor ? editor.innerHTML : "";

            // Scope title search to Form-script
            const form = document.getElementById('Form-script');
            const title = form?.querySelector('input[name="title"]')?.value || "Untitled Script";

            const csrfToken = getCookie('csrftoken');

            const contestId = document.getElementById('contest-id-input')?.value;

            const response = await fetch('/ajax/create-script/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ content, title, status: 'DRAFT', contest_id: contestId })
            });
            const data = await response.json();

            if (data.status === 'success') {
                scriptId = data.script_id;
                console.log("DEBUG: Created script with ID:", scriptId);

                // Update DOM
                let input = document.querySelector('input[name="script_id"]');
                if (!input) {
                    const form = document.getElementById('Form-script');
                    input = document.createElement('input');
                    input.type = 'hidden';
                    input.name = 'script_id';
                    form.prepend(input);
                }
                input.value = scriptId;

                // Update URL (optional but good)
                try {
                    history.pushState({}, '', `/script/write/${scriptId}/`);
                } catch (e) { console.error("History push failed:", e); }

                showToast("Script created!", "success");
            } else {
                showToast("Failed to create script: " + data.message, "error");
                return;
            }
        } catch (e) {
            console.error("Create script exception:", e);
            showToast("Error creating script", "error");
            return;
        }
    }

    // 2. Proceed with action
    if (actionName === 'save_draft') {
        await saveScriptAjax(scriptId, 'DRAFT');
    } else if (actionName === 'publish') {
        const hasMetadata = document.getElementById('script-has-metadata')?.value === 'true';
        console.log("DEBUG: Script has metadata:", hasMetadata);

        if (!hasMetadata) {
            openPublishModal();
        } else {
            const success = await saveScriptAjax(scriptId, 'PUBLISHED');
            if (success) {
                showToast("Script published successfully!", "success");
            }
        }
    } else {
        console.warn("DEBUG: Unknown action for script:", actionName);
    }
}

// --- POEM FUNCTIONS ---

async function savePoemAjax(poemId, status) {
    const editor = document.getElementById('editor-poem');
    const content = editor ? editor.innerHTML : "";

    // Scope search to the Poem form
    const form = document.getElementById('Form-poem');
    const title = form?.querySelector('input[name="title"]')?.value || "Untitled Poem";

    const description = form?.querySelector('input.cn')?.value || "";

    const csrfToken = getCookie('csrftoken');

    try {
        const response = await fetch(`/ajax/save-poem/${poemId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify({ content, title, status, description })
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Server error (${response.status}): ${errorText.substring(0, 100)}`);
        }

        const data = await response.json();
        if (data.status === 'success') {
            if (status === 'DRAFT') showToast("Poem saved successfully", "success");
            return true;
        } else {
            showToast(`Save failed: ${data.message || "Unknown error"}`, "error");
            return false;
        }
    } catch (error) {
        console.error("DEBUG: savePoemAjax error:", error);
        showToast("Error saving poem: " + error.message, "error");
        return false;
    }
}

async function savePoem(actionName) {
    const poemForm = document.getElementById('Form-poem');
    let poemIdInput = poemForm?.querySelector('input[name="poem_id"]');
    let poemId = poemIdInput?.value;

    if (!poemId || poemId === "None" || poemId === "") {
        console.log("DEBUG: No poemId found, attempting to create new poem...");
        try {
            const editor = document.getElementById('editor-poem');
            const content = editor ? editor.innerHTML : "";
            const title = poemForm?.querySelector('input[name="title"]')?.value || "Untitled Poem";
            const description = poemForm?.querySelector('input.cn')?.value || "";

            const csrfToken = getCookie('csrftoken');

            const contestId = document.getElementById('contest-id-input')?.value;

            const response = await fetch('/ajax/create-poem/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ content, title, status: 'DRAFT', description, contest_id: contestId })
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Server responded with ${response.status}: ${errorText}`);
            }

            const data = await response.json();

            if (data.status === 'success') {
                poemId = data.poem_id;
                if (poemIdInput) poemIdInput.value = poemId;
                try {
                    history.pushState({}, '', `/poem/write/${poemId}/`);
                } catch (e) { }
                showToast("Poem created!", "success");
            } else {
                showToast("Failed to create poem: " + (data.message || "Unknown error"), "error");
                return;
            }
        } catch (e) {
            console.error("DEBUG: Poem creation error:", e);
            showToast("Error creating poem: " + e.message, "error");
            return;
        }
    }

    if (actionName === 'save_draft') {
        await savePoemAjax(poemId, 'DRAFT');
    } else if (actionName === 'publish') {
        const hasMetadata = document.getElementById('poem-has-metadata')?.value === 'true';
        if (!hasMetadata) {
            openPublishModal();
        } else {
            const success = await savePoemAjax(poemId, 'PUBLISHED');
            if (success) {
                showToast("Poem published successfully!", "success");
            }
        }
    }
}



// Helper: Find the direct block child of the editor
function getBlock(editor, selection) {
    let node = selection.anchorNode;
    if (!node) return null;
    if (node === editor) {
        const offset = selection.anchorOffset;
        return editor.childNodes[offset] || editor.lastElementChild;
    }
    while (node && node.parentNode !== editor) {
        node = node.parentNode;
        if (node === document.body || node === null) return null;
    }
    return node;
}

// Global function to handle Script/Poem Tab logic (reusable for mobile)
function handleScriptTab(editor) {
    const selection = window.getSelection();
    if (!selection.rangeCount || !selection.anchorNode) return;
    if (!editor.contains(selection.anchorNode)) return;

    const currentBlock = getBlock(editor, selection);
    if (!currentBlock) return;

    if (currentMode === 'script') {
        // Screenplay Tab Logic
        // Action/Scene -> 1 tab -> Dialogue, 2 tabs -> Character
        if (currentBlock.classList.contains('script-left') || currentBlock.classList.contains('script-scene')) {
            // Action -> Dialogue (1st tab)
            currentBlock.className = 'script-dialogue';
        } else if (currentBlock.classList.contains('script-dialogue')) {
            // Dialogue -> Character (2nd tab)
            currentBlock.className = 'script-character';
            currentBlock.innerText = currentBlock.innerText.toUpperCase(); // Characters are UPPERCASE
        } else if (currentBlock.classList.contains('script-character')) {
            // Character -> Action (reset)
            currentBlock.className = 'script-left';
            currentBlock.style.textTransform = 'none';
        } else if (currentBlock.classList.contains('script-parenthetical')) {
            // Parenthetical -> Dialogue
            currentBlock.className = 'script-dialogue';
        }
    } else if (currentMode === 'poem') {
        // Poem Tab Logic removed as per user request
    }

    // Ensure sync after class change
    const hiddenId = currentMode === 'script' ? 'hidden-script' : 'hidden-poem';
    syncEditor(editor.id, hiddenId);
}

// Improved Script & Poem Mode Key Handling
document.addEventListener('keydown', (e) => {
    if (currentMode !== 'script' && currentMode !== 'poem') return;

    const editorId = currentMode === 'script' ? 'editor-script' : 'editor-poem';
    const editor = document.getElementById(editorId);
    if (!editor) return;

    const selection = window.getSelection();
    if (!selection.rangeCount || !selection.anchorNode) return;
    if (!editor.contains(selection.anchorNode)) return;

    if (e.key === 'Enter') {
        e.preventDefault();
        const currentBlock = getBlock(editor, selection);
        let newBlock = document.createElement('div');
        newBlock.innerHTML = '<br>';

        if (currentMode === 'script') {
            poemEnterSessionCount = 0; // Reset
            if (!currentBlock) {
                newBlock.className = 'script-left';
                editor.appendChild(newBlock);
            } else {
                const currentText = currentBlock.textContent || "";

                // Regex for auto-formatting scene/transition
                const sceneRegex = /^(INT\.|EXT\.|I\/E\.|INT\/EXT\.|EST\.|PROLOGUE|TEASER|COLD OPEN|FADE IN:|BLACK IN|ACT\s+[A-Z]+|SCENE\s+[0-9]+|MONTAGE|SERIES OF SHOTS|FLASHBACK|DREAM SEQUENCE|DAYDREAM|SUPER|TITLE CARD)/i;
                const transitionRegex = /^(CUT TO:|FADE TO:|DISSOLVE TO:|SMASH CUT TO:|MATCH CUT TO:|JUMP CUT TO:|WIPE TO:|TIME CUT:|FREEZE FRAME:|IRIS IN:|IRIS OUT:|FADE OUT\.|BLACK OUT\.|END OF ACT|THE END)/i;

                const isScene = sceneRegex.test(currentText.trim());
                const isTransition = transitionRegex.test(currentText.trim());

                if (isScene) {
                    currentBlock.className = 'script-scene';
                    currentBlock.innerText = currentText.trim().toUpperCase();
                } else if (isTransition) {
                    currentBlock.className = 'script-transition';
                    currentBlock.innerText = currentText.trim().toUpperCase();
                } else if (currentBlock.classList.contains('script-character')) {
                    currentBlock.innerText = currentText.trim().toUpperCase();
                }

                // DETERMINE NEXT BLOCK CLASS
                let newClass = 'script-left'; // Default to Action/Scene Description

                if (currentBlock.classList.contains('script-scene')) {
                    newClass = 'script-left'; // Action follows Scene
                } else if (currentBlock.classList.contains('script-character')) {
                    newClass = 'script-dialogue'; // Dialogue follows Character
                } else if (currentBlock.classList.contains('script-parenthetical')) {
                    newClass = 'script-dialogue'; // Dialogue follows Parenthetical
                } else if (currentBlock.classList.contains('script-dialogue')) {
                    newClass = 'script-left'; // Action follows Dialogue (Standard). User can Tab for Character.
                } else if (currentBlock.classList.contains('script-transition')) {
                    newClass = 'script-scene'; // Scene follows Transition
                }

                newBlock.className = newClass;
                if (currentBlock.nextSibling) editor.insertBefore(newBlock, currentBlock.nextSibling);
                else editor.appendChild(newBlock);
            }
        } else if (currentMode === 'poem') {
            const currentBlock = getBlock(editor, selection);
            const isEmpty = currentBlock && currentBlock.innerText.trim() === '';

            if (isEmpty) {
                poemEnterSessionCount++;
            } else {
                poemEnterSessionCount = 0;
            }

            if (poemEnterSessionCount === 1) { // This corresponds to the 2nd Enter (1st from an empty line)
                if (currentBlock) {
                    currentBlock.className = 'poem-line poem-stanza-break';
                    currentBlock.innerHTML = '<br>';
                }
                // Continue to create a new line after the stanza break
            } else if (poemEnterSessionCount === 3) { // 4th Enter
                poemEnterSessionCount = 0;
                if (currentBlock) {
                    currentBlock.className = 'poem-sub-name';
                    currentBlock.innerHTML = 'Subtitle';

                    const range = document.createRange();
                    const sel = window.getSelection();
                    range.selectNodeContents(currentBlock);
                    sel.removeAllRanges();
                    sel.addRange(range);
                    updatePageIndicators();
                    return; // Stay on the subtitle line to type
                }
            }

            // Normal line insertion
            newBlock.className = 'poem-line';
            if (currentBlock) {
                if (currentBlock.nextSibling) editor.insertBefore(newBlock, currentBlock.nextSibling);
                else editor.appendChild(newBlock);
            } else {
                editor.appendChild(newBlock);
            }
        }

        const newRange = document.createRange();
        newRange.selectNodeContents(newBlock);
        newRange.collapse(true);
        selection.removeAllRanges();
        selection.addRange(newRange);
        newBlock.scrollIntoView({ behavior: 'auto', block: 'nearest' });

        // Ensure indicators update after manual block insertion
        updatePageIndicators();
    } else if (e.key === 'Tab') {
        e.preventDefault();
        handleScriptTab(editor);
    } else if (e.key === 'Backspace') {
        if (currentMode !== 'script') return;
        const currentBlock = getBlock(editor, selection);
        if (currentBlock && selection.anchorOffset === 0) {
            // Backspace at start of line converts specialized blocks back to Action
            const specialized = ['script-character', 'script-dialogue', 'script-parenthetical', 'script-transition', 'script-scene'];
            if (specialized.some(cls => currentBlock.classList.contains(cls))) {
                e.preventDefault();
                currentBlock.className = 'script-left';
                updatePageIndicators();
            }
        }
    }
});

// Initialize first lines
document.addEventListener('DOMContentLoaded', () => {
    const scriptEditor = document.getElementById('editor-script');
    if (scriptEditor) {
        if (!scriptEditor.innerHTML.trim()) {
            scriptEditor.innerHTML = '<div class="script-center"><br></div>';
        }

        // Add real-time keyword formatting
        scriptEditor.addEventListener('input', (e) => {
            const selection = window.getSelection();
            if (!selection.rangeCount || !selection.anchorNode) return;

            let node = selection.anchorNode;
            while (node && node.parentNode !== scriptEditor) node = node.parentNode;
            if (!node || node.nodeType !== 1) return;

            const text = node.innerText || "";
            const sceneRegex = /^(INT\.|EXT\.|I\/E\.|INT\/EXT\.|EST\.|PROLOGUE|TEASER|COLD OPEN|MONTAGE|SERIES OF SHOTS|FLASHBACK|DREAM SEQUENCE|DAYDREAM|SUPER|TITLE CARD)/i;
            const transitionRegex = /^(CUT TO:|FADE TO:|DISSOLVE TO:|SMASH CUT TO:|MATCH CUT TO:|JUMP CUT TO:|WIPE TO:|TIME CUT:|FREEZE FRAME:|IRIS IN:|IRIS OUT:|FADE OUT\.|BLACK OUT\.|END OF ACT|THE END)/i;

            if (sceneRegex.test(text.trim())) {
                if (!node.classList.contains('script-scene')) {
                    node.className = 'script-scene';
                    // Clear inline styles that might interfere with class bolding
                    node.style.fontWeight = '';
                    node.style.textAlign = '';
                    node.style.textTransform = '';
                }
            } else if (transitionRegex.test(text.trim())) {
                if (!node.classList.contains('script-transition')) {
                    node.className = 'script-transition';
                    node.style.fontWeight = '';
                    node.style.textAlign = '';
                    node.style.textTransform = '';
                }
            } else if (text.trim().startsWith('(')) {
                if (!node.classList.contains('script-parenthetical')) {
                    node.className = 'script-parenthetical';
                    node.style.fontWeight = 'normal';
                    node.style.fontStyle = 'italic';
                    node.style.textAlign = '';
                }
            }

            // Shorthand (V.O.), (O.S.), etc. - Should NOT be bold even on Character lines
            const shorthandRegex = /\((V\.O\.|O\.S\.|O\.C\.|CONT'D)\)/gi;
            if (shorthandRegex.test(text)) {
                if (!node.innerHTML.includes('class="auto-normal"')) {
                    const originalHTML = node.innerHTML;
                    const newHTML = originalHTML.replace(shorthandRegex, (match) => {
                        return `<span class="auto-normal" style="font-weight: normal; font-style: normal;">${match.toUpperCase()}</span>`;
                    });

                    if (newHTML !== originalHTML) {
                        const savedSelection = saveSelection(node);
                        node.innerHTML = newHTML;
                        restoreSelection(node, savedSelection);
                    }
                }
            }
        });
    }
    const poemEditor = document.getElementById('editor-poem');
    if (poemEditor && !poemEditor.innerHTML.trim()) {
        poemEditor.innerHTML = '<div class="poem-line"><br></div>';
    }
});

const originalSwitchMode = switchMode;
switchMode = function (type) {
    originalSwitchMode(type);
    if (type === 'script') {
        const editor = document.getElementById('editor-script');
        if (editor && !editor.innerText.trim()) {
            editor.innerHTML = '<div class="script-center"><br></div>';
        }
        editor?.focus();
    } else if (type === 'poem') {
        const editor = document.getElementById('editor-poem');
        if (editor && !editor.innerText.trim()) {
            editor.innerHTML = '<div class="poem-line"><br></div>';
        }
        editor?.focus();
    }
}
