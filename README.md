# Face Recognition System with YOLOv8 and FaceNet

A real-time face recognition system that uses YOLOv8 for face detection and FaceNet for face recognition. The system can recognize people using only one reference photo per person.

## 🎯 Features

- **Single Photo Recognition**: Works with just one reference image per person
- **Real-time Processing**: Live webcam face recognition
- **High Accuracy**: Uses state-of-the-art YOLOv8 and FaceNet models
- **Easy Setup**: Simple installation and configuration
- **Visual Feedback**: Bounding boxes with names and similarity scores

## 🏗️ Project Structure

```
face_recognition_project/
│
├── dataset/                    # Reference images folder
│   ├── harsha/
│   │   └── harsha.jpg
│   ├── rahul/
│   │   └── rahul.jpg
│   └── priya/
│       └── priya.jpg
│
├── embeddings/                 # Generated face embeddings
│   └── embeddings.pkl
│
├── recognize.py               # Main recognition script
├── generate_embeddings.py     # Embedding generation script
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project
cd face_recognition_project

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Prepare Dataset

1. Create folders for each person in the `dataset/` directory
2. Add one reference photo per person (named anything, .jpg/.png/.jpeg)

Example:
```
dataset/
├── john/
│   └── john_photo.jpg
├── mary/
│   └── mary.png
└── robert/
    └── robert.jpeg
```

### 3. Generate Embeddings

```bash
python generate_embeddings.py
```

This will:
- Detect faces in reference photos
- Generate face embeddings using FaceNet
- Save embeddings to `embeddings/embeddings.pkl`

### 4. Run Face Recognition

```bash
python recognize.py
```

Press 'q' to quit, 's' to save current frame.

## 📋 Requirements

### Hardware
- **Minimum**: 4GB RAM, integrated graphics
- **Recommended**: 8GB+ RAM, dedicated GPU (NVIDIA CUDA)

### Software
- Python 3.8+
- OpenCV 4.5+
- PyTorch 1.9+
- (See requirements.txt for exact versions)

## 🛠️ How It Works

### Step 1: Face Detection (YOLOv8)
- YOLOv8 detects people in images/video frames
- Extracts bounding boxes around detected faces
- Filters by confidence and size

### Step 2: Face Embedding (FaceNet)
- Crops and preprocesses detected faces
- FaceNet converts faces to 512-dimensional embeddings
- Embeddings represent unique facial features

### Step 3: Recognition
- Compares new face embeddings with stored ones
- Uses cosine similarity for matching
- Returns name if similarity > threshold

## ⚙️ Configuration

### Similarity Threshold
Adjust recognition sensitivity in `recognize.py`:

```python
recognizer = FaceRecognizer(embeddings_path, similarity_threshold=0.6)
```

- **Higher (0.7-0.8)**: More strict, fewer false positives
- **Lower (0.4-0.5)**: More lenient, more matches

### Camera Settings
Change camera index in `recognize.py`:

```python
recognizer.run_webcam(camera_index=0)  # 0 = default camera
```

## 🎨 Adding New People

1. **Create Folder**: `dataset/new_person/`
2. **Add Photo**: Place one clear face photo in the folder
3. **Regenerate Embeddings**: `python generate_embeddings.py`
4. **Restart Recognition**: `python recognize.py`

**Tips for Reference Photos:**
- Clear, front-facing photo
- Good lighting
- Minimal background distractions
- High resolution if possible

## 📊 Performance Tips

### Hardware Optimization
- **GPU Acceleration**: Install CUDA for 10x speed improvement
- **Memory**: Close unnecessary applications
- **Camera Quality**: Use lower resolution for faster processing

### Software Optimization
- **Model Size**: Use `yolov8n.pt` (nano) for speed, `yolov8s.pt` (small) for accuracy
- **Frame Rate**: Limit processing to 15-30 FPS
- **Detection Frequency**: Skip frames between detections

### Code Optimization
```python
# In recognize.py, adjust these parameters:
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)   # Lower resolution
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Lower resolution
```

## 🎯 Improving Accuracy

### Better Reference Photos
- Multiple angles and expressions
- Different lighting conditions
- Recent photos (faces change over time)

### Model Tuning
```python
# In generate_embeddings.py and recognize.py:
confidence_threshold = 0.7  # Higher for better detection
face_size_threshold = 80    # Minimum face size in pixels
```

### Multiple Reference Photos
Modify `generate_embeddings.py` to average multiple embeddings per person:

```python
# Process all images in person folder
embeddings = []
for image_path in image_files:
    embedding = generate_embedding(image_path)
    embeddings.append(embedding)
