# run_simple.py
import subprocess
import time
import sys
import os

def run_simple_instances():
    """Simple runner that runs instances in separate windows"""
    
    ports = [8001, 8002, 8003]
    
    print("🚀 Opening 3 terminal windows with FastAPI instances...")
    
    for port in ports:
        # Open a new terminal window for each instance
        if sys.platform == "win32":
            # Windows
            cmd = f'start "MediZen Port {port}" cmd /c "set PORT={port} && python -m uvicorn app.main:app --host 0.0.0.0 --port {port} --workers 1"'
            subprocess.Popen(cmd, shell=True)
        else:
            # Linux/Mac
            cmd = f'xterm -e "PORT={port} python -m uvicorn app.main:app --host 0.0.0.0 --port {port} --workers 1"'
            subprocess.Popen(cmd, shell=True)
        
        time.sleep(1)
        print(f"✅ Instance started on port {port}")
    
    print("\n📊 All instances running in separate windows!")
    print("   Close each window to stop the instance")

if __name__ == "__main__":
    run_simple_instances()