// Configuration
const CONFIG = {
    maxFileSize: 25 * 1024 * 1024, // 25MB in bytes
    maxFiles: 20,
    maxTotalSize: 200 * 1024 * 1024, // 200MB in bytes
    allowedTypes: ['image/png', 'image/jpeg', 'image/jpg', 'image/webp', 'application/pdf', 'image/heic'],
    allowedExtensions: ['.png', '.jpg', '.jpeg', '.webp', '.pdf', '.heic'],
    apiEndpoints: {
        uploads: '/api/uploads/create',
        submissions: '/api/submissions'
    },
    autosaveInterval: 5000, // 5 seconds
    clientVersion: 'web-1.0.0'
};

// Global state
let uploadedFiles = [];
let autosaveTimer = null;
let isDraftSaved = false;

// DOM elements
const form = document.getElementById('veritas-form');
const uploadZone = document.getElementById('uploadZone');
const fileInput = document.getElementById('fileUpload');
const filePreviews = document.getElementById('filePreviews');
const submitBtn = document.getElementById('submitBtn');
const resultArea = document.getElementById('resultArea');
const successBanner = document.getElementById('successBanner');
const statusCard = document.getElementById('statusCard');
const errorAlert = document.getElementById('errorAlert');
const draftNotification = document.getElementById('draftNotification');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    loadDraftFromStorage();
    setupAutosave();
});

// Event Listeners
function initializeEventListeners() {
    // Form submission
    form.addEventListener('submit', handleFormSubmit);
    
    // File upload events
    fileInput.addEventListener('change', handleFileSelect);
    uploadZone.addEventListener('click', () => fileInput.click());
    uploadZone.addEventListener('dragover', handleDragOver);
    uploadZone.addEventListener('dragleave', handleDragLeave);
    uploadZone.addEventListener('drop', handleFileDrop);
    
    // Real-time validation
    document.getElementById('houseAddress').addEventListener('input', validateHouseAddress);
    document.getElementById('landlordName').addEventListener('input', validateLandlordName);
    document.getElementById('listingUrl').addEventListener('input', validateListingUrl);
    document.getElementById('otherDetails').addEventListener('input', handleTextareaInput);
    document.getElementById('privacyConsent').addEventListener('change', validateConsent);
    
    // Retry button
    document.getElementById('retryBtn').addEventListener('click', handleRetry);
    
    // Paste handling
    document.addEventListener('paste', handlePaste);
    
    // Form input changes for autosave
    form.addEventListener('input', scheduleAutosave);
    form.addEventListener('change', scheduleAutosave);
}

// File Upload Handlers
function handleFileSelect(event) {
    const files = Array.from(event.target.files);
    processFiles(files);
}

function handleDragOver(event) {
    event.preventDefault();
    uploadZone.classList.add('dragover');
}

function handleDragLeave(event) {
    event.preventDefault();
    uploadZone.classList.remove('dragover');
}

function handleFileDrop(event) {
    event.preventDefault();
    uploadZone.classList.remove('dragover');
    
    const files = Array.from(event.dataTransfer.files);
    processFiles(files);
}

function processFiles(files) {
    const errors = [];
    const validFiles = [];
    
    // Check total file count
    if (uploadedFiles.length + files.length > CONFIG.maxFiles) {
        errors.push(`Maximum ${CONFIG.maxFiles} files allowed. You can upload ${CONFIG.maxFiles - uploadedFiles.length} more files.`);
        return showFileError(errors.join(' '));
    }
    
    // Validate each file
    files.forEach(file => {
        const validation = validateFile(file);
        if (validation.valid) {
            validFiles.push(file);
        } else {
            errors.push(`${file.name}: ${validation.error}`);
        }
    });
    
    // Check total size
    const currentTotalSize = uploadedFiles.reduce((sum, file) => sum + file.size, 0);
    const newFilesSize = validFiles.reduce((sum, file) => sum + file.size, 0);
    
    if (currentTotalSize + newFilesSize > CONFIG.maxTotalSize) {
        errors.push(`Total file size cannot exceed ${formatFileSize(CONFIG.maxTotalSize)}.`);
    }
    
    if (errors.length > 0) {
        showFileError(errors.join(' '));
        return;
    }
    
    // Process valid files
    validFiles.forEach(file => {
        const fileData = {
            id: generateFileId(),
            file: file,
            name: file.name,
            size: file.size,
            type: file.type,
            preview: null,
            uploaded: false,
            uploadProgress: 0
        };
        
        uploadedFiles.push(fileData);
        createFilePreview(fileData);
        
        // Generate preview for images
        if (file.type.startsWith('image/')) {
            generateImagePreview(fileData);
        }
    });
    
    clearFileError();
    scheduleAutosave();
}