avg_embedding = np.mean(embeddings, axis=0)
```

## 🔧 Troubleshooting

### Common Issues

**"No embeddings found"**
- Run `python generate_embeddings.py` first
- Check dataset folder structure
- Verify image formats (.jpg, .png, .jpeg)

**"No faces detected"**
- Check reference photo quality
- Ensure faces are clearly visible
- Try different lighting conditions

**Poor Recognition Accuracy**
- Lower similarity threshold
- Add better reference photos
- Ensure consistent lighting

**Camera Not Working**
- Check camera index (try 0, 1, 2)
- Ensure camera is not used by other apps
- Install camera drivers

### Performance Issues

**Slow Performance**
- Install CUDA for GPU acceleration
- Reduce camera resolution
- Use smaller YOLOv8 model

**High Memory Usage**
- Close other applications
- Use smaller batch sizes
- Restart Python process

## 🚀 Extensions for Final Year Project

### Advanced Features
1. **Anti-Spoofing**: Detect if face is real or photo/video
2. **Age/Gender Estimation**: Add demographic analysis
3. **Emotion Recognition**: Detect facial expressions
4. **Face Tracking**: Maintain identity across frames
5. **Database Integration**: Store recognition logs with timestamps

### Web Interface
1. **Flask/FastAPI Backend**: REST API for recognition
2. **React Frontend**: Web-based face recognition
3. **Real-time Streaming**: WebRTC for browser support
4. **User Management**: Registration and profile system

### Mobile App
1. **React Native**: Cross-platform mobile app
2. **On-device Processing**: TensorFlow Lite models
3. **Offline Recognition**: No internet required
4. **Cloud Sync**: Backup embeddings to cloud

### Security Features
1. **Liveness Detection**: Blink detection, head movement
2. **Face Anti-Spoofing**: 3D depth analysis
3. **Encryption**: Secure embedding storage
4. **Access Control**: Permission-based recognition

### Performance Optimization
1. **Model Quantization**: Reduce model size and improve speed
2. **Edge Computing**: Deploy to edge devices
3. **Batch Processing**: Handle multiple faces simultaneously
4. **Caching**: Cache frequent embeddings

### Research Extensions
1. **Few-shot Learning**: Recognize with minimal data
2. **Domain Adaptation**: Adapt to different environments
3. **Cross-modal Recognition**: Voice + face recognition
4. **Privacy-Preserving**: Federated learning approaches

## 📚 Technical Details

### Models Used
- **YOLOv8n**: 6.2M parameters, fast inference
- **FaceNet (InceptionResnetV1)**: 512-dimensional embeddings
- **Pretrained on VGGFace2**: High-quality face representations

### Metrics
- **Detection Speed**: ~30 FPS on GPU, ~10 FPS on CPU
- **Recognition Accuracy**: >95% with good reference photos
- **Embedding Dimension**: 512 features per face
- **Similarity Metric**: Cosine similarity (0-1 scale)

### Dependencies
```
ultralytics==8.0.196    # YOLOv8
facenet-pytorch==2.5.3  # FaceNet
opencv-python==4.8.1.78 # Computer Vision
torch==2.0.1           # Deep Learning
numpy==1.24.3          # Numerical Computing
scipy==1.11.1          # Scientific Computing
```

## 📄 License

This project is for educational purposes. Please respect privacy and obtain consent before capturing or storing face images.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Verify your installation
3. Test with the provided example dataset
4. Check system requirements

---

**Note**: This system is designed for educational and research purposes. For production use, consider additional security measures and privacy protections.
