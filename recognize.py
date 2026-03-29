"""
Real-time Face Recognition Script
==================================

This script:
1. Loads pre-generated face embeddings
2. Captures video from webcam
3. Detects faces using YOLOv8
4. Recognizes faces using FaceNet embeddings
5. Displays bounding boxes with names and similarity scores

Author: Face Recognition System
"""

import os
import pickle
import numpy as np
import cv2
from ultralytics import YOLO
from facenet_pytorch import InceptionResnetV1
import torch
from PIL import Image
from scipy.spatial.distance import cosine
import time


class FaceRecognizer:
    def __init__(self, embeddings_path="embeddings/embeddings.pkl", similarity_threshold=0.6):
        """
        Initialize face recognizer
        
        Args:
            embeddings_path: Path to embeddings pickle file
            similarity_threshold: Minimum similarity score for recognition
        """
        print("🔧 Initializing face recognizer...")
        
        # Load embeddings
        self.embeddings_dict = self.load_embeddings(embeddings_path)
        self.person_names = list(self.embeddings_dict.keys())
        self.person_embeddings = np.array(list(self.embeddings_dict.values()))
        
        if not self.person_names:
            print("❌ No embeddings found. Please run generate_embeddings.py first.")
            exit(1)
        
        print(f"📂 Loaded {len(self.person_names)} face embeddings")
        
        # Load YOLOv8 for face detection
        self.yolo_model = YOLO('yolov8n.pt')
        
        # Load FaceNet for face embeddings
        self.facenet_model = InceptionResnetV1(pretrained='vggface2').eval()
        
        # Check if GPU is available
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.facenet_model = self.facenet_model.to(self.device)
        
        # Set similarity threshold
        self.similarity_threshold = similarity_threshold
        
        print(f"✅ Models loaded successfully!")
        print(f"📱 Using device: {self.device}")
        print(f"🎯 Similarity threshold: {self.similarity_threshold}")
        
        # Colors for different people
        self.colors = self.generate_colors(len(self.person_names))
    
    def generate_colors(self, num_colors):
        """Generate distinct colors for different people"""
        colors = []
        for i in range(num_colors):
            hue = i * 360 / num_colors
            # Convert HSV to RGB
            c = np.array([hue, 0.8, 0.8])
            rgb = cv2.cvtColor(np.uint8([[c]]), cv2.COLOR_HSV2RGB)[0][0]
            colors.append(rgb.tolist())
        return colors
    
    def load_embeddings(self, embeddings_path):
        """Load embeddings from pickle file"""
        if not os.path.exists(embeddings_path):
            print(f"❌ Embeddings file not found: {embeddings_path}")
            return {}
        
        with open(embeddings_path, 'rb') as f:
            embeddings_dict = pickle.load(f)
        
        return embeddings_dict
    
    def detect_faces(self, image):
        """
        Detect faces in image using YOLOv8
        
        Args:
            image: Input image (numpy array)
            
        Returns:
            List of bounding boxes [x1, y1, x2, y2, confidence]
        """
        results = self.yolo_model(image, classes=[0])  # Class 0 = person
        faces = []
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Get bounding box coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = box.conf[0].cpu().numpy()
                
                # Convert to integers
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                
                # Filter by confidence and size
                if confidence > 0.5 and (x2 - x1) > 50 and (y2 - y1) > 50:
                    faces.append([x1, y1, x2, y2, confidence])
        
        return faces
    
    def extract_face(self, image, bbox):
        """
        Extract and preprocess face from image
        
        Args:
            image: Input image (numpy array)
            bbox: Bounding box [x1, y1, x2, y2, confidence]
            
        Returns:
            Preprocessed face tensor
        """
        x1, y1, x2, y2, _ = bbox
        
        # Extract face
        face = image[y1:y2, x1:x2]
        
        # Convert to RGB
        face_rgb = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
        
        # Convert to PIL Image
        face_pil = Image.fromarray(face_rgb)
        
        # Resize to FaceNet input size (160x160)
        face_pil = face_pil.resize((160, 160))
        
        # Convert to tensor and normalize
        face_tensor = torch.FloatTensor(np.array(face_pil)) / 255.0
        face_tensor = face_tensor.permute(2, 0, 1)  # HWC -> CHW
        face_tensor = face_tensor.unsqueeze(0)  # Add batch dimension
        
        # Normalize using ImageNet mean and std
        mean = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)
        std = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)
        face_tensor = (face_tensor - mean) / std
        
        return face_tensor.to(self.device)
    
    def generate_embedding(self, face_tensor):
        """
        Generate face embedding using FaceNet
        
        Args:
            face_tensor: Preprocessed face tensor
            
        Returns:
            Face embedding vector (numpy array)
        """
        with torch.no_grad():
            embedding = self.facenet_model(face_tensor)
            embedding = embedding.cpu().numpy()
            # Normalize embedding
            embedding = embedding / np.linalg.norm(embedding)
        
        return embedding[0]  # Remove batch dimension
    
    def recognize_face(self, embedding):
        """
        Recognize face by comparing with stored embeddings
        
        Args:
            embedding: Face embedding vector
            
        Returns:
            Tuple of (person_name, similarity_score)
        """
        if len(self.person_embeddings) == 0:
            return "Unknown", 0.0
        
        # Calculate cosine similarity with all stored embeddings
        similarities = []
        for stored_embedding in self.person_embeddings:
            # Cosine similarity = 1 - cosine distance
            similarity = 1 - cosine(embedding, stored_embedding)
            similarities.append(similarity)
        
        similarities = np.array(similarities)
        
        # Get best match
        best_idx = np.argmax(similarities)
        best_similarity = similarities[best_idx]
        
        if best_similarity >= self.similarity_threshold:
            return self.person_names[best_idx], best_similarity
        else:
            return "Unknown", best_similarity
    
    def draw_results(self, image, faces, recognitions):
        """
        Draw bounding boxes and labels on image
        
        Args:
            image: Input image
            faces: List of face bounding boxes
            recognitions: List of (name, similarity) tuples
        """
        for i, (face, (name, similarity)) in enumerate(zip(faces, recognitions)):
            x1, y1, x2, y2, confidence = face
            
            # Choose color based on recognition
            if name == "Unknown":
                color = (0, 0, 255)  # Red for unknown
            else:
                person_idx = self.person_names.index(name)
                color = tuple(int(c) for c in self.colors[person_idx % len(self.colors)])
            
            # Draw bounding box
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
            
            # Prepare label text
            label = f"{name} ({similarity:.2f})"
            
            # Calculate text size and position
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            thickness = 2
            (text_width, text_height), baseline = cv2.getTextSize(label, font, font_scale, thickness)
            
            # Draw background for text
            cv2.rectangle(image, (x1, y1 - text_height - 10), 
                         (x1 + text_width, y1), color, -1)
            
            # Draw text
            cv2.putText(image, label, (x1, y1 - 5), font, font_scale, (255, 255, 255), thickness)
        
        return image
    
    def run_webcam(self, camera_index=0):
        """
        Run real-time face recognition on webcam
        
        Args:
            camera_index: Webcam camera index
        """
        print("🎥 Starting webcam...")
        print("Press 'q' to quit, 's' to save current frame")
        
        # Initialize webcam
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            print(f"❌ Could not open camera {camera_index}")
            return
        
        # Set camera properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # FPS calculation
        fps_counter = 0
        fps_start_time = time.time()
        current_fps = 0
        
        print("✅ Webcam started successfully!")
        print("🎯 Face recognition is now running...")
        
        while True:
            # Read frame
            ret, frame = cap.read()
            
            if not ret:
                print("❌ Could not read frame from camera")
                break
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Detect faces
            faces = self.detect_faces(frame)
            
            # Recognize faces
            recognitions = []
            for face in faces:
                face_tensor = self.extract_face(frame, face)
                embedding = self.generate_embedding(face_tensor)
                name, similarity = self.recognize_face(embedding)
                recognitions.append((name, similarity))
            
            # Draw results
            frame = self.draw_results(frame, faces, recognitions)
            
            # Calculate FPS
            fps_counter += 1
            if fps_counter >= 10:
                current_fps = fps_counter / (time.time() - fps_start_time)
                fps_counter = 0
                fps_start_time = time.time()
            
            # Display FPS
            cv2.putText(frame, f"FPS: {current_fps:.1f}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Display instructions
            cv2.putText(frame, "Press 'q' to quit", (10, frame.shape[0] - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Show frame
            cv2.imshow("Face Recognition", frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                # Save current frame
                timestamp = int(time.time())
                filename = f"capture_{timestamp}.jpg"
                cv2.imwrite(filename, frame)
                print(f"📸 Saved frame as {filename}")
        
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        print("👋 Face recognition stopped")


def main():
    """Main function to run face recognition"""
    print("🚀 Real-time Face Recognition")
    print("=" * 50)
    
    # Check if embeddings exist
    embeddings_path = "embeddings/embeddings.pkl"
    if not os.path.exists(embeddings_path):
        print("❌ No embeddings found!")
        print("📝 Please run 'python generate_embeddings.py' first")
        return
    
    # Initialize recognizer
    recognizer = FaceRecognizer(embeddings_path, similarity_threshold=0.6)
    
    # Run webcam recognition
    recognizer.run_webcam()


if __name__ == "__main__":
    main()
