# 🚀 Vercel Deployment Guide

## 📋 **Vercel Configuration Settings**

### **1. Build Settings**
```json
// vercel.json
{
  "version": 2,
  "name": "face-recognition",
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ],
  "env": {
    "FLASK_ENV": "production",
    "PYTHON_VERSION": "3.9"
  }
}
```

### **2. Runtime Settings**
- **Runtime**: Python 3.9
- **Framework**: Flask (serverless)
- **Build Command**: `pip install -r requirements-vercel.txt`
- **Output Directory**: Root (no build output)
- **Function Timeout**: 10 seconds (Vercel limit)

## 🔧 **Key Settings for Vercel**

### **Build Configuration**
```json
{
  "installCommand": "pip install -r requirements-vercel.txt",
  "buildCommand": "echo 'Build complete'",
  "outputDirectory": "",
  "framework": null
}
```

### **Environment Variables**
```bash
# Required Environment Variables
FLASK_ENV=production
PYTHON_VERSION=3.9
SECRET_KEY=your-vercel-secret-key

# Optional (for performance)
VERCEL_PYTHON_VERSION=3.9
VERCEL_REGION=us-east-1
```

## 📁 **File Structure for Vercel**

```
face-recognition/
├── api/
│   └── index.py              # Serverless function
├── embeddings/
│   └── embeddings.pkl         # Pre-generated embeddings
├── yolov8n.pt                # YOLO model (auto-download)
├── vercel.json               # Vercel config
├── requirements-vercel.txt     # Serverless dependencies
└── VERCEL_DEPLOYMENT.md      # This guide
```

## 🚀 **Deployment Steps**

### **1. Prepare for Vercel**
```bash
# 1. Pre-generate embeddings locally
python generate_embeddings.py

# 2. Copy embeddings to project
cp embeddings/embeddings.pkl ./

# 3. Install Vercel CLI
npm i -g vercel

# 4. Login to Vercel
vercel login
```

### **2. Deploy to Vercel**
```bash
# Deploy from project root
cd "C:\GitHub\Face recognition"
vercel --prod

# Follow prompts:
# ? Set up and deploy "~/GitHub/Face recognition"? [Y/n]
# ? Which scope do you want to deploy to? Your Name
# ? Link to existing project? [y/N]
# ? What's your project's name? face-recognition
```

### **3. Deployment Output**
```bash
✅ Production: https://face-recognition-your-username.vercel.app
✅ Inspect: https://vercel.com/your-username/face-recognition
✅ Logs: https://vercel.com/your-username/face-recognition/_logs
```

## ⚙️ **Vercel Dashboard Settings**

### **Build & Development Settings**
```
Framework Preset: Other
Root Directory: ./
Build Command: pip install -r requirements-vercel.txt
Output Directory: ./
Install Command: pip install -r requirements-vercel.txt
Python Version: 3.9
Node Version: 18.x
```

### **Environment Variables**
```
FLASK_ENV = production
PYTHON_VERSION = 3.9
SECRET_KEY = your-secret-key-here
```

### **Domains**
```
Primary Domain: face-recognition-your-username.vercel.app
Custom Domains: your-domain.com (if configured)
```

## 🔧 **Serverless Optimizations**

### **Model Loading Strategy**
```python
# Load models once per function invocation
global yolo_model, facenet_model, device

def load_models():
    global yolo_model, facenet_model, device
    if yolo_model is None:
        # Load models only on first request
        yolo_model = YOLO('yolov8n.pt')
        facenet_model = InceptionResnetV1(pretrained='vggface2').eval()
        device = torch.device('cpu')  # Force CPU for serverless
        facenet_model = facenet_model.to(device)
```

### **Memory Management**
```python
# Optimize for serverless constraints
torch.set_num_threads(1)  # Single thread
torch.backends.cudnn.enabled = False  # Disable CUDA
cv2.setNumThreads(1)  # Single thread
```

### **File Handling**
```python
# Use temporary files for uploads
import tempfile
import base64

def process_image(file_data):
    with tempfile.NamedTemporaryFile() as temp_file:
        temp_file.write(file_data)
        # Process image
        return result
```

