// Face Recognition System Frontend JavaScript

class FaceRecognitionApp {
    constructor() {
        this.currentTab = 'upload';
        this.webcamStream = null;
        this.recognitionInterval = null;
        this.similarityThreshold = 0.6;
        
        this.init();
        this.loadManagePeople();
    }

    init() {
        this.setupEventListeners();
        this.setupDragAndDrop();
    }

    setupEventListeners() {
        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tab = e.currentTarget.dataset.tab;
                this.switchTab(tab);
            });
        });

        // Upload form
        document.getElementById('uploadForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.uploadPhoto();
        });

        // Generate embeddings
        document.getElementById('generateBtn').addEventListener('click', () => {
            this.generateEmbeddings();
        });

        // Webcam controls
        document.getElementById('startWebcam').addEventListener('click', () => {
            this.startWebcam();
        });

        document.getElementById('stopWebcam').addEventListener('click', () => {
            this.stopWebcam();
        });

        // Similarity threshold
        document.getElementById('similarityThreshold').addEventListener('input', (e) => {
            this.similarityThreshold = parseFloat(e.target.value);
            document.getElementById('thresholdValue').textContent = this.similarityThreshold.toFixed(1);
        });

        // File input change
        document.getElementById('photoFile').addEventListener('change', (e) => {
            this.previewImage(e.target.files[0]);
        });
    }

    setupDragAndDrop() {
        const uploadArea = document.querySelector('.border-dashed').parentElement;
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                document.getElementById('photoFile').files = files;
                this.previewImage(files[0]);
            }
        });
    }

    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('text-blue-600', 'border-b-2', 'border-blue-600');
            btn.classList.add('text-gray-600');
        });

        document.querySelector(`[data-tab="${tabName}"]`).classList.remove('text-gray-600');
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('text-blue-600', 'border-b-2', 'border-blue-600');

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.add('hidden');
        });

        document.getElementById(`${tabName}-tab`).classList.remove('hidden');

        this.currentTab = tabName;

        // Load data for specific tabs
        if (tabName === 'manage') {
            this.loadManagePeople();
        }
    }

    async uploadPhoto() {
        const formData = new FormData();
        const fileInput = document.getElementById('photoFile');
        const nameInput = document.getElementById('personName');

        if (!fileInput.files[0] || !nameInput.value.trim()) {
            this.showToast('Please provide both name and photo', 'error');
            return;
        }

        formData.append('file', fileInput.files[0]);
        formData.append('name', nameInput.value.trim());

        try {
            this.setLoading('generateBtn', true);
            
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                this.showToast(`Photo uploaded successfully for ${result.name}`, 'success');
                document.getElementById('uploadForm').reset();
            } else {
                this.showToast(result.error || 'Upload failed', 'error');
            }
        } catch (error) {
            this.showToast('Upload failed: ' + error.message, 'error');
        } finally {
            this.setLoading('generateBtn', false);
        }
    }

    async generateEmbeddings() {
        try {
            document.getElementById('generateStatus').classList.remove('hidden');
            this.setLoading('generateBtn', true);

            const response = await fetch('/api/generate_embeddings', {
                method: 'POST'
            });

            const result = await response.json();

            if (result.success) {
                this.showToast(`Embeddings generated for ${result.count} people`, 'success');
            } else {
                this.showToast(result.error || 'Failed to generate embeddings', 'error');
            }
        } catch (error) {
            this.showToast('Failed to generate embeddings: ' + error.message, 'error');
        } finally {
            document.getElementById('generateStatus').classList.add('hidden');
            this.setLoading('generateBtn', false);
        }
    }

    
    async loadManagePeople() {
        try {
            const response = await fetch('/api/people');
            const people = await response.json();

            const manageList = document.getElementById('managePeopleList');
            manageList.innerHTML = '';

            if (people.length === 0) {
                manageList.innerHTML = `
                    <div class="text-center py-8 text-gray-500">
                        <i class="fas fa-user-slash text-4xl mb-2"></i>
                        <p>No people in dataset yet</p>
                    </div>
                `;
                return;
            }

            people.forEach(person => {
                const personItem = document.createElement('div');
                personItem.className = 'flex items-center justify-between p-4 bg-gray-50 rounded-lg';
                personItem.innerHTML = `
                    <div class="flex items-center space-x-4">
                        <img src="/uploads/${person.filename}" alt="${person.name}" 
                             class="w-16 h-16 object-cover rounded-lg"
                             onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjQiIGhlaWdodD0iNjQiIHZpZXdCb3g9IjAgMCA2NCA2NCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjY0IiBoZWlnaHQ9IjY0IiBmaWxsPSIjRjNGNEY2Ii8+CjxwYXRoIGQ9Ik0zMiAzMkMzOC42Mjc0IDMyIDQ0IDI2LjYyNzQgNDQgMjBDNDQgMTMuMzcyNiAzOC42Mjc0IDggMzIgOEMyNS4zNzI2IDggMjAgMTMuMzcyNiAyMCAyMEMyMCAyNi42Mjc0IDI1LjM3MjYgMzIgMzIgMzJaIiBmaWxsPSIjOUNBM0FGIi8+CjxwYXRoIGQ9Ik0xNiA1NEgxMlY0NkMxMiA0My4zMTQzIDE0LjMxNDMgNDEgMTYgNDFIMTZWMTZIMjRWNDFIMjRDMjYuNjg1NyA0MSAyOSA0My4zMTQzIDI5IDQ2VjU0SDE2WiIgZmlsbD0iIzlDQTNBRiIvPgo8cGF0aCBkPSJNNDAgNTRINDhWNDZDNDggNDMuMzE0MyA0NS42ODU3IDQxIDQzIDQxSDQzVjE2SDMzVjQxSDMzQzMwLjMxNDMgNDEgMjggNDMuMzE0MyAyOCA0NlY1NEg0MFoiIGZpbGw9IiM5Q0EzQUYiLz4KPC9zdmc+'">
                        <div>
                            <h3 class="font-medium text-gray-900">${person.name}</h3>
                            <p class="text-sm text-gray-500">${person.filename}</p>
                        </div>
                    </div>
                    <div class="flex space-x-2">
                        <button onclick="app.deletePerson('${person.name}')" 
                                class="px-3 py-1 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors">
                            <i class="fas fa-trash mr-1"></i>Delete
                        </button>
                    </div>
                `;
                manageList.appendChild(personItem);
            });
        } catch (error) {
            console.error('Failed to load manage people:', error);
        }
    }

    async deletePerson(name) {
        if (!confirm(`Are you sure you want to delete ${name} from the dataset?`)) {
            return;
        }

        try {
            const response = await fetch(`/api/delete_person/${name}`, {
                method: 'DELETE'
            });

            const result = await response.json();

            if (result.success) {
                this.showToast(`${name} deleted successfully`, 'success');
                if (this.currentTab === 'manage') {
                    this.loadManagePeople();
                }
            } else {
                this.showToast(result.error || 'Failed to delete person', 'error');
            }
        } catch (error) {
            this.showToast('Failed to delete person: ' + error.message, 'error');
        }
    }

    async startWebcam() {
        try {
            const video = document.getElementById('webcam');
            this.webcamStream = await navigator.mediaDevices.getUserMedia({ 
                video: { 
                    width: { ideal: 640 },
                    height: { ideal: 480 }
                } 
            });
            
            video.srcObject = this.webcamStream;
            
            // Start recognition loop
            this.recognitionInterval = setInterval(() => {
                this.performRecognition();
            }, 1000); // Recognize every second

            this.showToast('Webcam started', 'success');
            this.updateStatus('Camera Active', 'processing');
        } catch (error) {
            this.showToast('Failed to access webcam: ' + error.message, 'error');
        }
    }

    stopWebcam() {
        if (this.webcamStream) {
            this.webcamStream.getTracks().forEach(track => track.stop());
            this.webcamStream = null;
        }

        if (this.recognitionInterval) {
            clearInterval(this.recognitionInterval);
            this.recognitionInterval = null;
        }

        const video = document.getElementById('webcam');
        video.srcObject = null;

        // Clear results
        document.getElementById('recognitionResults').innerHTML = `
            <div class="bg-gray-50 rounded-lg p-4 text-center text-gray-500">
                <i class="fas fa-user-slash text-3xl mb-2"></i>
                <p>No faces detected yet</p>
            </div>
        `;

        // Clear overlay
        const canvas = document.getElementById('overlay');
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        this.showToast('Webcam stopped', 'info');
        this.updateStatus('Ready', 'ready');
    }

    async performRecognition() {
        const video = document.getElementById('webcam');
        const canvas = document.getElementById('overlay');
        
        // Set canvas size to match video
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        // Create a temporary canvas to capture current frame
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = video.videoWidth;
        tempCanvas.height = video.videoHeight;
        const tempCtx = tempCanvas.getContext('2d');
        tempCtx.drawImage(video, 0, 0);

        // Convert to blob and send to server
        tempCanvas.toBlob(async (blob) => {
            const formData = new FormData();
            formData.append('file', blob, 'webcam_frame.jpg');

            try {
                const response = await fetch('/api/recognize', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();
                this.displayRecognitionResults(result.faces);
                this.drawBoundingBoxes(result.faces, canvas);
            } catch (error) {
                console.error('Recognition failed:', error);
            }
        }, 'image/jpeg', 0.8);
    }

    displayRecognitionResults(faces) {
        const resultsDiv = document.getElementById('recognitionResults');
        
        if (faces.length === 0) {
            resultsDiv.innerHTML = `
                <div class="bg-gray-50 rounded-lg p-4 text-center text-gray-500">
                    <i class="fas fa-user-slash text-3xl mb-2"></i>
                    <p>No faces detected</p>
                </div>
            `;
            return;
        }

        resultsDiv.innerHTML = '';
        faces.forEach(face => {
            const resultDiv = document.createElement('div');
            resultDiv.className = `recognition-result p-3 rounded-lg ${
                face.name === 'Unknown' ? 'unknown bg-red-50' : 'known bg-green-50'
            }`;
            
            const similarityPercent = (face.similarity * 100).toFixed(1);
            resultDiv.innerHTML = `
                <div class="flex items-center justify-between">
                    <div>
                        <p class="font-medium ${face.name === 'Unknown' ? 'text-red-800' : 'text-green-800'}">
                            ${face.name}
                        </p>
                        <p class="text-sm text-gray-600">
                            Confidence: ${similarityPercent}%
                        </p>
                    </div>
                    <div class="text-2xl">
                        ${face.name === 'Unknown' ? '❓' : '✅'}
                    </div>
                </div>
            `;
            resultsDiv.appendChild(resultDiv);
        });
    }

    drawBoundingBoxes(faces, canvas) {
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        faces.forEach(face => {
            const [x1, y1, x2, y2] = face.bbox;
            
            // Set color based on recognition
            if (face.name === 'Unknown') {
                ctx.strokeStyle = '#ef4444'; // Red
                ctx.fillStyle = '#ef4444';
            } else {
                ctx.strokeStyle = '#10b981'; // Green
                ctx.fillStyle = '#10b981';
            }

            // Draw bounding box
            ctx.lineWidth = 2;
            ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);

            // Draw label background
            const label = `${face.name} (${(face.similarity * 100).toFixed(1)}%)`;
            ctx.font = '14px sans-serif';
            const textWidth = ctx.measureText(label).width;
            
            // Background for text
            ctx.fillRect(x1, y1 - 25, textWidth + 8, 20);
            
            // Text
            ctx.fillStyle = 'white';
            ctx.fillText(label, x1 + 4, y1 - 10);
        });
    }

    previewImage(file) {
        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                // You could add a preview here if needed
            };
            reader.readAsDataURL(file);
        }
    }

    setLoading(buttonId, loading) {
        const button = document.getElementById(buttonId);
        if (loading) {
            button.classList.add('loading');
            button.disabled = true;
            button.innerHTML = '<i class="spinner mr-2"></i>Processing...';
        } else {
            button.classList.remove('loading');
            button.disabled = false;
            button.innerHTML = button.getAttribute('data-original-text') || 
                              (buttonId === 'generateBtn' ? '<i class="fas fa-magic mr-2"></i>Generate Embeddings' : 
                               '<i class="fas fa-upload mr-2"></i>Upload Photo');
        }
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        
        toast.className = `toast ${type} text-white px-4 py-3 rounded-lg shadow-lg flex items-center space-x-2`;
        
        const icon = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        }[type];

        toast.innerHTML = `
            <i class="${icon}"></i>
            <span>${message}</span>
        `;

        container.appendChild(toast);

        // Auto remove after 3 seconds
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => {
                container.removeChild(toast);
            }, 300);
        }, 3000);
    }

    updateStatus(text, type = 'ready') {
        const status = document.getElementById('status');
        const colors = {
            ready: 'bg-green-500',
            processing: 'bg-yellow-500',
            error: 'bg-red-500'
        };

        status.className = `text-sm ${colors[type]} px-3 py-1 rounded-full`;
        status.innerHTML = `<i class="fas fa-circle text-xs mr-1"></i> ${text}`;
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new FaceRecognitionApp();
});
