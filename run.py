import subprocess
import sys
import time
import os

# Get current folder path
current_dir = os.path.dirname(os.path.abspath(__file__))

print("===================================================")
print("🚀 Starting Okay Bot AI Number System Converter...")
print("===================================================")

# 1. Start Backend API server in background
print("[1/2] Launching Backend Server on Port 8000...")
backend_path = os.path.join(current_dir, "backend.py")
backend_process = subprocess.Popen([sys.executable, backend_path])

# 2. Wait 2 seconds for backend to initialize
time.sleep(2)

# 3. Start Streamlit Frontend
print("[2/2] Launching Streamlit Frontend...")
app_path = os.path.join(current_dir, "app.py")
try:
    subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])
finally:
    # Cleanup backend on close
    backend_process.terminate()
