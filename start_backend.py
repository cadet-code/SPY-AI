#!/usr/bin/env python3
"""
Spa AI Automation System - Backend Startup Script
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        sys.exit(1)

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Creating .env file...")
        env_content = """# API Keys
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
RESEND_API_KEY=your_resend_api_key_here

# Spa Configuration
SPA_MANAGER_EMAIL=manager@yourspa.com
SPA_NAME=Luxury Spa & Wellness
SPA_ADDRESS=123 Wellness Street, City, State 12345
SPA_PHONE=+1 (555) 123-4567

# Google Services
GOOGLE_CALENDAR_ID=primary
GOOGLE_SHEETS_ID=your_google_sheets_id_here

# Database
DATABASE_URL=sqlite:///./spa_automation.db

# AI Configuration
AI_MODEL=gpt-3.5-turbo
MAX_TOKENS=1000

# Appointment Settings
APPOINTMENT_DURATION=60
BUFFER_TIME=15
"""
        with open(env_file, "w") as f:
            f.write(env_content)
        print("✅ .env file created")
        print("⚠️  Please update the .env file with your API keys before running the application")
    else:
        print("✅ .env file already exists")

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting Spa AI Automation System...")
    try:
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

def main():
    """Main startup function"""
    print("=" * 50)
    print("🌟 Spa AI Automation System")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Install dependencies
    install_dependencies()
    
    # Create .env file
    create_env_file()
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()
