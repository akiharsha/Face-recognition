"""
Generate Face Embeddings Script
===============================

This script:
1. Loads YOLOv8 for face detection
2. Loads FaceNet for face embedding generation
3. Processes reference images from dataset folder
4. Generates and saves face embeddings to embeddings.pkl

Author: Face Recognition System
"""

import os
import pickle
import numpy as np
from pathlib import Path
import cv2
from ultralytics import YOLO
from facenet_pytorch import InceptionResnetV1
import torch
from PIL import Image
from tqdm import tqdm


class FaceEmbeddingGenerator:
    def __init__(self):
        """Initialize YOLOv8 and FaceNet models"""
        print("🔧 Initializing models...")
        
        # Load YOLOv8 for face detection
        self.yolo_model = YOLO('yolov8n.pt')  # Nano version for faster inference
        
        # Load FaceNet for face embeddings
        # Using InceptionResnetV1 pretrained on VGGFace2
        self.facenet_model = InceptionResnetV1(pretrained='vggface2').eval()
        
        # Check if GPU is available
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.facenet_model = self.facenet_model.to(self.device)
        
        print(f"✅ Models loaded successfully!")
        print(f"📱 Using device: {self.device}")
    
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
    
    def process_dataset(self, dataset_path="dataset"):
        """
        Process all reference images in dataset folder
        
        Args:
            dataset_path: Path to dataset folder
            
        Returns:
            Dictionary of {person_name: embedding}
        """
        dataset_path = Path(dataset_path)
        embeddings_dict = {}
        
        if not dataset_path.exists():
            print(f"❌ Dataset folder not found: {dataset_path}")
            return embeddings_dict
        
        # Get all image files directly in dataset folder
        image_files = list(dataset_path.glob("*.jpg")) + list(dataset_path.glob("*.png")) + list(dataset_path.glob("*.jpeg"))
        
        if not image_files:
            print(f"❌ No image files found in {dataset_path}")
            print("📁 Add photos like: dataset/harsha.jpg, dataset/rahul.jpg")
            return embeddings_dict
        
        print(f"👥 Found {len(image_files)} people in dataset")
        
        for image_path in tqdm(image_files, desc="Processing people"):
            # Extract person name from filename (remove extension)
            person_name = image_path.stem
            print(f"\n📸 Processing {person_name}: {image_path.name}")
            
            # Load image
            image = cv2.imread(str(image_path))
            if image is None:
                print(f"❌ Could not load image: {image_path}")
                continue
            
            # Detect faces
            faces = self.detect_faces(image)
            
            if not faces:
                print(f"❌ No faces detected in {image_path}")
                continue
            
            if len(faces) > 1:
                print(f"⚠️  Multiple faces detected in {image_path}, using largest one")
                # Use largest face
                faces.sort(key=lambda x: (x[2] - x[0]) * (x[3] - x[1]), reverse=True)
            
            # Extract face and generate embedding
            face_bbox = faces[0]
            face_tensor = self.extract_face(image, face_bbox)
            embedding = self.generate_embedding(face_tensor)
            
            embeddings_dict[person_name] = embedding
            print(f"✅ Generated embedding for {person_name}")
        
        return embeddings_dict
    
    def save_embeddings(self, embeddings_dict, output_path="embeddings/embeddings.pkl"):
        """
        Save embeddings to pickle file
        
        Args:
            embeddings_dict: Dictionary of {person_name: embedding}
            output_path: Output file path
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'wb') as f:
            pickle.dump(embeddings_dict, f)
        
        print(f"💾 Saved {len(embeddings_dict)} embeddings to {output_path}")
    
    def load_embeddings(self, embeddings_path="embeddings/embeddings.pkl"):
        """
        Load embeddings from pickle file
        
        Args:
            embeddings_path: Path to embeddings file
            
        Returns:
            Dictionary of {person_name: embedding}
        """
        if not os.path.exists(embeddings_path):
            print(f"❌ Embeddings file not found: {embeddings_path}")
            return {}
        
        with open(embeddings_path, 'rb') as f:
            embeddings_dict = pickle.load(f)
        
        print(f"📂 Loaded {len(embeddings_dict)} embeddings from {embeddings_path}")
        return embeddings_dict


def main():
    """Main function to generate embeddings"""
    print("🚀 Face Embedding Generator")
    print("=" * 50)
    
    # Initialize generator
    generator = FaceEmbeddingGenerator()
    
    # Process dataset
    embeddings_dict = generator.process_dataset()
    
    if embeddings_dict:
        # Save embeddings
        generator.save_embeddings(embeddings_dict)
        
        print("\n✅ Embedding generation completed successfully!")
        print(f"📊 Processed {len(embeddings_dict)} people:")
        for name in embeddings_dict.keys():
            print(f"   - {name}")
    else:
        print("\n❌ No embeddings generated. Please check your dataset structure.")
        print("📁 Expected structure:")
        print("   dataset/")
        print("     harsha.jpg")
        print("     rahul.jpg")
        print("     priya.png")


if __name__ == "__main__":
    main()
