# 🚀 Deployment Guide

## 📋 Deployment Checklist

### ✅ **READY FOR DEPLOYMENT**
- [x] All core files present
- [x] Dependencies defined in requirements.txt
- [x] Production startup script created
- [x] Security configurations applied
- [x] Error handling implemented

## 🛠️ **Deployment Options**

### **Option 1: Local Development**
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py
```

### **Option 2: Production Mode**
```bash
# Install dependencies
pip install -r requirements.txt

# Run production server
python start_production.py
```

### **Option 3: Docker Deployment**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p dataset embeddings

# Expose port
EXPOSE 5000

# Run production server
CMD ["python", "start_production.py"]
```

### **Option 4: Cloud Deployment (Heroku)**
```bash
# Create Procfile
echo "web: python start_production.py" > Procfile

# Deploy to Heroku
heroku create your-app-name
git push heroku main
```

## 🔧 **Environment Variables**

### **Required for Production**
```bash
# Set these environment variables
export FLASK_ENV=production
export SECRET_KEY=your-secret-key-here
export MAX_CONTENT_LENGTH=16777216  # 16MB
```

### **Optional**
```bash
export CUDA_VISIBLE_DEVICES=0  # GPU support
export EMBEDDINGS_PATH=/app/embeddings
export DATASET_PATH=/app/dataset
```

## 📁 **File Structure for Deployment**

```
face-recognition/
├── app.py                    # Main Flask app
├── start_production.py       # Production startup
├── requirements.txt          # Dependencies
├── templates/
│   └── index.html         # Frontend
├── static/
│   ├── css/style.css      # Styling
│   └── js/app.js         # Frontend logic
├── dataset/                # User photos (create empty)
├── embeddings/             # Face embeddings (create empty)
└── yolov8n.pt            # YOLO model (auto-download)
```

## 🔒 **Security Considerations**

### **File Upload Security**
- ✅ File type validation (images only)
- ✅ File size limits (16MB max)
- ✅ Secure filename handling
- ✅ Input sanitization

### **API Security**
- ✅ CORS configuration
- ✅ Request validation
- ✅ Error message sanitization

### **Production Security**
- ✅ Debug mode disabled
- ✅ Host binding to localhost
- ✅ Environment variables for secrets

## 🚀 **Production Server Setup**

### **Using Gunicorn (Recommended)**
```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn --bind 127.0.0.1:5000 --workers 4 app:app
```

### **Using Nginx + Gunicorn**
```nginx
# /etc/nginx/sites-available/face-recognition
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /path/to/face-recognition/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## 📊 **Performance Optimization**

### **For High Traffic**
```bash
# Increase workers
gunicorn --workers 8 --bind 127.0.0.1:5000 app:app

# Enable caching
export FLASK_CACHE_TYPE=redis
export REDIS_URL=redis://localhost:6379/0
```

### **For Large Datasets**
```bash
# Use GPU acceleration
export CUDA_VISIBLE_DEVICES=0

# Optimize memory
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128
```

## 🔍 **Testing Before Deployment**

### **1. Local Testing**
```bash
# Test all features
python -m pytest tests/

# Test manually
python start_production.py
# Open http://127.0.0.1:5000
# Test upload, recognition, management
```

### **2. Load Testing**
```bash
# Install Apache Bench
ab -n 1000 -c 10 http://127.0.0.1:5000/api/people
```

## 🚨 **Common Deployment Issues**

### **Port Already in Use**
```bash
# Find process using port 5000
netstat -tulpn | grep :5000

# Kill process
kill -9 <PID>
```

### **Model Download Fails**
```bash
# Download YOLO model manually
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
```

### **Permission Denied**
```bash
# Fix file permissions
chmod +x start_production.py
chmod -R 755 static/
chmod -R 755 templates/
```

## 📈 **Monitoring**

### **Health Check Endpoint**
```python
# Add to app.py
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'models_loaded': bool(yolo_model and facenet_model),
        'timestamp': time.time()
    })
```

### **Logging**
```python
# Add logging configuration
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

## 🎯 **Deployment Commands**

### **Quick Deploy**
```bash
# 1. Clone/copy project
# 2. Install dependencies
pip install -r requirements.txt

# 3. Create directories
mkdir -p dataset embeddings

# 4. Run production server
python start_production.py

# 5. Test in browser
# http://127.0.0.1:5000
```

### **Full Production Deploy**
```bash
# 1. Set environment
export FLASK_ENV=production

# 2. Install with production server
pip install -r requirements.txt gunicorn

# 3. Run with Gunicorn
gunicorn --bind 127.0.0.1:5000 --workers 4 app:app

# 4. Setup reverse proxy (Nginx/Apache)
# 5. Configure SSL certificate
# 6. Monitor performance
```

## ✅ **Deployment Verification**

After deployment, verify:
- [ ] Server starts without errors
- [ ] All pages load correctly
- [ ] File upload works
- [ ] Webcam recognition functions
- [ ] Person management works
- [ ] No console errors
- [ ] Mobile responsive
- [ ] Performance acceptable

**Your project is now ready for production deployment!** 🎉