function validateFile(file) {
    // Check file type
    if (!CONFIG.allowedTypes.includes(file.type)) {
        const extension = '.' + file.name.split('.').pop().toLowerCase();
        if (!CONFIG.allowedExtensions.includes(extension)) {
            return {
                valid: false,
                error: `File type not supported. Allowed types: ${CONFIG.allowedExtensions.join(', ')}`
            };
        }
    }
    
    // Check file size
    if (file.size > CONFIG.maxFileSize) {
        return {
            valid: false,
            error: `File size exceeds ${formatFileSize(CONFIG.maxFileSize)} limit`
        };
    }
    
    // Check for duplicate names
    if (uploadedFiles.some(f => f.name === file.name)) {
        return {
            valid: false,
            error: 'File with this name already exists'
        };
    }
    
    return { valid: true };
}

function createFilePreview(fileData) {
    const preview = document.createElement('div');
    preview.className = 'file-preview';
    preview.dataset.fileId = fileData.id;
    
    preview.innerHTML = `
        <button type="button" class="file-remove" onclick="removeFile('${fileData.id}')" aria-label="Remove ${fileData.name}">
            ×
        </button>
        <div class="file-content">
            ${fileData.type.startsWith('image/') ? 
                '<div class="image-placeholder">Loading...</div>' : 
                `<div class="file-icon">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"/>
                    </svg>
                </div>`
            }
        </div>
        <div class="file-name">${fileData.name}</div>
        <div class="file-size">${formatFileSize(fileData.size)}</div>
        <div class="progress-bar" style="display: none;">
            <div class="progress-fill" style="width: 0%"></div>
        </div>
    `;
    
    filePreviews.appendChild(preview);
}

function generateImagePreview(fileData) {
    const reader = new FileReader();
    reader.onload = function(e) {
        const preview = document.querySelector(`[data-file-id="${fileData.id}"] .image-placeholder`);
        if (preview) {
            preview.outerHTML = `<img src="${e.target.result}" alt="${fileData.name}">`;
        }
        fileData.preview = e.target.result;
    };
    reader.readAsDataURL(fileData.file);
}

function removeFile(fileId) {
    uploadedFiles = uploadedFiles.filter(file => file.id !== fileId);
    const preview = document.querySelector(`[data-file-id="${fileId}"]`);
    if (preview) {
        preview.remove();
    }
    clearFileError();
    scheduleAutosave();
}

// Validation Functions
function validateHouseAddress() {
    const input = document.getElementById('houseAddress');
    const error = document.getElementById('houseAddress-error');
    const value = input.value.trim();
    
    clearFieldError(input, error);
    
    if (!value) {
        if (input.dataset.touched) {
            showFieldError(input, error, 'House address is required');
            return false;
        }
        return true;
    }
    
    input.dataset.touched = 'true';
    
    if (value.length < 5) {
        showFieldError(input, error, 'Address must be at least 5 characters long');
        return false;
    }
    
    if (value.length > 200) {
        showFieldError(input, error, 'Address must be less than 200 characters');
        return false;
    }
    
    return true;
}

function validateLandlordName() {
    const input = document.getElementById('landlordName');
    const error = document.getElementById('landlordName-error');
    const value = input.value.trim();
    
    clearFieldError(input, error);
    
    if (!value) {
        if (input.dataset.touched) {
            showFieldError(input, error, 'Landlord name is required');
            return false;
        }
        return true;
    }
    
    input.dataset.touched = 'true';
    
    if (value.length < 1) {
        showFieldError(input, error, 'Landlord name must be at least 1 character long');
        return false;
    }
    
    if (value.length > 100) {
        showFieldError(input, error, 'Landlord name must be less than 100 characters');
        return false;
    }
    
    return true;
}

