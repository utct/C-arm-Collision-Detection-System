"""
Launch All Components - C-arm Simulation System
Starts collision server, DRR server, and optionally visualizer
"""

import subprocess
import sys
import time
from pathlib import Path
import argparse

def main():
    parser = argparse.ArgumentParser(description='Launch C-arm simulation components')
    parser.add_argument('--no-drr', action='store_true', 
                        help='Skip DRR server (faster startup)')
    parser.add_argument('--visualizer', action='store_true', 
                        help='Include collision visualizer (default: off)')
    args = parser.parse_args()
    
    print("=" * 70)
    print("LAUNCHING C-ARM SIMULATION SYSTEM")
    print("=" * 70)
    
    script_dir = Path(__file__).parent
    venv_python = script_dir / ".venv" / "Scripts" / "python.exe"
    venv_gpu_python = script_dir / ".venv_gpu" / "Scripts" / "python.exe"
    
    if not venv_python.exists():
        print("\n[ERROR] Virtual environment not found")
        print(f"Expected: {venv_python}")
        sys.exit(1)
    
    has_gpu_venv = venv_gpu_python.exists()
    if not has_gpu_venv:
        print("\n[WARNING] GPU virtual environment not found at .venv_gpu/")
        print("          DRR server will use CPU mode (~4s per frame)")
        print("          For real-time: create .venv_gpu with Python 3.11 + CUDA")
    
    processes = []
    total_steps = 1 + (0 if args.no_drr else 1) + (1 if args.visualizer else 0)
    
    try:
        print("\n[1/{}] Starting collision detection server...".format(total_steps))
        server_process = subprocess.Popen(
            [str(venv_python), "collision_server.py"],
            cwd=str(script_dir)
        )
        processes.append(("Collision Server", server_process))
        print("        [OK] Collision server started")
        time.sleep(2)
        
        step = 1
        if not args.no_drr:
            step += 1
            drr_python = venv_gpu_python if has_gpu_venv else venv_python
            mode = "GPU" if has_gpu_venv else "CPU"
            
            print("\n[{}/{}] Starting DRR server ({} mode)...".format(step, total_steps, mode))
            drr_process = subprocess.Popen(
                [str(drr_python), "drr_server.py"],
                cwd=str(script_dir)
            )
            processes.append(("DRR Server", drr_process))
            print("        [OK] DRR server started")
            if has_gpu_venv:
                print("        [GPU] Real-time rendering (~100ms per frame)")
            else:
                print("        [WARNING] CPU mode (~4s per frame)")
            time.sleep(5)
        
        if args.visualizer:
            step += 1
            print("\n[{}/{}] Starting collision visualizer...".format(step, total_steps))
            visualizer_process = subprocess.Popen(
                [str(venv_python), "collision_visualizer.py"],
                cwd=str(script_dir)
            )
            processes.append(("Collision Visualizer", visualizer_process))
            print("        [OK] Visualizer started")
            time.sleep(2)
        
        print("\n" + "=" * 70)
        print("ALL COMPONENTS RUNNING")
        print("=" * 70)
        print("\nNow launch H3D separately:")
        print("  .venv\\Scripts\\Activate.ps1")
        print("  python launch_h3d.py")
        print("\nIn H3D:")
        print("  - Click 'DRR Mode: OFF' button to enable photorealistic X-rays")
        if has_gpu_venv and not args.no_drr:
            print("  - Move C-arm sliders → DRR updates in REAL-TIME! (~100ms)")
        elif not args.no_drr:
            print("  - Move C-arm sliders → DRR updates slowly (~4s delay)")
        print("\nPress Ctrl+C to stop all servers")
        print("=" * 70)
        
        # Wait for processes to exit
        while True:
            time.sleep(1)
            # Check if any process has terminated
            for name, process in processes:
                if process.poll() is not None:
                    print(f"\n{name} has stopped. Shutting down other components...")
                    raise KeyboardInterrupt
        
    except KeyboardInterrupt:
        print("\n\nShutting down all components...")
    
    except Exception as e:
        print(f"\n[ERROR] {e}")
    
    finally:
        # Clean up all processes
        for name, process in processes:
            if process.poll() is None:  # Process still running
                print(f"Terminating {name}...")
                process.terminate()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()
        
        print("\nAll components stopped.")
        print("=" * 70)

if __name__ == '__main__':
    main()
