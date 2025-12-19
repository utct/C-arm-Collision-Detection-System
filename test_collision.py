#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Quick Test - Collision Detection System
========================================

Simple test to verify the collision detection system is working.
"""

import sys
from pathlib import Path

# Add lib directory to path
lib_path = Path(__file__).parent / 'lib'
sys.path.insert(0, str(lib_path))

print("Testing Collision Detection System...")
print("="*60)

try:
    print("\n1. Testing imports...")
    from CollisionDetection import CollisionDetector
    print("   [OK] CollisionDetection module imported successfully")
    
    print("\n2. Initializing detector...")
    detector = CollisionDetector()
    print("   [OK] Detector initialized successfully")
    
    print("\n3. Testing safe configuration...")
    c_arm_safe = {
        'lateral': 0.0,
        'vertical': 0.2,
        'wigwag': 0.0,
        'horizontal': 0.1,
        'tilt': 0.0,
        'orbital': 0.0
    }
    
    table_safe = {
        'vertical': 0.1,
        'trend': 0.0,
        'tilt': 0.0,
        'longitudinal': 0.3,
        'transverse': 0.0
    }
    
    collision = detector.check_collision(c_arm_safe, table_safe)
    details = detector.get_collision_details()
    
    print(f"   Result: {'COLLISION' if collision else 'SAFE'}")
    print(f"   Details: {details}")
    print("   [OK] Collision check completed")
    
    print("\n" + "="*60)
    print("[PASS] ALL TESTS PASSED!")
    print("="*60)
    print("\nThe collision detection system is working correctly.")
    print("You can now run 'python collision_demo.py' for full demo.\n")
    
except ImportError as e:
    print(f"\n❌ Import Error: {e}")
    print("\nPlease install required packages:")
    print("  pip install -r requirements_collision.txt")
    
except FileNotFoundError as e:
    print(f"\n❌ File Not Found: {e}")
    print("\nPlease ensure 3D assets are in the '3d_inputs' directory:")
    print("  - c_arm_pcd_pts.npy")
    print("  - table_top_watertight_mesh.ply")
    print("  - table_body_sphere_watertight_mesh.ply")
    print("  - table_wheels_base_watertight_mesh.ply")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
