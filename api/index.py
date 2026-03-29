"""
Vercel Serverless Function for Face Recognition
==========================================

Modified for Vercel deployment with serverless constraints
"""

import os
import json
import numpy as np
from pathlib import Path
import cv2
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from scipy.spatial.distance import cosine
import base64
import tempfile

app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'face_recognition_secret_key')

# Global variables (loaded once)
yolo_model = None
facenet_model = None
device = None
embeddings_dict = {}

def load_models():
    """Load models in serverless environment"""
    global yolo_model, facenet_model, device, embeddings_dict
    
    if yolo_model is None:
        from ultralytics import YOLO
        from facenet_pytorch import InceptionResnetV1
        import torch
        
        print("🔧 Loading models...")
        
        # Load YOLOv8 for face detection
        yolo_model = YOLO('yolov8n.pt')
        
        # Load FaceNet for face embeddings
        facenet_model = InceptionResnetV1(pretrained='vggface2').eval()
        
        # Check device
        device = torch.device('cpu')  # Force CPU for serverless
        facenet_model = facenet_model.to(device)
        
        print(f"✅ Models loaded successfully!")
        print(f"📱 Using device: {device}")
    
    # Load embeddings from static file (for Vercel)
    embeddings_dict = load_embeddings()

def load_embeddings():
    """Load embeddings from file or return empty dict"""
    try:
        import pickle
        # In Vercel, we need to handle this differently
        embeddings_path = "embeddings/embeddings.pkl"
        if os.path.exists(embeddings_path):
            with open(embeddings_path, 'rb') as f:
                embeddings = pickle.load(f)
            print(f"📂 Loaded {len(embeddings)} embeddings")
            return embeddings
    except Exception as e:
        print(f"⚠️ Could not load embeddings: {e}")
    return {}

def detect_faces(image):
    """Detect faces using YOLOv8"""
    results = yolo_model(image, classes=[0])  # Class 0 = person
    faces = []
    
    for result in results:
        boxes = result.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            confidence = box.conf[0].cpu().numpy()
            
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            
            if confidence > 0.5 and (x2 - x1) > 50 and (y2 - y1) > 50:
                faces.append([x1, y1, x2, y2, confidence])
    
    return faces

def extract_face(image, bbox):
    """Extract and preprocess face from image"""
    x1, y1, x2, y2, _ = bbox
    
    face = image[y1:y2, x1:x2]
    face_rgb = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
    
    from PIL import Image
    face_pil = Image.fromarray(face_rgb)
    face_pil = face_pil.resize((160, 160))
    
    import torch
    face_tensor = torch.FloatTensor(np.array(face_pil)) / 255.0
    face_tensor = face_tensor.permute(2, 0, 1)  # HWC -> CHW
    face_tensor = face_tensor.unsqueeze(0)  # Add batch dimension
    
    # Normalize using ImageNet mean and std
    mean = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)
    std = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)
    face_tensor = (face_tensor - mean) / std
    
    return face_tensor.to(device)

def generate_embedding(face_tensor):
    """Generate face embedding using FaceNet"""
    with torch.no_grad():
        embedding = facenet_model(face_tensor)
        embedding = embedding.cpu().numpy()
        embedding = embedding / np.linalg.norm(embedding)
    
    return embedding[0]

def recognize_face(embedding, similarity_threshold=0.6):
    """Recognize face by comparing with stored embeddings"""
    if len(embeddings_dict) == 0:
        return "Unknown", 0.0
    
    person_names = list(embeddings_dict.keys())
    person_embeddings = np.array(list(embeddings_dict.values()))
    
    similarities = []
    for stored_embedding in person_embeddings:
        similarity = 1 - cosine(embedding, stored_embedding)
        similarities.append(similarity)
    
    similarities = np.array(similarities)
    best_idx = np.argmax(similarities)
    best_similarity = similarities[best_idx]
    
    if best_similarity >= similarity_threshold:
        return person_names[best_idx], best_similarity
    else:
        return "Unknown", best_similarity

@app.route('/')
def index():
    """Main endpoint - return HTML"""
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Face Recognition System</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-gray-100">
    <div class="container mx-auto px-4 py-8">
        <div class="bg-white rounded-lg shadow-md p-6">
            <h1 class="text-2xl font-bold mb-4 text-center">Face Recognition System</h1>
            <p class="text-center text-gray-600">Serverless deployment on Vercel</p>
            <div class="mt-6">
                <h2 class="text-lg font-semibold mb-2">Test Recognition</h2>
                <input type="file" id="imageInput" accept="image/*" class="border rounded p-2 w-full">
                <button onclick="testRecognition()" class="bg-blue-600 text-white px-4 py-2 rounded mt-2">Recognize Face</button>
                <div id="results" class="mt-4"></div>
            </div>
        </div>
    </div>
    <script>
        async function testRecognition() {
            const fileInput = document.getElementById('imageInput');
            const results = document.getElementById('results');
            
            if (!fileInput.files[0]) {
                results.innerHTML = '<p class="text-red-600">Please select an image</p>';
                return;
            }
            
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            
            results.innerHTML = '<p class="text-blue-600">Processing...</p>';
            
            try {
                const response = await fetch('/api/recognize', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.faces && result.faces.length > 0) {
                    const face = result.faces[0];
                    const confidence = (face.similarity * 100).toFixed(1);
                    results.innerHTML = `
                        <div class="bg-green-50 border border-green-200 rounded p-4">
                            <p class="font-semibold">Recognized: ${face.name}</p>
                            <p class="text-sm text-gray-600">Confidence: ${confidence}%</p>
                        </div>
                    `;
                } else {
                    results.innerHTML = '<div class="bg-red-50 border border-red-200 rounded p-4"><p class="font-semibold">No face detected</p></div>';
                }
            } catch (error) {
                results.innerHTML = '<p class="text-red-600">Error: ' + error.message + '</p>';
            }
        }
    </script>
</body>
</html>
    '''

@app.route('/api/recognize', methods=['POST'])
def api_recognize():
    """Recognize face from uploaded image"""
    load_models()
    
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    try:
        # Read image
        image_bytes = file.read()
        image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
        
        if image is None:
            return jsonify({"error": "Could not read image"}), 400
        
        # Detect faces
        faces = detect_faces(image)
        
        if not faces:
            return jsonify({"faces": []})
        
        results = []
        for i, face in enumerate(faces):
            face_tensor = extract_face(image, face)
            embedding = generate_embedding(face_tensor)
            name, similarity = recognize_face(embedding)
            
            results.append({
                "id": i,
                "name": name,
                "similarity": float(similarity),
                "bbox": face[:4]
            })
        
        return jsonify({"faces": results})
        
    except Exception as e:
        return jsonify({"error": f"Recognition failed: {str(e)}"}), 500

@app.route('/api/people', methods=['GET'])
def api_people():
    """Get list of people"""
    load_models()
    return jsonify(list(embeddings_dict.keys()))

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    load_models()
    return jsonify({
        'status': 'healthy',
        'models_loaded': bool(yolo_model and facenet_model),
        'embeddings_count': len(embeddings_dict),
        'platform': 'vercel-serverless'
    })

# Vercel serverless handler
def handler(request):
    """Vercel serverless handler"""
    return app(request.environ, lambda start_response: start_response(['200 OK', []), [])

if __name__ == "__main__":
    app.run(debug=False)
