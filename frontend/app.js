/**
 * Image Morph - Frontend JavaScript
 * Professional image conversion tool with modern UI
 */

// API Base URL
const API_BASE_URL = window.location.origin.includes('localhost') 
    ? 'http://localhost:8000/api' 
    : '/api';

// State
let currentFile = null;
let currentImageId = null;
let selectedFormat = null;

// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const uploadContent = document.querySelector('.upload-content');
const uploadPreview = document.getElementById('uploadPreview');
const fileInput = document.getElementById('fileInput');
const previewImage = document.getElementById('previewImage');
const fileNameEl = document.getElementById('fileName');
const fileSizeEl = document.getElementById('fileSize');
const changeFileBtn = document.getElementById('changeFileBtn');
const uploadError = document.getElementById('uploadError');
const errorMessage = document.getElementById('errorMessage');

const conversionSection = document.getElementById('conversionSection');
const formatCards = document.querySelectorAll('.format-card');
const svgOption = document.getElementById('svgOption');
const qualityControl = document.getElementById('qualityControl');
const qualitySlider = document.getElementById('qualitySlider');
const qualityValue = document.getElementById('qualityValue');
const convertBtn = document.getElementById('convertBtn');

const resultSection = document.getElementById('resultSection');
const resultImage = document.getElementById('resultImage');
const originalSizeEl = document.getElementById('originalSize');
const convertedSizeEl = document.getElementById('convertedSize');
const savingsPercentEl = document.getElementById('savingsPercent');
const downloadBtn = document.getElementById('downloadBtn');
const convertAnotherBtn = document.getElementById('convertAnotherBtn');

const historyList = document.getElementById('historyList');
const refreshHistoryBtn = document.getElementById('refreshHistoryBtn');

const toastContainer = document.getElementById('toastContainer');

// Mobile Navigation
const hamburger = document.querySelector('.hamburger');
const navMenu = document.querySelector('.nav-menu');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadHistory();
    setupEventListeners();
    setupMobileNav();
    checkSvgSupport();
});

// Check if SVG conversion is supported
async function checkSvgSupport() {
    try {
        const response = await fetch(`${API_BASE_URL}/info`);
        if (response.ok) {
            const data = await response.json();
            if (!data.supported_output_formats.includes('svg')) {
                svgOption.style.display = 'none';
            }
        }
    } catch (error) {
        console.log('Could not check SVG support');
    }
}

// Mobile Navigation
function setupMobileNav() {
    if (hamburger) {
        hamburger.addEventListener('click', () => {
            hamburger.classList.toggle('active');
            navMenu.classList.toggle('active');
        });
    }
    
    // Close menu when clicking a link
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            hamburger.classList.remove('active');
            navMenu.classList.remove('active');
        });
    });
}

// Event Listeners
function setupEventListeners() {
    // Upload area drag and drop
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    uploadArea.addEventListener('click', () => fileInput.click());
    
    // File input change
    fileInput.addEventListener('change', handleFileSelect);
    
    // Change file button
    changeFileBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        resetUpload();
    });
    
    // Format selection
    formatCards.forEach(card => {
        card.addEventListener('click', () => selectFormat(card));
    });
    
    // Quality slider
    qualitySlider.addEventListener('input', (e) => {
        qualityValue.textContent = e.target.value;
    });
    
    // Convert button
    convertBtn.addEventListener('click', handleConvert);
    
    // Result actions
    downloadBtn.addEventListener('click', handleDownload);
    convertAnotherBtn.addEventListener('click', resetAll);
    
    // History refresh
    refreshHistoryBtn.addEventListener('click', loadHistory);
}

// Drag and Drop Handlers
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        validateAndProcessFile(files[0]);
    }
}

function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        validateAndProcessFile(files[0]);
    }
}

// File Validation and Processing
function validateAndProcessFile(file) {
    hideError();
    
    // Check file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/bmp', 'image/tiff'];
    const allowedExtensions = ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension)) {
        showError(`Invalid file format. Allowed: JPG, JPEG, PNG, WEBP, BMP, TIFF`);
        return;
    }
    
    // Check file size (10MB max)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
        showError(`File too large. Maximum size: 10MB`);
        return;
    }
    
    currentFile = file;
    displayPreview(file);
    uploadFile(file);
}

