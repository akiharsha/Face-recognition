# Quick Setup Guide

## 🚀 5-Minute Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Add Reference Photos
Place one photo per person in dataset folders:
```
dataset/
├── john/
│   └── john.jpg
├── mary/
│   └── mary.jpg
```

### 3. Generate Embeddings
```bash
python generate_embeddings.py
```

### 4. Run Recognition
```bash
python recognize.py
```

## 📸 Example Usage

1. **Add your photo**: `dataset/your_name/your_photo.jpg`
2. **Run generator**: `python generate_embeddings.py`
3. **Start webcam**: `python recognize.py`
4. **Test**: Show your face to the camera

## 🔧 Troubleshooting

**No camera?** Try different camera index: `recognizer.run_webcam(camera_index=1)`

**Poor detection?** Add better reference photo with clear lighting

**Slow performance?** Install CUDA or reduce camera resolution
