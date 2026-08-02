// =========================================
// Toast System
// =========================================
function showToast(message, type = "info") {
    const container = document.getElementById("toastContainer");
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    
    let icon = "";
    if (type === "success") {
        icon = `<svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>`;
    } else if (type === "error") {
        icon = `<svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>`;
    } else {
        icon = `<svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>`;
    }

    toast.innerHTML = `${icon} <span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add("fade-out");
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// =========================================
// Sidebar & Mobile Overlay Logic
// =========================================
const sidebar = document.getElementById("sidebar");
const hamburgerBtn = document.getElementById("hamburgerBtn");
const closeSidebarBtn = document.getElementById("closeSidebarBtn");
const mobileOverlay = document.getElementById("mobileOverlay");

function toggleSidebar() {
    if (window.innerWidth <= 900) {
        sidebar.classList.toggle("open");
        if (sidebar.classList.contains("open")) {
            mobileOverlay.classList.add("show");
        } else {
            mobileOverlay.classList.remove("show");
        }
    } else {
        sidebar.classList.toggle("collapsed");
    }
}

hamburgerBtn.addEventListener("click", toggleSidebar);
closeSidebarBtn.addEventListener("click", toggleSidebar);
mobileOverlay.addEventListener("click", toggleSidebar);


// =========================================
// Load Documents
// =========================================
loadDocuments();

async function loadDocuments() {
    try {
        const response = await fetch("/documents");
        const data = await response.json();
        const list = document.getElementById("documentList");
        list.innerHTML = "";

        if (data.documents.length === 0) {
            list.innerHTML = `
                <div class="docs-empty-state">
                    <svg viewBox="0 0 24 24" width="32" height="32" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                        <polyline points="14 2 14 8 20 8"></polyline>
                        <line x1="16" y1="13" x2="8" y2="13"></line>
                        <line x1="16" y1="17" x2="8" y2="17"></line>
                        <polyline points="10 9 9 9 8 9"></polyline>
                    </svg>
                    No documents uploaded yet. Upload your first document to start chatting.
                </div>
            `;
            return;
        }

        data.documents.forEach(file => {
            list.innerHTML += `
            <div class="document-row">
                <div class="doc-name" title="${file}">
                    <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                        <polyline points="14 2 14 8 20 8"></polyline>
                        <line x1="16" y1="13" x2="8" y2="13"></line>
                        <line x1="16" y1="17" x2="8" y2="17"></line>
                        <polyline points="10 9 9 9 8 9"></polyline>
                    </svg>
                    ${file}
                </div>
                <button class="delete-btn" onclick="deleteDocument('${file}')" title="Delete">
                    <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">
                        <polyline points="3 6 5 6 21 6"></polyline>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                        <line x1="10" y1="11" x2="10" y2="17"></line>
                        <line x1="14" y1="11" x2="14" y2="17"></line>
                    </svg>
                </button>
            </div>
            `;
        });
    } catch (error) {
        showToast("Failed to load documents", "error");
    }
}


// =========================================
// Ask AI
// =========================================
const askBtn = document.getElementById("askBtn");
const questionInput = document.getElementById("question");
const chatBox = document.getElementById("chatBox");
const chatScrollWrapper = document.getElementById("chatScrollWrapper");
const loading = document.getElementById("loading");
const loadingText = document.getElementById("loadingText");

askBtn.addEventListener("click", askQuestion);

questionInput.addEventListener("keypress", function(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        askQuestion();
    }
});

questionInput.addEventListener("input", function() {
    this.style.height = "auto";
    this.style.height = Math.min(this.scrollHeight, 200) + "px";
});

function formatAnswer(text) {
    const paragraphs = text.split('\n\n');
    return paragraphs.map(p => {
        return `<p>${p.replace(/\n/g, '<br>')}</p>`;
    }).join('');
}

async function askQuestion() {
    if (askBtn.disabled) return;
    
    const question = questionInput.value.trim();
    if (question === "") return;

    const welcomeScreen = document.getElementById("welcomeScreen");
    if (welcomeScreen) welcomeScreen.style.display = "none";

    chatBox.innerHTML += `
    <div class="message-row user-row">
        <div class="user-message">
            ${question}
        </div>
    </div>
    `;

    questionInput.value = "";
    questionInput.style.height = "auto";
    chatScrollWrapper.scrollTo({ top: chatScrollWrapper.scrollHeight, behavior: 'smooth' });

    loading.classList.remove("hidden");
    loadingText.innerText = "Generating response...";
    askBtn.disabled = true;

    try {
        const response = await fetch("/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question: question })
        });

        const data = await response.json();

        loading.classList.add("hidden");
        askBtn.disabled = false;

        if (!data.success) {
            let msg = data.message || "An error occurred while generating a response.";
            if (msg.includes("<")) msg = "Unexpected error generating response.";
            showToast(msg, "error");
            return;
        }

        let sourceHTML = "";
        data.sources.forEach(source => {
            sourceHTML += `
            <div class="source-card">
                <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                </svg>
                <div style="flex:1; word-break: break-word;" title="${source.file}">
                    <strong>${source.file}</strong>
                </div>
                <div style="color:var(--text-secondary); font-size:12px; white-space:nowrap;">
                    Page ${source.page}
                </div>
            </div>`;
        });

        const formattedAnswer = formatAnswer(data.answer);

        chatBox.innerHTML += `
        <div class="message-row ai-row">
            <div class="ai-message">
                <div class="ai-content">
                    ${formattedAnswer}
                </div>
                ${data.sources.length > 0 ? `
                <button class="source-toggle">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="16" x2="12" y2="12"></line>
                        <line x1="12" y1="8" x2="12.01" y2="8"></line>
                    </svg>
                    View Sources (${data.sources.length})
                </button>
                <div class="source-list" style="display:none;">
                    ${sourceHTML}
                </div>
                ` : ''}
            </div>
        </div>
        `;

        chatScrollWrapper.scrollTo({ top: chatScrollWrapper.scrollHeight, behavior: 'smooth' });
        bindSourceToggles();

    } catch (error) {
        loading.classList.add("hidden");
        askBtn.disabled = false;
        let msg = error.message || "Failed to reach server.";
        if (msg.includes("<")) msg = "Network error. Please try again.";
        showToast(msg, "error");
    }
}

function bindSourceToggles() {
    const buttons = document.querySelectorAll(".source-toggle:not(.bound)");
    buttons.forEach(button => {
        button.classList.add("bound");
        button.onclick = function() {
            const list = this.nextElementSibling;
            if (list.style.display === "none") {
                list.style.display = "flex";
                this.innerHTML = `
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:14px;height:14px;">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="16" x2="12" y2="12"></line>
                        <line x1="12" y1="8" x2="12.01" y2="8"></line>
                    </svg>
                    Hide Sources
                `;
            } else {
                list.style.display = "none";
                this.innerHTML = `
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:14px;height:14px;">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="16" x2="12" y2="12"></line>
                        <line x1="12" y1="8" x2="12.01" y2="8"></line>
                    </svg>
                    View Sources (${list.querySelectorAll(".source-card").length})
                `;
            }
        };
    });
}

// =========================================
// Upload Documents & Drag-Drop
// =========================================
const VALID_EXTENSIONS = [".pdf", ".txt", ".docx", ".csv", ".xlsx", ".xls", ".pptx", ".md"];
const MAX_FILE_SIZE = 20 * 1024 * 1024; // 20 MB

const fileInput = document.getElementById("fileInput");
const dragOverlay = document.getElementById("dragOverlay");

// Drag Events
document.addEventListener("dragenter", (e) => {
    e.preventDefault();
    if (e.dataTransfer.types.includes("Files")) {
        dragOverlay.classList.remove("hidden");
    }
});

dragOverlay.addEventListener("dragover", (e) => {
    e.preventDefault();
});

dragOverlay.addEventListener("dragleave", (e) => {
    e.preventDefault();
    dragOverlay.classList.add("hidden");
});

dragOverlay.addEventListener("drop", (e) => {
    e.preventDefault();
    dragOverlay.classList.add("hidden");
    handleUpload(e.dataTransfer.files);
});

fileInput.addEventListener("change", () => {
    handleUpload(fileInput.files);
});

async function handleUpload(files) {
    if (!files || files.length === 0) return;

    const formData = new FormData();
    let validFilesCount = 0;

    for (const file of files) {
        if (file.size > MAX_FILE_SIZE) {
            showToast(`File "${file.name}" exceeds 20 MB.`, "error");
            continue;
        }

        const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
        if (!VALID_EXTENSIONS.includes(ext)) {
            showToast(`Unsupported file type: ${ext}. Supported: PDF, TXT, DOCX, CSV, MD, Excel, PPTX.`, "error");
            continue;
        }

        formData.append("files", file);
        validFilesCount++;
    }

    fileInput.value = ""; // Reset immediately

    if (validFilesCount === 0) {
        showToast("No valid files to upload.", "error");
        return;
    }

    // Progress Simulation
    loading.classList.remove("hidden");
    
    const progressStates = [
        "Uploading document...",
        "Parsing content...",
        "Generating embeddings...",
        "Updating search index...",
        "Almost ready..."
    ];
    
    let progressIndex = 0;
    loadingText.innerText = progressStates[0];
    
    // Disable inputs
    fileInput.disabled = true;
    document.querySelector('.upload-btn').classList.add('disabled');
    askBtn.disabled = true;
    questionInput.disabled = true;
    document.querySelectorAll('.delete-btn').forEach(btn => btn.disabled = true);
    
    const progressInterval = setInterval(() => {
        progressIndex = Math.min(progressIndex + 1, progressStates.length - 1);
        loadingText.innerText = progressStates[progressIndex];
    }, 2000);

    try {
        const response = await fetch("/upload", {
            method: "POST",
            body: formData
        });
        const data = await response.json();
        
        clearInterval(progressInterval);
        
        if (data.success) {
            loadingText.innerText = "Done ✓";
            showToast("Upload successful", "success");
            setTimeout(() => {
                loading.classList.add("hidden");
                loadDocuments();
                resetUIState();
            }, 1000);
        } else {
            loading.classList.add("hidden");
            resetUIState();
            let msg = data.message || "Embedding generation failed. Please try again.";
            if (msg.includes("<")) msg = "Unexpected error generating embeddings.";
            showToast(msg, "error");
        }
    } catch (error) {
        clearInterval(progressInterval);
        loading.classList.add("hidden");
        resetUIState();
        let msg = error.message || "Please try again.";
        if (msg.includes("<")) msg = "Network error during upload.";
        showToast("Upload failed: " + msg, "error");
    }
}

function resetUIState() {
    fileInput.disabled = false;
    document.querySelector('.upload-btn').classList.remove('disabled');
    askBtn.disabled = false;
    questionInput.disabled = false;
    document.querySelectorAll('.delete-btn').forEach(btn => btn.disabled = false);
}

// =========================================
// Delete Document
// =========================================
async function deleteDocument(file) {
    const ok = confirm(`Delete "${file}"?`);
    if (!ok) return;

    loading.classList.remove("hidden");
    loadingText.innerText = "Deleting document and updating search index...";
    
    // Disable inputs
    fileInput.disabled = true;
    document.querySelector('.upload-btn').classList.add('disabled');
    askBtn.disabled = true;
    questionInput.disabled = true;
    document.querySelectorAll('.delete-btn').forEach(btn => btn.disabled = true);

    try {
        const response = await fetch(`/delete/${encodeURIComponent(file)}`, {
            method: "DELETE"
        });

        const data = await response.json();
        loading.classList.add("hidden");
        resetUIState();

        if (data.success) {
            showToast("Document deleted successfully", "success");
            loadDocuments();
        } else {
            let msg = data.message || "Failed to delete document.";
            if (msg.includes("<")) msg = "Unexpected error deleting document.";
            showToast(msg, "error");
        }
    } catch (error) {
        loading.classList.add("hidden");
        resetUIState();
        let msg = error.message || "Failed to delete document.";
        if (msg.includes("<")) msg = "Network error during deletion.";
        showToast(msg, "error");
    }
}