function validateListingUrl() {
    const input = document.getElementById('listingUrl');
    const error = document.getElementById('listingUrl-error');
    const value = input.value.trim();
    
    clearFieldError(input, error);
    
    if (!value) {
        if (input.dataset.touched) {
            showFieldError(input, error, 'Listing URL is required');
            return false;
        }
        return true;
    }
    
    input.dataset.touched = 'true';
    
    if (value.length < 5) {
        showFieldError(input, error, 'URL must be at least 5 characters long');
        return false;
    }
    
    if (value.length > 500) {
        showFieldError(input, error, 'URL must be less than 500 characters');
        return false;
    }
    
    // URL validation
    try {
        const url = new URL(value);
        if (!['http:', 'https:'].includes(url.protocol)) {
            showFieldError(input, error, 'URL must start with http:// or https://');
            return false;
        }
    } catch {
        showFieldError(input, error, 'Please enter a valid URL');
        return false;
    }
    
    return true;
}

function validateOtherDetails() {
    const input = document.getElementById('otherDetails');
    const error = document.getElementById('otherDetails-error');
    const value = input.value.trim();
    
    clearFieldError(input, error);
    
    if (value.length > 10000) {
        showFieldError(input, error, 'Details must be less than 10,000 characters');
        return false;
    }
    
    return true;
}

function validateConsent() {
    const input = document.getElementById('privacyConsent');
    const error = document.getElementById('privacyConsent-error');
    
    clearFieldError(input, error);
    
    if (!input.checked) {
        showFieldError(input, error, 'You must agree to the Privacy Policy');
        return false;
    }
    
    return true;
}

function validateForm() {
    const isAddressValid = validateHouseAddress();
    const isLandlordNameValid = validateLandlordName();
    const isUrlValid = validateListingUrl();
    const isDetailsValid = validateOtherDetails();
    const isConsentValid = validateConsent();
    
    // Mark all fields as touched for validation display
    document.getElementById('houseAddress').dataset.touched = 'true';
    document.getElementById('landlordName').dataset.touched = 'true';
    document.getElementById('listingUrl').dataset.touched = 'true';
    
    return isAddressValid && isLandlordNameValid && isUrlValid && isDetailsValid && isConsentValid;
}

// Form Submission
async function handleFormSubmit(event) {
    event.preventDefault();
    
    if (!validateForm()) {
        return;
    }
    
    setLoadingState(true);
    hideResults();
    
    try {
        // Upload files first if any
        let attachments = [];
        if (uploadedFiles.length > 0) {
            attachments = await uploadFiles();
        }
        
        // Submit form data
        const formData = collectFormData(attachments);
        const response = await submitForm(formData);
        
        if (response.ok) {
            const result = await response.json();
            
            // Save address to sessionStorage for results page
            const address = document.getElementById('houseAddress').value.trim();
            sessionStorage.setItem('veritas_address', address);
            
            // Navigate to results page
            window.location.href = 'results.html';
        } else {
            const error = await response.json();
            showError(error);
        }
    } catch (error) {
        console.error('Submission error:', error);
        showError({
            errorId: 'client_error_' + Date.now(),
            message: 'Network error occurred. Please check your connection and try again.'
        });
    } finally {
        setLoadingState(false);
    }
}

async function uploadFiles() {
    // For demo purposes, we'll simulate file uploads
    // In a real implementation, this would handle pre-signed URLs or direct uploads
    
    const attachments = [];
    
    for (const fileData of uploadedFiles) {
        try {
            // Simulate upload progress
            await simulateFileUpload(fileData);
            
            // Create attachment object
            attachments.push({
                id: fileData.id,
                name: fileData.name,
                mime: fileData.type,
                url: `https://example.com/uploads/${fileData.id}`, // Simulated URL
                size: fileData.size
            });
        } catch (error) {
            throw new Error(`Failed to upload ${fileData.name}: ${error.message}`);
        }
    }
    
    return attachments;
}

async function simulateFileUpload(fileData) {
    const preview = document.querySelector(`[data-file-id="${fileData.id}"] .progress-bar`);
    const progressFill = preview?.querySelector('.progress-fill');
    
    if (preview) {
        preview.style.display = 'block';
    }
    
    // Simulate upload progress
    for (let progress = 0; progress <= 100; progress += 10) {
        await new Promise(resolve => setTimeout(resolve, 50));
        if (progressFill) {
            progressFill.style.width = `${progress}%`;
        }
        fileData.uploadProgress = progress;
    }
    
    fileData.uploaded = true;
    
    if (preview) {
        preview.style.display = 'none';
    }
}

