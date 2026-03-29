"""
Flask Web Application for Face Recognition System
=================================================

This web application provides:
1. File upload interface for adding reference photos
2. Embedding generation management
3. Real-time face recognition via webcam
4. Person management (add/remove people)

Author: Face Recognition System
"""

import os
import pickle
import numpy as np
from pathlib import Path
import cv2
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from ultralytics import YOLO
from facenet_pytorch import InceptionResnetV1
import torch
from PIL import Image
from scipy.spatial.distance import cosine

app = Flask(__name__)
CORS(app)

# Configuration
app.config['UPLOAD_FOLDER'] = 'dataset'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SECRET_KEY'] = 'face_recognition_secret_key'

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Global variables for models
yolo_model = None
facenet_model = None
device = None
embeddings_dict = {}

def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_models():
    """Load YOLOv8 and FaceNet models"""
    global yolo_model, facenet_model, device
    
    print("🔧 Loading models...")
    
    # Load YOLOv8 for face detection
    yolo_model = YOLO('yolov8n.pt')
    
    # Load FaceNet for face embeddings
    facenet_model = InceptionResnetV1(pretrained='vggface2').eval()
    
    # Check if GPU is available
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    facenet_model = facenet_model.to(device)
    
    print(f"✅ Models loaded successfully!")
    print(f"📱 Using device: {device}")

def load_embeddings():
    """Load existing embeddings"""
    global embeddings_dict
    embeddings_path = "embeddings/embeddings.pkl"
    
    if os.path.exists(embeddings_path):
        with open(embeddings_path, 'rb') as f:
            embeddings_dict = pickle.load(f)
        print(f"📂 Loaded {len(embeddings_dict)} embeddings")
    else:
        embeddings_dict = {}
        print("📂 No existing embeddings found")

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
    face_pil = Image.fromarray(face_rgb)
    face_pil = face_pil.resize((160, 160))
    
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

def generate_embeddings_from_dataset():
    """Generate embeddings from all images in dataset folder"""
    dataset_path = Path("dataset")
    new_embeddings = {}
    
    if not dataset_path.exists():
        return {"error": "Dataset folder not found"}
    
    image_files = list(dataset_path.glob("*.jpg")) + list(dataset_path.glob("*.png")) + list(dataset_path.glob("*.jpeg"))
    
    for image_path in image_files:
        person_name = image_path.stem
        image = cv2.imread(str(image_path))
        
        if image is None:
            continue
        
        faces = detect_faces(image)
        
        if not faces:
            continue
        
        if len(faces) > 1:
            faces.sort(key=lambda x: (x[2] - x[0]) * (x[3] - x[1]), reverse=True)
        
        face_bbox = faces[0]
        face_tensor = extract_face(image, face_bbox)
        embedding = generate_embedding(face_tensor)
        
        new_embeddings[person_name] = embedding
    
    # Save embeddings
    os.makedirs("embeddings", exist_ok=True)
    with open("embeddings/embeddings.pkl", 'wb') as f:
        pickle.dump(new_embeddings, f)
    
    global embeddings_dict
    embeddings_dict = new_embeddings
    
    return {"success": True, "count": len(new_embeddings), "people": list(new_embeddings.keys())}

# Routes
@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/people')
def get_people():
    """Get list of all people in the dataset"""
    dataset_path = Path("dataset")
    people = []
    
    if dataset_path.exists():
        image_files = list(dataset_path.glob("*.jpg")) + list(dataset_path.glob("*.png")) + list(dataset_path.glob("*.jpeg"))
        people = [{"name": f.stem, "filename": f.name} for f in image_files]
    
    return jsonify(people)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload a reference photo"""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    name = request.form.get('name', '').strip()
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not name:
        return jsonify({"error": "Name is required"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400
    
    # Create secure filename
    filename = secure_filename(f"{name}.jpg")
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Save file
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    file.save(filepath)
    
    return jsonify({"success": True, "filename": filename, "name": name})

@app.route('/api/generate_embeddings', methods=['POST'])
def api_generate_embeddings():
    """Generate embeddings from dataset"""
    result = generate_embeddings_from_dataset()
    return jsonify(result)

@app.route('/api/recognize', methods=['POST'])
def api_recognize():
    """Recognize face from uploaded image"""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
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
            "bbox": face[:4]  # x1, y1, x2, y2
        })
    
    return jsonify({"faces": results})

@app.route('/api/delete_person/<name>', methods=['DELETE'])
def delete_person(name):
    """Delete a person from dataset"""
    dataset_path = Path("dataset")
    
    # Find and delete image file
    for ext in ['.jpg', '.png', '.jpeg']:
        filepath = dataset_path / f"{name}{ext}"
        if filepath.exists():
            filepath.unlink()
            break
    
    # Regenerate embeddings
    result = generate_embeddings_from_dataset()
    
    return jsonify(result)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    # Initialize models
    load_models()
    load_embeddings()
    
    # Run the app
    # For production, use: debug=False, host='127.0.0.1'
    app.run(debug=True, host='127.0.0.1', port=5000)
