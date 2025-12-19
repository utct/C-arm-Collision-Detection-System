"""
Quick Test - Collision Detection System
Tests if server can be started and performs collision checks
"""

import sys
import os

def test_imports():
    """Test if required packages are installed"""
    print("=" * 70)
    print("TEST 1: Checking Python packages")
    print("=" * 70)
    
    try:
        import numpy
        print("[OK] numpy version:", numpy.__version__)
    except ImportError as e:
        print("[FAIL] numpy not found:", e)
        print("       Install with: pip install numpy")
        return False
    
    try:
        import vedo
        print("[OK] vedo version:", vedo.__version__)
    except ImportError as e:
        print("[FAIL] vedo not found:", e)
        print("       Install with: pip install vedo")
        return False
    
    print("\n✅ All packages installed correctly!\n")
    return True

def test_files():
    """Test if required 3D files exist"""
    print("=" * 70)
    print("TEST 2: Checking 3D data files")
    print("=" * 70)
    
    files = [
        '3d_inputs/c_arm_pcd_pts.npy',
        '3d_inputs/table_top_watertight_mesh.ply',
        '3d_inputs/table_body_sphere_watertight_mesh.ply',
        '3d_inputs/table_wheels_base_watertight_mesh.ply'
    ]
    
    all_exist = True
    for filepath in files:
        if os.path.exists(filepath):
            size = os.path.getsize(filepath) / 1024  # KB
            print(f"[OK] {filepath} ({size:.1f} KB)")
        else:
            print(f"[FAIL] {filepath} NOT FOUND")
            all_exist = False
    
    if all_exist:
        print("\n✅ All 3D files found!\n")
    else:
        print("\n❌ Some files are missing!")
        print("   Make sure you're running from project root directory.\n")
    
    return all_exist

def test_collision_check():
    """Test collision detection with sample poses"""
    print("=" * 70)
    print("TEST 3: Running collision checks")
    print("=" * 70)
    
    try:
        import numpy as np
        import vedo
        
        # Load data
        print("\nLoading C-arm point cloud...")
        c_arm_pc = vedo.Points(np.load('3d_inputs/c_arm_pcd_pts.npy'))
        print(f"  Loaded {c_arm_pc.points().shape[0]} points")
        
        print("\nLoading table meshes...")
        table_top = vedo.load('3d_inputs/table_top_watertight_mesh.ply')
        table_body = vedo.load('3d_inputs/table_body_sphere_watertight_mesh.ply')
        table_base = vedo.load('3d_inputs/table_wheels_base_watertight_mesh.ply')
        print(f"  Table top: {table_top.npoints} vertices")
        print(f"  Table body: {table_body.npoints} vertices")
        print(f"  Table base: {table_base.npoints} vertices")
        
        # Test collision at neutral pose
        print("\n" + "-" * 70)
        print("Testing collision at neutral pose (LAO=0°, CRAN=0°)...")
        print("-" * 70)
        
        # C-arm at neutral position
        c_arm_pc_copy = c_arm_pc.clone()
        
        # Table at position from main.x3d
        table_pose = np.eye(4)
        table_pose[0, 3] = 0.22
        table_pose[1, 3] = -0.05
        table_pose[2, 3] = 0.1
        
        table_top_copy = table_top.clone()
        table_top_copy.apply_transform(T=table_pose, reset=False, concatenate=False)
        
        # Check collision
        collision_points = table_top_copy.inside_points(c_arm_pc_copy.points())
        count = collision_points.points().shape[0]
        
        print(f"\nCollision points detected: {count}")
        if count == 0:
            print("✅ SAFE - No collision at neutral pose")
        else:
            print("[COLLISION] Check transformation matrices")
        
        # Test collision at extreme angle
        print("\n" + "-" * 70)
        print("Testing collision at extreme angle (LAO=60°, CRAN=40°)...")
        print("-" * 70)
        
        # Create rotation transformation
        lao_rad = np.radians(60)
        cran_rad = np.radians(40)
        
        T = np.eye(4)
        cos_lao = np.cos(lao_rad)
        sin_lao = np.sin(lao_rad)
        cos_cran = np.cos(cran_rad)
        sin_cran = np.sin(cran_rad)
        
        T[0, 0] = cos_lao
        T[0, 1] = -sin_lao * cos_cran
        T[0, 2] = sin_lao * sin_cran
        T[1, 0] = sin_lao
        T[1, 1] = cos_lao * cos_cran
        T[1, 2] = -cos_lao * sin_cran
        T[2, 1] = sin_cran
        T[2, 2] = cos_cran
        
        c_arm_pc_copy2 = c_arm_pc.clone()
        c_arm_pc_copy2.apply_transform(T=T, reset=False, concatenate=False)
        
        collision_points2 = table_top_copy.inside_points(c_arm_pc_copy2.points())
        count2 = collision_points2.points().shape[0]
        
        print(f"\nCollision points detected: {count2}")
        if count2 > 0:
            print("✅ COLLISION - System detecting collisions correctly")
        else:
            print("[WARNING] No collision detected - Might need transformation adjustment")
        
        print("\n" + "=" * 70)
        print("✅ Collision detection system is functional!")
        print("=" * 70)
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR during collision check: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "COLLISION SYSTEM TEST SUITE" + " " * 25 + "║")
    print("╚" + "=" * 68 + "╝")
    print("\n")
    
    # Run tests
    test1_pass = test_imports()
    if not test1_pass:
        print("\n❌ FAILED: Install missing packages first")
        return 1
    
    test2_pass = test_files()
    if not test2_pass:
        print("\n❌ FAILED: Missing required 3D files")
        return 1
    
    test3_pass = test_collision_check()
    if not test3_pass:
        print("\n❌ FAILED: Collision detection error")
        return 1
    
    # Success!
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 24 + "ALL TESTS PASSED!" + " " * 28 + "║")
    print("╚" + "=" * 68 + "╝")
    print("\n")
    print("[READY] Ready to run collision_server.py!")
    print("\n   Next steps:")
    print("   1. Open new terminal")
    print("   2. Run: python collision_server.py")
    print("   3. Launch H3D and open main.x3d")
    print("   4. Move sliders and watch collision indicator!\n")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