function collectFormData(attachments) {
    return {
        houseAddress: document.getElementById('houseAddress').value.trim(),
        landlordName: document.getElementById('landlordName').value.trim(),
        listingUrl: document.getElementById('listingUrl').value.trim(),
        otherDetails: document.getElementById('otherDetails').value.trim(),
        attachments: attachments,
        consents: {
            privacy: document.getElementById('privacyConsent').checked,
            contact: true // Assuming contact consent is implied
        },
        metadata: {
            clientVersion: CONFIG.clientVersion,
            locale: navigator.language || 'en-US',
            tz: Intl.DateTimeFormat().resolvedOptions().timeZone,
            userAgent: navigator.userAgent,
            timestamp: new Date().toISOString()
        }
    };
}

async function submitForm(formData) {
    // For demo purposes, simulate API call
    // In production, this would make actual API calls
    
    console.log('Submitting form data:', formData);
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Simulate different responses for testing
    const shouldSucceed = Math.random() >= 0; // 100% success rate for demo
    
    if (shouldSucceed) {
        return {
            ok: true,
            json: async () => ({
                submissionId: 'subm_' + Date.now(),
                status: 'received',
                estimatedWaitSec: 15
            })
        };
    } else {
        return {
            ok: false,
            json: async () => ({
                errorId: 'err_' + Date.now(),
                message: 'Validation failed: Please check your inputs and try again.'
            })
        };
    }
}

// UI State Management
function setLoadingState(loading) {
    submitBtn.disabled = loading;
    if (loading) {
        submitBtn.classList.add('loading');
    } else {
        submitBtn.classList.remove('loading');
    }
}

function showSuccess(result) {
    resultArea.style.display = 'block';
    successBanner.style.display = 'flex';
    
    if (result.submissionId) {
        statusCard.style.display = 'block';
        document.getElementById('jobId').textContent = result.submissionId;
        document.getElementById('waitTime').textContent = result.estimatedWaitSec || 'Unknown';
    }
    
    errorAlert.style.display = 'none';
    
    // Scroll to results
    resultArea.scrollIntoView({ behavior: 'smooth' });
}

function showError(error) {
    resultArea.style.display = 'block';
    errorAlert.style.display = 'flex';
    
    document.getElementById('errorMessage').textContent = error.message || 'An unexpected error occurred.';
    document.getElementById('errorId').textContent = error.errorId || 'unknown';
    
    successBanner.style.display = 'none';
    statusCard.style.display = 'none';
    
    // Scroll to error
    errorAlert.scrollIntoView({ behavior: 'smooth' });
}

function hideResults() {
    resultArea.style.display = 'none';
    successBanner.style.display = 'none';
    statusCard.style.display = 'none';
    errorAlert.style.display = 'none';
}

function handleRetry() {
    hideResults();
    form.scrollIntoView({ behavior: 'smooth' });
}

// Field Error Helpers
function showFieldError(input, errorElement, message) {
    input.classList.add('error');
    errorElement.textContent = message;
}

function clearFieldError(input, errorElement) {
    input.classList.remove('error');
    errorElement.textContent = '';
}

function showFileError(message) {
    const errorElement = document.getElementById('fileUpload-error');
    errorElement.textContent = message;
}

function clearFileError() {
    const errorElement = document.getElementById('fileUpload-error');
    errorElement.textContent = '';
}

// Textarea Handler
function handleTextareaInput(event) {
    const textarea = event.target;
    const counter = document.getElementById('otherDetails-count');
    const length = textarea.value.length;
    
    counter.textContent = length;
    
    // Update counter color based on limit
    if (length > 9500) {
        counter.style.color = '#dc2626';
    } else if (length > 8000) {
        counter.style.color = '#f59e0b';
    } else {
        counter.style.color = '#6b7280';
    }
    
    validateOtherDetails();
}

// Paste Handler
function handlePaste(event) {
    const items = Array.from(event.clipboardData.items);
    const files = items
        .filter(item => item.kind === 'file')
        .map(item => item.getAsFile())
        .filter(file => file);
    
    if (files.length > 0) {
        event.preventDefault();
        processFiles(files);
    }
}

// Autosave Functionality
function scheduleAutosave() {
    if (autosaveTimer) {
        clearTimeout(autosaveTimer);
    }
    
    autosaveTimer = setTimeout(() => {
        saveDraftToStorage();
    }, CONFIG.autosaveInterval);
}

