# Control Software for Image-Guided C-Arm and Patient Table Systems

Honours Project - Interactive Medical Imaging Simulation System

## Screenshots

### Main System Interface
![Main H3D GUI](document/screenshots/Screenshot%202025-12-18%20164556.png)
*H3D GUI showing C-arm control, patient table positioning, collision detection, and real-time X-ray rendering with anatomical segmentation*

### 3D Collision Visualizer
![Collision Visualizer](document/screenshots/Screenshot%202025-12-18%20164438.png)
*Real-time 3D visualization of C-arm (cyan), patient table (orange/red/gray), and patient model (beige) for collision detection debugging*

## Overview

This project implements a real-time simulation system for an image-guided C-arm and patient table with collision detection and photorealistic X-ray rendering. The system features 9 degrees of freedom (6 for C-arm, 3 for patient table) with GPU-accelerated DRR (Digitally Reconstructed Radiograph) generation and anatomical segmentation overlay.

### Key Features

- **9 DOF Control System**
  - C-arm: 6 DOF (Orbital/LAO-RAO, Tilt/CRAN-CAUD, Wigwag, Lateral, Vertical, Horizontal)
  - Patient Table: 3 DOF (Vertical, Longitudinal, Transverse)

- **Real-time Collision Detection**
  - Point cloud + mesh intersection algorithm (research paper method)
  - Detects collisions between C-arm, table, and patient
  - Visual feedback with green (safe) / red (collision) indicators

- **Photorealistic X-ray Rendering**
  - GPU-accelerated DRR generation using DiffDRR (~100ms per frame with CUDA)
  - CPU fallback mode available (~4s per frame)
  - Colored anatomical segmentation overlay (TotalSegmentator v2 labels)
  - Real-time updates as C-arm moves

- **Workspace Analysis**
  - Statistical reachability analysis for surgical planning
  - Monte Carlo random sampling (5,000-100,000+ poses)
  - Identify collision-free workspace for clinical interventions
  - Generate publication-quality results

- **Architecture**
  - H3D GUI (Python 2.7) for 3D visualization
  - Python 3 servers for collision detection and DRR rendering
  - File-based IPC using JSON for pose communication

## System Requirements

### Required
- Python 2.7 (for H3D)
- Python 3.11+ (for servers)
- H3D API installed
- Windows OS

### Python 3 Dependencies
```
numpy
vedo
torch
diffdrr
pillow
scipy
nibabel
pynrrd
```

### Highly Recommended (for Real-time Performance)
- **NVIDIA GPU with CUDA support** (GTX 1060 or better)
- **CUDA Toolkit** (11.8 or later)
- **PyTorch with CUDA** (provides ~40x speedup for DRR rendering)
- Without GPU: DRR renders at 0.25 fps (4s per frame)
- With GPU: DRR renders at ~10 fps (100ms per frame)

## Project Structure

```
backup/
├── main.x3d                         # Main H3D GUI file
├── collision_server.py              # Collision detection server (Python 3)
├── drr_server.py                    # DRR rendering server (Python 3)
├── collision_visualizer.py          # 3D collision visualization tool
├── collision_demo.py                # Interactive collision testing tool
├── workspace_analysis.py            # Surgical workspace analysis tool
├── workspace_visualizer.py          # Workspace results visualization
├── launch_all.py                    # Launch script for servers
├── launch_h3d.py                    # H3D launcher
├── lib/
│   ├── CollisionClient.py           # Collision client (Python 2.7, runs in H3D)
│   ├── TransformationMats.py        # DH transformation matrices
│   ├── CarmModelMovement.py         # C-arm movement controller
│   ├── PatientTableMovementSimple.py # Table movement controller
│   ├── DRRModeController.py         # DRR mode toggle
│   ├── SegmentationController.py    # Segmentation overlay controller
│   └── ...                          # Other utility scripts
├── 3d_inputs/                       # C-arm and table 3D models
├── models/                          # Patient and C-arm models
├── ui/                              # UI components (sliders, buttons)
└── workspace_analysis_output/       # Workspace analysis results (generated)
```

## Setup Instructions

### 1. Install Python Environments