## 📊 **Vercel Limits & Constraints**

### **Function Limits**
- **Execution Timeout**: 10 seconds max
- **Memory**: 1GB max
- **File Size**: 50MB max upload
- **Request Size**: 4.5MB max
- **Concurrent Executions**: 1000 per region

### **Build Limits**
- **Build Time**: 5 minutes max
- **Build Memory**: 3GB max
- **Dependencies**: 500MB max
- **Output Size**: 100MB max

## 🌐 **API Endpoints on Vercel**

### **Available Endpoints**
```
GET  /                    # Main web interface
POST /api/recognize     # Face recognition
GET  /api/people         # List people
GET  /health             # Health check
```

### **Request Format**
```bash
# Recognition Request
curl -X POST \
  -F "file=@image.jpg" \
  https://face-recognition-your-username.vercel.app/api/recognize

# People List Request
curl https://face-recognition-your-username.vercel.app/api/people

# Health Check
curl https://face-recognition-your-username.vercel.app/health
```

## 🔍 **Testing Vercel Deployment**

### **Local Testing**
```bash
# Test serverless function locally
vercel dev

# Output:
# > Ready! Available at http://localhost:3000
```

### **Production Testing**
```bash
# Test deployed app
curl https://face-recognition-your-username.vercel.app/health

# Expected response:
{
  "status": "healthy",
  "models_loaded": true,
  "embeddings_count": 42,
  "platform": "vercel-serverless"
}
```

## 🚨 **Common Vercel Issues**

### **Build Failures**
```bash
# Issue: Model download timeout
# Solution: Pre-download models
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt

# Issue: Dependencies too large
# Solution: Use CPU-only versions
pip install torch==2.0.1+cpu torchvision==0.15.2+cpu
```

### **Runtime Errors**
```bash
# Issue: Function timeout
# Solution: Optimize processing
# - Reduce image size
# - Use smaller models
# - Implement early exit

# Issue: Memory exceeded
# Solution: Reduce memory usage
# - Use torch.no_grad()
# - Clear intermediate variables
# - Use CPU instead of GPU
```

### **Performance Issues**
```bash
# Issue: Cold start delays
# Solution: Keep functions warm
# - Use cron jobs for periodic requests
# - Implement edge caching
# - Optimize import loading
```

## 📈 **Monitoring on Vercel**

### **Vercel Analytics**
- **Function Invocations**: Request count
- **Errors**: Error rate and types
- **Duration**: Average response time
- **Memory**: Peak usage per function

### **Custom Monitoring**
```python
@app.route('/metrics')
def metrics():
    return jsonify({
        'platform': 'vercel-serverless',
        'timestamp': time.time(),
        'version': '1.0.0',
        'models_loaded': bool(yolo_model and facenet_model)
    })
```

## 🎯 **Best Practices for Vercel**

### **1. Optimize Cold Starts**
```python
# Minimize import time
import lazy_imports  # Import models only when needed

# Use global variables
global models_cache
models_cache = {}  # Cache between invocations
```

### **2. Handle Timeouts**
```python
# Implement timeout handling
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Function timeout")

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(8)  # 8 second timeout
```

### **3. Optimize Dependencies**
```txt
# requirements-vercel.txt
torch==2.0.1+cpu              # CPU-only version
torchvision==0.15.2+cpu         # CPU-only version
opencv-python-headless==4.8.1.78   # No GUI dependencies
```

## 🔄 **CI/CD for Vercel**

### **GitHub Actions**
```yaml
# .github/workflows/vercel.yml
name: Deploy to Vercel

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
```

## 🎉 **Deployment Verification**

After deployment, verify:
- [ ] Web interface loads at your-domain.vercel.app
- [ ] Face recognition works with test images
- [ ] API endpoints return correct responses
- [ ] Health check shows "healthy" status
- [ ] Functions complete within 10-second timeout
- [ ] Memory usage stays below 1GB

**Your face recognition system is now ready for Vercel deployment!** 🚀