function displayPreview(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImage.src = e.target.result;
        fileNameEl.textContent = file.name;
        fileSizeEl.textContent = formatFileSize(file.size);
        
        uploadContent.hidden = true;
        uploadPreview.hidden = false;
        conversionSection.hidden = false;
        
        // Scroll to conversion section
        setTimeout(() => {
            conversionSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
    };
    reader.readAsDataURL(file);
}

// File Upload
async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        showToast('Uploading image...', 'info');
        
        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }
        
        const data = await response.json();
        currentImageId = data.id;
        
        showToast('Upload successful!', 'success');
        convertBtn.disabled = false;
        
    } catch (error) {
        showError(`Upload failed: ${error.message}`);
        showToast(`Upload failed: ${error.message}`, 'error');
    }
}

// Format Selection
function selectFormat(card) {
    formatCards.forEach(c => c.classList.remove('active'));
    card.classList.add('active');
    selectedFormat = card.dataset.format;
    
    // Show/hide quality control for lossy formats
    if (selectedFormat === 'webp' || selectedFormat === 'jpg' || selectedFormat === 'jpeg') {
        qualityControl.hidden = false;
    } else {
        qualityControl.hidden = true;
    }
    
    convertBtn.disabled = false;
}

// Image Conversion
async function handleConvert() {
    if (!currentImageId || !selectedFormat) {
        showToast('Please select an output format', 'warning');
        return;
    }
    
    const quality = qualitySlider.value;
    
    try {
        // Show loading state
        convertBtn.disabled = true;
        const btnText = convertBtn.querySelector('.btn-text');
        const spinner = convertBtn.querySelector('.spinner');
        const icon = convertBtn.querySelector('i');
        
        btnText.textContent = 'Converting...';
        spinner.hidden = false;
        icon.hidden = true;
        
        showToast('Converting image...', 'info');
        
        const formData = new FormData();
        formData.append('id', currentImageId);
        formData.append('format', selectedFormat);
        formData.append('quality', quality);
        
        const response = await fetch(`${API_BASE_URL}/convert`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Conversion failed');
        }
        
        const data = await response.json();
        
        // Show results
        showResults(data);
        loadHistory(); // Refresh history
        
        showToast('Conversion successful!', 'success');
        
    } catch (error) {
        showError(`Conversion failed: ${error.message}`);
        showToast(`Conversion failed: ${error.message}`, 'error');
    } finally {
        // Reset button state
        convertBtn.disabled = false;
        const btnText = convertBtn.querySelector('.btn-text');
        const spinner = convertBtn.querySelector('.spinner');
        const icon = convertBtn.querySelector('i');
        
        btnText.textContent = 'Convert Image';
        spinner.hidden = true;
        icon.hidden = false;
    }
}

