#!/usr/bin/env python3
"""
QUICK LIGHTWEIGHT SETUP - Installs essential packages from requirements.txt and guides the user.
"""

import subprocess
import sys
import os
import platform

def run_cmd(cmd):
    """Run command with real-time output"""
    print(f"🔧 {cmd}")
    # Use shell=True for commands like 'pip install -r ...' which might have complex args
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8')
    for line in process.stdout:
        print(line, end='')
    process.wait()
    return process.returncode == 0

def main():
    print("⚡ LIGHTWEIGHT SafeQuery Setup")
    print("📦 Installing essential packages from backend/requirements.txt")
    print("=" * 50)

    # Install dependencies from requirements.txt located in the backend folder
    req_file = os.path.join("backend", "requirements.txt")
    if not os.path.exists(req_file):
        print(f"❌ Error: '{req_file}' not found. Please ensure it's in the 'backend' directory.")
        sys.exit(1)

    if not run_cmd(f'"{sys.executable}" -m pip install -r {req_file}'):
        print("\n⚠️ An error occurred during package installation. Please check the logs above.")
        sys.exit(1)
    else:
        print("\n🎉 All packages installed successfully!")

    # Create directories inside the backend folder
    for dir_name in [os.path.join("backend", "chroma_db"), os.path.join("backend", "logs")]:
        os.makedirs(dir_name, exist_ok=True)
        print(f"📁 Created: {dir_name}")

    print("\n✅ Setup complete!")
    print("\nNext steps:")

    if platform.system() in ["Linux", "Darwin"]:  # Darwin is macOS
        print("1. Install Ollama (if not installed): curl -fsSL https://ollama.ai/install.sh | sh")
    else:  # Windows
        print("1. Install Ollama: If you haven't, download and run the Windows installer from ollama.ai.")

    print("\n👉 For systems with limited RAM (< 8GB), use a smaller model:")
    print("2. Download a Model: ollama pull gemma:2b (recommended) OR ollama pull mistral:7b")
    print("3. Start server: In your project's 'backend' directory, run -> uvicorn main:app --reload --port 8000")

if __name__ == "__main__":
    main()