#!/usr/bin/env python3
"""
Production Startup Script for Face Recognition System
============================================

Use this script for production deployment instead of app.py
"""

import os
import sys

def check_requirements():
    """Check if all required files exist"""
    required_files = [
        'app.py',
        'requirements.txt',
        'templates/index.html',
        'static/css/style.css',
        'static/js/app.js'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All required files present")
    return True

def check_directories():
    """Check if required directories exist"""
    required_dirs = ['dataset', 'embeddings', 'static', 'templates']
    
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            print(f"📁 Creating directory: {dir_name}")
            os.makedirs(dir_name, exist_ok=True)

def main():
    """Main production startup"""
    print("🚀 Starting Face Recognition System (Production Mode)")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Create directories
    check_directories()
    
    # Import and run app
    from app import app, load_models, load_embeddings
    
    # Initialize models
    print("🔧 Loading models...")
    load_models()
    load_embeddings()
    
    # Production configuration
    print("🌐 Starting production server...")
    print("📍 Server: http://127.0.0.1:5000")
    print("🔒 Debug mode: DISABLED")
    print("⚠️  Press Ctrl+C to stop server")
    
    try:
        app.run(
            debug=False,
            host='127.0.0.1',
            port=5000,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