**Python 2.7 Environment (for H3D):**
```bash
# H3D requires Python 2.7
# Install H3D API following official documentation
```

**Python 3 Environment (for servers):**
```bash
# Create virtual environment for CPU mode
python -m venv .venv
.venv\Scripts\activate
pip install numpy vedo torch diffdrr pillow
```

**Optional - GPU Environment (Recommended for Real-time Performance):**

For ~40x faster DRR rendering (100ms vs 4s per frame), follow these steps:

```bash
# Create separate environment for GPU acceleration
python -m venv .venv_gpu
.venv_gpu\Scripts\activate
```

**Step 1: Check Your GPU and CUDA Version**
```bash
# Check if NVIDIA GPU is available
nvidia-smi
```
This will show your GPU model and CUDA version. Note the CUDA version (e.g., 11.8, 12.1).

**Step 2: Install PyTorch with CUDA Support**

Visit [pytorch.org](https://pytorch.org/get-started/locally/) and select your configuration, or use one of these:

```bash
# For CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# For CUDA 12.4
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```

**Step 3: Install Other Dependencies**
```bash
pip install numpy vedo diffdrr pillow
```

**Step 4: Verify GPU is Working**
```bash
python -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"
```

Expected output:
```
CUDA available: True
GPU: NVIDIA GeForce RTX 3060
```

If you see `CUDA available: False`, your PyTorch installation is CPU-only. Reinstall with correct CUDA version.

### 2. GPU Setup (Highly Recommended)

For real-time performance, set up GPU acceleration:

**Quick GPU Setup:**
1. Install [NVIDIA CUDA Toolkit](https://developer.nvidia.com/cuda-downloads) (version 11.8 or later)
2. Verify installation: `nvidia-smi` in terminal
3. Create GPU environment and install PyTorch with CUDA (see "Optional - GPU Environment" above)
4. Verify GPU works: `python -c "import torch; print(torch.cuda.is_available())"`

**Performance Impact:**
- Without GPU: Live demo will update every 4 seconds (not interactive)

**For Presentations/Demos:** GPU is essential for smooth live demonstrations.

### 3. Verify 3D Data Files

Ensure the following files exist:
- `3d_inputs/c_arm_pcd_pts.npy` - C-arm point cloud
- `3d_inputs/table_top_watertight_mesh.ply` - Table top mesh
- `3d_inputs/table_body_sphere_watertight_mesh.ply` - Table body mesh
- `3d_inputs/table_wheels_base_watertight_mesh.ply` - Table wheels mesh
- `models/patient_model.ply` - Patient mesh

## Running the System

1. **Start all servers with visualizer:**
```bash
python launch_all.py --visualizer
```

Optional flags:
- `--no-drr` - Skip DRR server (faster startup, basic X-ray only)
- `--visualizer` - Include collision visualizer window (Recommended)

2. **Manually open `main.x3d`**

## Usage

### Controls

**C-arm Controls (Right side):**
- Orbital (LAO/RAO): -100° to 100°
- Tilt (CRAN/CAUD): -90° to 270°
- Wigwag: -10° to 10°
- Lateral: -15 to 15 cm
- Horizontal: 0 to 15 cm
- Vertical: 0 to 46 cm

**Patient Table Controls (Left side):**
- Vertical: 0 to 36 cm
- Longitudinal: 0 to 70 cm
- Transverse: -13 to 13 cm

**Zoom:**
- Magnification: 0.5x to 2.0x (for DRR)

### Features

**Collision Detection:**
- Automatically checks for collisions as you move sliders
- Green border = Safe
- Red border = Collision detected
- Status indicator shows "No Collision" or "Collision Detected"

**DRR Mode:**
- Toggle button to switch between basic volume rendering and photorealistic DRR
- DRR mode shows real X-ray-like images with proper perspective

**Anatomical Segmentation:**
- Click dropdown to select anatomical structures (ribs, vertebrae, organs, etc.)
- Selected structures are highlighted in color on the X-ray
- Multiple structures can be selected simultaneously

**Standard Positions:**
- Pre-configured C-arm positions for common clinical views
- Numbered buttons (0-9) for quick access

## Testing & Demo Tools

### Collision Detection Demo

Interactive testing tool for collision detection without running the full system.

```bash
.venv\Scripts\activate
python collision_demo.py
```

**Features:**
1. **Standard Surgical Positions** - Tests 5 common C-arm positions (PA, AP, Lateral, Vascular)
2. **Extreme Positions** - Tests joint limits and edge cases
3. **Interactive Manual Test** - Enter custom joint values and test specific configurations
4. **Run All Tests** - Comprehensive automated testing

**Interactive Mode:**
- Enter C-arm joint values (orbital, tilt, wigwag, translations)
- Enter table joint values (vertical, longitudinal, transverse)
- Get immediate collision feedback with detailed point counts
- See which components are colliding (table top, body, wheels, patient)

**Example Output:**
```
[COLLISION] COLLISION DETECTED!
Collision Points:
  Table Top:    127 points
  Table Body:   0 points
  Table Base:   0 points
  Patient:      45 points
  TOTAL:        172 points
```

### Real-time 3D Visualizer

Standalone 3D visualization tool for debugging collision detection.

```bash
.venv\Scripts\activate
python collision_visualizer.py
```

**Controls:**
- Press **SPACEBAR** to update visualization from `collision_pose.json`
- Close window to exit

**Visual Feedback:**
- **Cyan** C-arm point cloud (turns red when colliding)
- **Orange** Table top mesh
- **Red** Table body mesh
- **Gray** Table wheels mesh
- **Beige** Patient model

**Usage Scenarios:**

*Standalone Testing:*
1. Run the visualizer
2. Run `collision_demo.py` in interactive mode
3. Press SPACEBAR in visualizer after each test

*With H3D System:*
1. Launch H3D system (`python launch_h3d.py`)
2. Run visualizer in a separate window
3. Move sliders in H3D
4. Press SPACEBAR in visualizer to see current state
5. Useful for presentation/demonstration purposes

### Manual Collision Testing

For programmatic testing, you can directly use the collision server:

```python
from collision_server import CollisionServer

# Initialize
server = CollisionServer()

# Test a configuration
result = server.check_collision(
    lao_rao_deg=0.0,           # Orbital angle
    cran_caud_deg=180.0,       # Tilt angle
    wigwag_deg=0.0,
    lateral_m=0.0,
    vertical_m=0.2,
    horizontal_m=0.1,
    table_vertical_m=0.15,
    table_longitudinal_m=0.3,
    table_transverse_m=0.0
)

print(f"Collision: {result['collision']}")
print(f"Total collision points: {result['collision_points']['total']}")
print(f"Table top: {result['collision_points']['table_top']}")
print(f"Patient: {result['collision_points']['patient']}")
```

### Surgical Workspace Analysis

**NEW:** Comprehensive workspace analysis tool that generates random poses and calculates collision-free reachability statistics, following the research paper methodology.

```bash
.venv\Scripts\activate
python workspace_analysis.py
```

**Quick Test (1,000 poses):**
```bash
python workspace_analysis.py --quick
```

**Analysis Modes:**

1. **Single Configuration Analysis**
```bash
# Analyze specific setup and intervention
python workspace_analysis.py --setup setup5 --intervention PA --samples 10000
```

2. **Compare All Setups**
```bash
# Compare all DOF configurations for one intervention
python workspace_analysis.py --compare-setups --intervention V2 --samples 10000
```

3. **Analyze All Interventions**
```bash
# Test all clinical interventions for one setup
python workspace_analysis.py --all-interventions --setup setup5 --samples 10000
```

**Available Configurations:**

*DOF Setups:*
- `setup1`: C-arm 5DOF (no lateral) - 5 DOF
- `setup2`: C-arm 6DOF (all joints) - 6 DOF  
- `setup3`: C-arm 6DOF + Table Transverse - 7 DOF
- `setup4`: C-arm 6DOF + Table Transverse + Vertical - 8 DOF
- `setup5`: C-arm 6DOF + Table All (default) - 9 DOF
- `setup6`: Table All (no C-arm movement) - 3 DOF

*Clinical Interventions:*
- `PA`: Posterior-Anterior (0° orbital, 180° tilt)
- `AP`: Anterior-Posterior (0° orbital, 0° tilt)
- `V1`: Vascular 1 (-30° orbital, 180° tilt)
- `V2`: Vascular 2 (45° orbital, 205° tilt)
- `Ver`: Vertebroplasty (-35° orbital, 180° tilt)
- `Lat`: Lateral (-90° orbital, 180° tilt)

**Example Output:**
```
================================================================================
RESULTS: C-arm 6DOF + Table All (Vertical, Longitudinal, Transverse)
Intervention: Posterior-Anterior
================================================================================

  Total poses tested:     10,000
  Collision-free:         3,265 (32.65%)
  Collision:              6,735 (67.35%)

  Collision breakdown:
    table_top           : 4,821 (48.21%)
    table_body          : 2,145 (21.45%)
    table_base          : 892 (8.92%)
    patient             : 3,678 (36.78%)

  Analysis time:          520.3s
  Processing rate:        19.2 poses/second
================================================================================
```

**Viewing Results:**

Display analysis results in formatted text:

```bash
# View results
python workspace_visualizer.py workspace_analysis_output/results.json
```

**Output:**
- Formatted text summary with:
  - Setup and intervention details
  - Collision-free statistics and percentages
  - Collision breakdown by component (table top, body, base, patient)
  - Performance metrics (poses/second, analysis time)
- JSON results with detailed statistics

**Use Cases:**
- Quantify surgical workspace for different DOF combinations
- Compare workspace sizes between configurations
- Identify optimal C-arm and table setups for specific interventions
- Generate publication-quality figures for presentations
- Validate workspace claims with statistical data

**Performance:**
- 10,000 poses: ~8-10 minutes on standard hardware
- 100,000 poses: ~80-100 minutes (for research-level analysis)
- Results saved automatically to `workspace_analysis_output/`

## Technical Details

### Collision Detection Algorithm

Based on point cloud + mesh intersection:
1. C-arm represented as point cloud (10,000+ points)
2. Table and patient represented as watertight meshes
3. Transform all objects to world coordinates using DH parameters
4. Check if C-arm points are inside any mesh using Vedo's `inside_points()`
5. Visual feedback updated in real-time

### DH Parameters

**C-arm Kinematic Chain:**
- Joint 1: Horizontal translation (prismatic)
- Joint 2: Vertical translation (prismatic)
- Joint 3: Wigwag rotation (revolute)
- Joint 4: Lateral translation (prismatic)
- Joint 5: Tilt/CRAN-CAUD (revolute)
- Joint 6: Orbital/LAO-RAO (revolute)

**Patient Table Chain:**
- Joint 1: Vertical translation (prismatic)
- Joint 2: Longitudinal translation (prismatic)
- Joint 3: Transverse translation (prismatic)

### Communication Protocol

**File-based IPC:**
- `collision_pose.json` - H3D writes current pose, servers read
- `collision_result.json` - Collision server writes results, H3D reads
- `segmentation_settings.json` - H3D writes selected segments, DRR server reads
- `drr_live.png` - DRR server writes rendered image, H3D displays

**Update Flow:**
1. User moves slider in H3D
2. CollisionClient.py writes pose to `collision_pose.json`
3. Both servers detect file change and process:
   - collision_server.py checks collisions -> writes `collision_result.json`
   - drr_server.py renders DRR -> writes `drr_live.png`
4. H3D reads results and updates display

## Performance

### GPU Mode (Recommended)
- DRR rendering: ~100ms per frame
- Collision detection: ~50ms per check
- Total system: Real-time (~7 fps capable)
- **~40x speedup over CPU mode**

### CPU Mode
- DRR rendering: ~4s per frame
- Collision detection: ~50ms per check
- Total system: 0.25 fps (update every 4 seconds)

### Performance Comparison Chart

| Component | CPU Mode | GPU Mode (CUDA) | Speedup |
|-----------|----------|-----------------|---------|
| DRR Rendering | ~4000ms | ~100ms | 40x |
| Collision Detection | ~50ms | ~50ms | 1x |
| Overall Frame Time | ~4050ms | ~150ms | 27x |
| Effective FPS | 0.25 fps | 6-7 fps | 24-28x |

**Recommendation:** GPU mode is essential for live demonstrations and real-time interaction.

## Troubleshooting

### Servers not responding
- Check that both servers are running
- Verify JSON files are being created (`collision_pose.json`, etc.)
- Check terminal output for errors

### Slow DRR rendering
- Install GPU environment with CUDA PyTorch
- Verify GPU is being used: Check DRR server output for "Using device: cuda"
- If still slow, see GPU troubleshooting below

### Collision detection not working
- Verify `3d_inputs/` folder contains all required meshes
- Check `collision_server.py` terminal for errors
- Try restarting the collision server

### H3D won't start
- Verify Python 2.7 environment is active
- Check H3D API is properly installed
- Ensure `main.x3d` file exists

### GPU-Specific Troubleshooting

**Problem: "CUDA available: False" after installing PyTorch**

Solution 1 - Wrong PyTorch version:
```bash
# Uninstall CPU version
pip uninstall torch torchvision torchaudio

# Reinstall with CUDA (match your CUDA version)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

Solution 2 - CUDA Toolkit not installed:
- Download and install [NVIDIA CUDA Toolkit](https://developer.nvidia.com/cuda-downloads)
- Make sure the version matches your PyTorch installation (e.g., CUDA 11.8)
- Restart your terminal after installation

Solution 3 - Outdated GPU drivers:
- Update NVIDIA drivers from [NVIDIA Driver Downloads](https://www.nvidia.com/Download/index.aspx)
- Minimum driver version: 450.80.02+ for CUDA 11.x

**Problem: DRR server says "Using device: cuda" but still slow**

Check:
```bash
# In your .venv_gpu environment
python -c "import torch; x = torch.rand(1000, 1000).cuda(); print('GPU Test:', x.device)"
```

If error occurs:
- GPU memory might be full (close other GPU applications)
- Try restarting the DRR server
- Check `nvidia-smi` for GPU utilization

**Problem: "RuntimeError: CUDA out of memory"**

Solution:
- Close other GPU-intensive applications (games, other ML programs)
- Reduce CT scan resolution (edit `drr_server.py`)
- Use a GPU with more VRAM (minimum 4GB recommended)

**Problem: GPU works but rendering quality is poor**

This is normal - check that:
- DRR Mode is enabled (toggle button in GUI)
- Zoom level is appropriate (0.5x to 2.0x)
- C-arm is positioned to view patient anatomy

### Verifying GPU Setup is Working

When `drr_server.py` starts successfully with GPU, you should see:

```
[1/6] Initializing DRR Generator...
      Using device: cuda
      GPU: NVIDIA GeForce RTX 3060
      [OK] DRR generator initialized

[2/6] Loading CT scan...
      Loaded CT: torch.Size([512, 512, 512])
      [OK] CT loaded

...

[6/6] DRR Server ready
      [GPU] Real-time rendering (~100ms per frame)
```

If you see `Using device: cpu` instead, follow GPU troubleshooting steps above.

## Credits

### Research Foundation

This project implements and extends the methodology from:

**F. Jaheen, V. Gutta, and P. Fallavollita,** *"C-arm and Patient Table Integrated Kinematics and Surgical Workspace Analysis,"* IEEE Access, 2024.

**Key concepts adopted from the paper:**
- Denavit-Hartenberg (DH) parameters for forward kinematics
- Point cloud + watertight mesh collision detection algorithm
- 6-DOF C-arm and multi-DOF table integrated kinematic chain
- Vedo library for 3D mesh operations and collision checking

**Original contributions in this Honours project:**
- Real-time interactive simulation system with H3D GUI
- GPU-accelerated photorealistic X-ray rendering (~40x speedup)
- Colored anatomical segmentation overlays (TotalSegmentator v2)
- Client-server architecture for Python 2.7/3 integration
- Real-time collision visual feedback system
- Interactive 3D collision visualizer

### Libraries

- **DiffDRR** - GPU-accelerated X-ray rendering
- **Vedo** - 3D visualization and mesh operations (v2023.4.6)
- **H3D API** - 3D graphics and haptics framework
- **PyTorch** - Deep learning framework (GPU acceleration)
- **TotalSegmentator** - Anatomical segmentation labels

## License

Honours Project - Academic Use

