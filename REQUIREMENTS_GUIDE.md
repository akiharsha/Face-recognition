# 📦 Requirements Guide for Different Platforms

## 🎯 **Which Requirements File to Use**

### **For Render.com Deployment:**
```bash
pip install -r requirements-render.txt
```
**Why:** Uses Render-compatible PyTorch 2.1.2

### **For Vercel Deployment:**
```bash
pip install -r requirements-vercel.txt
```
**Why:** CPU-only packages for serverless

### **For Local Development (Latest):**
```bash
pip install -r requirements-latest.txt
```
**Why:** Newest stable versions

### **For Local Development (Stable):**
```bash
pip install -r requirements.txt
```
**Why:** Proven stable versions

### **For Python 3.12+ Specific:**
```bash
pip install -r requirements-py312.txt
```
**Why:** Python 3.12+ optimized

## 🏗️ **Platform-Specific Requirements**

### **Render.com Issues:**
- ❌ `torch==2.4.0` not available
- ✅ `torch==2.1.2` works
- ✅ Use older stable versions

### **Vercel Issues:**
- ❌ GPU packages not supported
- ✅ Use `torch==2.1.2+cpu`
- ✅ Use `opencv-python-headless`

### **Local Development:**
- ✅ Any version works
- ✅ Use latest for best features

## 📋 **Version Compatibility Matrix**

| Platform | PyTorch | Ultralytics | Flask | Python |
|----------|-----------|-------------|---------|---------|
| Render | 2.1.2 | 8.0.196 | 2.3.3 | 3.8-3.11 |
| Vercel | 2.1.2+cpu | 8.0.196 | 2.3.3 | 3.8-3.11 |
| Local Latest | 2.11.0 | 8.3.0 | 3.0.3 | 3.8-3.12 |
| Local Stable | 2.1.2 | 8.0.196 | 2.3.3 | 3.8-3.11 |

## 🚀 **Quick Deployment Commands**

### **Render Deployment:**
```bash
# In Render dashboard, set:
# Build Command: pip install -r requirements-render.txt
# Python Version: 3.11
```

### **Vercel Deployment:**
```bash
# In Vercel dashboard, set:
# Install Command: pip install -r requirements-vercel.txt
# Python Version: 3.11
```

### **Local Development:**
```bash
# For latest features:
pip install -r requirements-latest.txt

# For stability:
pip install -r requirements.txt
```

## 🔧 **Troubleshooting**

### **Common Errors:**
1. **"No matching distribution found"** → Use platform-specific requirements
2. **"Requires different python version"** → Check Python version compatibility
3. **"Build failed"** → Use older stable versions

### **Solutions:**
1. **Render:** Use `requirements-render.txt`
2. **Vercel:** Use `requirements-vercel.txt`
3. **Local:** Use `requirements-latest.txt`

## 📝 **File Descriptions**

- `requirements.txt` - Stable, proven versions
- `requirements-render.txt` - Render.com compatible
- `requirements-vercel.txt` - Vercel serverless optimized
- `requirements-py312.txt` - Python 3.12+ specific
- `requirements-latest.txt` - Latest stable versions
