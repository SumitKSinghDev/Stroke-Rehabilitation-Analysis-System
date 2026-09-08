import subprocess
import sys
import time
import os
import signal

def run():
    print("==================================================================")
    print("  RehabShield: Gait & Upper Limb Impairment Stroke Rehab System   ")
    print("==================================================================")

    # 1. Start FastAPI Backend
    print("\n[+] Starting FastAPI backend on http://localhost:8080 ...")
    backend_cmd = [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
    backend_process = subprocess.Popen(
        backend_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    # 2. Wait for backend to initialize
    time.sleep(2)

    # 3. Start React Frontend
    print("[+] Starting Vite React frontend on http://localhost:5173 ...")
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
    # Use cmd /c on Windows to bypass powershell execution restriction
    frontend_cmd = ["cmd", "/c", "npm run dev"]
    frontend_process = subprocess.Popen(
        frontend_cmd,
        cwd=frontend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    # Function to stream process outputs
    import threading
    def stream_output(process, name):
        for line in iter(process.stdout.readline, ''):
            print(f"[{name}] {line.strip()}")
        process.stdout.close()

    t1 = threading.Thread(target=stream_output, args=(backend_process, "Backend"), daemon=True)
    t2 = threading.Thread(target=stream_output, args=(frontend_process, "Frontend"), daemon=True)
    
    t1.start()
    t2.start()

    print("\n[OK] Both services are running.")
    print("    - API Docs: http://localhost:8080/docs")
    print("    - Web Client: http://localhost:5173")
    print("\nPress Ctrl+C to terminate both servers.")

    try:
        while True:
            time.sleep(1)
            # Check if any process terminated unexpectedly
            if backend_process.poll() is not None:
                print("[-] Backend process terminated unexpectedly.")
                break
            if frontend_process.poll() is not None:
                print("[-] Frontend process terminated unexpectedly.")
                break
    except KeyboardInterrupt:
        print("\n[-] Interrupt received. Shutting down services...")
    finally:
        # Terminate processes
        try:
            if os.name == 'nt':
                # On Windows, taskkill is more reliable for tree termination
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(backend_process.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(frontend_process.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                backend_process.terminate()
                frontend_process.terminate()
        except Exception:
            pass
        print("[OK] All services stopped successfully.")

if __name__ == "__main__":
    run()
