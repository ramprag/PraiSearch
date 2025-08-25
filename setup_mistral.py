#!/usr/bin/env python3
"""
QUICK LIGHTWEIGHT SETUP - Only essential packages
Total install size: ~500MB instead of 10GB+
"""

import subprocess
import sys
import os

def run_cmd(cmd):
    """Run command with real-time output"""
    print(f"🔧 {cmd}")
    result = subprocess.run(cmd.split(), capture_output=False)
    return result.returncode == 0

def main():
    print("⚡ LIGHTWEIGHT SafeQuery Setup")
    print("📦 Installing only essential packages (~500MB total)")
    print("=" * 50)

    # Create minimal requirements
    minimal_reqs = [
        "fastapi==0.111.0",
        "uvicorn[standard]==0.29.0",
        "pydantic==2.5.0",
        "chromadb==0.4.24",
        "sentence-transformers==2.7.0",
        "ollama==0.1.7",
        "newspaper3k==0.2.8",
        "beautifulsoup4==4.12.2",
        "requests==2.32.3",
        "feedparser==6.0.11",
        "apscheduler==3.10.4",
        "cryptography==42.0.8",
        "python-dotenv==1.0.0",
        "numpy==1.26.4"
    ]

    print("📦 Installing packages one by one...")
    failed = []

    for package in minimal_reqs:
        print(f"\n📦 Installing {package.split('==')[0]}...")
        if not run_cmd(f"pip install {package}"):
            failed.append(package)
            print(f"❌ Failed: {package}")
        else:
            print(f"✅ Success: {package}")

    if failed:
        print(f"\n⚠️ Failed packages: {failed}")
        print("Try installing them manually")
    else:
        print("\n🎉 All packages installed successfully!")

    # Create directories
    for dir_name in ["chroma_db", "logs"]:
        os.makedirs(dir_name, exist_ok=True)
        print(f"📁 Created: {dir_name}")

    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh")
    print("2. Download Mistral: ollama pull mistral:7b")
    print("3. Start server: python -m uvicorn main:app --reload --port 8000")

if __name__ == "__main__":
    main()