// Show Results
function showResults(data) {
    conversionSection.hidden = true;
    resultSection.hidden = false;
    
    // Set preview image
    resultImage.src = `${API_BASE_URL}/image/${data.id}`;
    
    // Set stats
    originalSizeEl.textContent = formatFileSize(data.original_size);
    convertedSizeEl.textContent = formatFileSize(data.converted_size);
    
    const savingsClass = data.savings_percent >= 0 ? 'savings' : '';
    const savingsPrefix = data.savings_percent >= 0 ? '-' : '+';
    savingsPercentEl.innerHTML = `<span class="${savingsClass}">${savingsPrefix}${Math.abs(data.savings_percent).toFixed(1)}%</span>`;
    
    // Scroll to results
    setTimeout(() => {
        resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}

// Download
async function handleDownload() {
    if (!currentImageId) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/download/${currentImageId}`);
        
        if (!response.ok) {
            throw new Error('Download failed');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        
        // Get filename from Content-Disposition header if available
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = 'converted_image';
        if (contentDisposition) {
            const match = contentDisposition.match(/filename="?(.+)"?/);
            if (match) filename = match[1];
        }
        
        // Trigger download
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        showToast('Download started!', 'success');
        
    } catch (error) {
        showToast(`Download failed: ${error.message}`, 'error');
    }
}

// Load History
async function loadHistory() {
    try {
        const response = await fetch(`${API_BASE_URL}/images`);
        
        if (!response.ok) {
            throw new Error('Failed to load history');
        }
        
        const data = await response.json();
        renderHistory(data.images);
        
    } catch (error) {
        console.error('Error loading history:', error);
        historyList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-exclamation-circle"></i>
                <p>Failed to load history</p>
            </div>
        `;
    }
}

function renderHistory(images) {
    if (!images || images.length === 0) {
        historyList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-inbox"></i>
                <p>No conversions yet. Upload an image to get started!</p>
            </div>
        `;
        return;
    }
    
    historyList.innerHTML = images.map(img => `
        <div class="history-item">
            <img class="history-thumb" src="${img.status === 'completed' ? `${API_BASE_URL}/image/${img.id}` : ''}" 
                 alt="" onerror="this.style.display='none'">
            <div class="history-info">
                <span class="history-name">${escapeHtml(img.original_name)}</span>
                <span class="history-meta">
                    ${img.original_format} → ${img.converted_format || 'N/A'} 
                    • ${formatFileSize(parseInt(img.file_size) || 0)}
                </span>
            </div>
            <span class="history-status ${img.status}">${img.status}</span>
            <div class="history-actions">
                ${img.status === 'completed' ? `
                    <button class="btn btn-primary" onclick="downloadHistoryImage('${img.id}')">
                        <i class="fas fa-download"></i>
                    </button>
                ` : ''}
                <button class="btn btn-secondary" onclick="deleteHistoryImage('${img.id}')">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `).join('');
}

// History Actions
window.downloadHistoryImage = async function(imageId) {
    try {
        const response = await fetch(`${API_BASE_URL}/download/${imageId}`);
        
        if (!response.ok) {
            throw new Error('Download failed');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `converted_image`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
    } catch (error) {
        showToast(`Download failed: ${error.message}`, 'error');
    }
};

window.deleteHistoryImage = async function(imageId) {
    if (!confirm('Are you sure you want to delete this image?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/image/${imageId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error('Delete failed');
        }
        
        showToast('Image deleted', 'success');
        loadHistory();
        
    } catch (error) {
        showToast(`Delete failed: ${error.message}`, 'error');
    }
};

// Utility Functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showError(message) {
    errorMessage.textContent = message;
    uploadError.hidden = false;
}

function hideError() {
    uploadError.hidden = true;
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: '<i class="fas fa-check-circle"></i>',
        error: '<i class="fas fa-exclamation-circle"></i>',
        warning: '<i class="fas fa-exclamation-triangle"></i>',
        info: '<i class="fas fa-info-circle"></i>'
    };
    
    toast.innerHTML = `
        ${icons[type]}
        <span>${escapeHtml(message)}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (toast.parentElement) {
            toast.style.animation = 'slideIn 0.3s ease reverse';
            setTimeout(() => toast.remove(), 300);
        }
    }, 5000);
}

// Reset Functions
function resetUpload() {
    currentFile = null;
    currentImageId = null;
    fileInput.value = '';
    
    uploadContent.hidden = false;
    uploadPreview.hidden = true;
    conversionSection.hidden = true;
    
    hideError();
}

function resetAll() {
    resetUpload();
    
    // Reset format selection
    formatCards.forEach(card => card.classList.remove('active'));
    selectedFormat = null;
    
    // Reset quality
    qualitySlider.value = 85;
    qualityValue.textContent = '85';
    qualityControl.hidden = false;
    
    // Reset button
    convertBtn.disabled = true;
    
    // Hide result section
    resultSection.hidden = true;
    
    // Scroll to top
    document.getElementById('converter').scrollIntoView({ behavior: 'smooth' });
}

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});
