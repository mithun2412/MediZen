# run_instances.py (UPDATED)
import subprocess
import time
import os
import signal
import sys
import threading

def run_instance(port):
    """Run a single FastAPI instance on a specific port"""
    
    # Set environment variables for this instance
    env = os.environ.copy()
    env["PORT"] = str(port)
    
    # If using SQLite, use separate database files
    if os.getenv("DATABASE_URL", "").startswith("sqlite"):
        env["DATABASE_URL"] = f"sqlite:///./medivoice_{port}.db"
    
    # Command to run
    cmd = [
        sys.executable, "-m", "uvicorn",
        "app.main:app",
        "--host", "0.0.0.0",
        "--port", str(port),
        "--workers", "1",
        "--log-level", "warning",  # Reduce noise
    ]
    
    # Start process
    process = subprocess.Popen(
        cmd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    return process

def run_multiple_instances():
    """Run 3 FastAPI instances on ports 8001, 8002, 8003"""
    
    ports = [8001, 8002, 8003]
    processes = {}
    
    print("🚀 Starting 3 FastAPI instances...")
    print("📝 Using separate databases for each instance\n")
    
    for port in ports:
        process = run_instance(port)
        processes[port] = process
        print(f"✅ Instance started on port {port} (PID: {process.pid})")
        time.sleep(2)  # Give each instance time to start
    
    print("\n📊 All instances running:")
    for port in ports:
        print(f"   Instance {port}: http://localhost:{port}")
    print("\n🌐 Test each instance:")
    print(f"   curl http://localhost:8001/health")
    print(f"   curl http://localhost:8002/health")
    print(f"   curl http://localhost:8003/health")
    print("\nPress Ctrl+C to stop all instances...")
    
    try:
        # Monitor processes
        while True:
            for port, process in list(processes.items()):
                if process.poll() is not None:
                    # Process died
                    print(f"⚠️ Instance on port {port} died. Restarting...")
                    
                    # Check if it was an error
                    stdout, stderr = process.communicate()
                    if stderr:
                        print(f"   Error: {stderr[:200]}...")
                    
                    # Restart
                    new_process = run_instance(port)
                    processes[port] = new_process
                    print(f"✅ Restarted instance on port {port}")
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping all instances...")
        for process in processes.values():
            process.terminate()
            process.wait()
        print("✅ All instances stopped")

if __name__ == "__main__":
    run_multiple_instances()