function saveDraftToStorage() {
    try {
        const draftData = {
            houseAddress: document.getElementById('houseAddress').value,
            landlordName: document.getElementById('landlordName').value,
            listingUrl: document.getElementById('listingUrl').value,
            otherDetails: document.getElementById('otherDetails').value,
            privacyConsent: document.getElementById('privacyConsent').checked,
            timestamp: Date.now(),
            files: uploadedFiles.map(f => ({
                id: f.id,
                name: f.name,
                size: f.size,
                type: f.type
            }))
        };
        
        localStorage.setItem('veritas-draft', JSON.stringify(draftData));
        showDraftSavedNotification();
        isDraftSaved = true;
    } catch (error) {
        console.warn('Failed to save draft:', error);
    }
}

function loadDraftFromStorage() {
    try {
        const draftJson = localStorage.getItem('veritas-draft');
        if (!draftJson) return;
        
        const draft = JSON.parse(draftJson);
        
        // Check if draft is not too old (24 hours)
        const maxAge = 24 * 60 * 60 * 1000;
        if (Date.now() - draft.timestamp > maxAge) {
            localStorage.removeItem('veritas-draft');
            return;
        }
        
        // Restore form values
        document.getElementById('houseAddress').value = draft.houseAddress || '';
        document.getElementById('landlordName').value = draft.landlordName || '';
        document.getElementById('listingUrl').value = draft.listingUrl || '';
        document.getElementById('otherDetails').value = draft.otherDetails || '';
        document.getElementById('privacyConsent').checked = draft.privacyConsent || false;
        
        // Update character counter
        const textarea = document.getElementById('otherDetails');
        const counter = document.getElementById('otherDetails-count');
        counter.textContent = textarea.value.length;
        
        isDraftSaved = true;
    } catch (error) {
        console.warn('Failed to load draft:', error);
        localStorage.removeItem('veritas-draft');
    }
}

function clearDraftFromStorage() {
    localStorage.removeItem('veritas-draft');
    isDraftSaved = false;
}

function showDraftSavedNotification() {
    draftNotification.style.display = 'block';
    
    setTimeout(() => {
        draftNotification.style.display = 'none';
    }, 2000);
}

function setupAutosave() {
    // Save draft before page unload if there are unsaved changes
    window.addEventListener('beforeunload', (event) => {
        if (!isDraftSaved && hasFormData()) {
            saveDraftToStorage();
        }
    });
}

function hasFormData() {
    const address = document.getElementById('houseAddress').value.trim();
    const url = document.getElementById('listingUrl').value.trim();
    const details = document.getElementById('otherDetails').value.trim();
    
    return address || url || details || uploadedFiles.length > 0;
}

// Form Clearing
function clearForm() {
    form.reset();
    uploadedFiles = [];
    filePreviews.innerHTML = '';
    
    // Clear character counter
    document.getElementById('otherDetails-count').textContent = '0';
    
    // Clear all error states
    const inputs = form.querySelectorAll('.field-input, .field-textarea, .checkbox-input');
    inputs.forEach(input => {
        input.classList.remove('error');
        delete input.dataset.touched;
    });
    
    const errors = form.querySelectorAll('.field-error');
    errors.forEach(error => error.textContent = '');
}

// Utility Functions
function generateFileId() {
    return 'file_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Global function for file removal (called from HTML)
window.removeFile = removeFile;

// Accessibility enhancements
document.addEventListener('keydown', function(event) {
    // Handle Escape key to close notifications
    if (event.key === 'Escape') {
        if (draftNotification.style.display === 'block') {
            draftNotification.style.display = 'none';
        }
    }
    
    // Handle Enter key on upload zone
    if (event.key === 'Enter' && event.target === uploadZone) {
        event.preventDefault();
        fileInput.click();
    }
});

// Handle focus management for file upload
uploadZone.addEventListener('keydown', function(event) {
    if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        fileInput.click();
    }
});

// Make upload zone focusable
uploadZone.setAttribute('tabindex', '0');
uploadZone.setAttribute('role', 'button');
uploadZone.setAttribute('aria-label', 'Click to upload files or drag and drop files here');

// Console logging for debugging
console.log('Veritas AI Frontend initialized');
console.log('Configuration:', CONFIG);
