#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for table DOF implementation
Tests collision detection with table movement
"""

import json
import time
import os

def write_test_pose(c_arm_pose, table_pose, test_name):
    """Write a test pose to collision_pose.json"""
    pose_data = {
        # C-arm DOF
        'lao_rao': c_arm_pose['lao_rao'],
        'cran_caud': c_arm_pose['cran_caud'],
        'wigwag': c_arm_pose['wigwag'],
        'lateral': c_arm_pose['lateral'],
        'vertical': c_arm_pose['vertical'],
        'horizontal': c_arm_pose['horizontal'],
        # Table DOF
        'table_vertical': table_pose['vertical'],
        'table_longitudinal': table_pose['longitudinal'],
        'table_transverse': table_pose['transverse'],
        'timestamp': time.time(),
        'test_name': test_name
    }
    
    with open('collision_pose.json', 'w') as f:
        json.dump(pose_data, f, indent=2)
    
    print(f"\n[TEST: {test_name}]")
    print(f"  C-arm: ORB={c_arm_pose['lao_rao']:.1f}° TILT={c_arm_pose['cran_caud']:.1f}° "
          f"LAT={c_arm_pose['lateral']:.2f}m VER={c_arm_pose['vertical']:.2f}m HOR={c_arm_pose['horizontal']:.2f}m")
    print(f"  Table: V={table_pose['vertical']:.2f}m L={table_pose['longitudinal']:.2f}m T={table_pose['transverse']:.2f}m")
    
    # Wait for server to process
    time.sleep(0.3)
    
    # Read result
    if os.path.exists('collision_result.json'):
        with open('collision_result.json', 'r') as f:
            result = json.load(f)
        
        collision = result.get('collision', False)
        points = result.get('collision_points', {}).get('total', 0)
        status = "❌ COLLISION" if collision else "✅ SAFE"
        print(f"  Result: {status} ({points} penetrating points)")
        return collision
    else:
        print("  Result: [WARNING] No response from server")
        return None

def main():
    """Run test suite for table DOF"""
    print("=" * 70)
    print("TABLE DOF COLLISION DETECTION TEST SUITE")
    print("=" * 70)
    print("\nMake sure collision_server.py is running!")
    print("Press Ctrl+C to stop\n")
    
    time.sleep(1)
    
    # Test 1: Neutral position (should be safe)
    write_test_pose(
        c_arm_pose={'lao_rao': 0, 'cran_caud': 0, 'wigwag': 0, 
                   'lateral': 0, 'vertical': 0, 'horizontal': 0},
        table_pose={'vertical': 0, 'longitudinal': 0, 'transverse': 0},
        test_name="Neutral Position (all zeros)"
    )
    
    # Test 2: Table raised, C-arm low (potential collision)
    write_test_pose(
        c_arm_pose={'lao_rao': 0, 'cran_caud': 0, 'wigwag': 0, 
                   'lateral': 0, 'vertical': 0, 'horizontal': 0},
        table_pose={'vertical': 0.36, 'longitudinal': 0, 'transverse': 0},
        test_name="Table Raised Max (vertical = 36cm)"
    )
    
    # Test 3: Table extended forward
    write_test_pose(
        c_arm_pose={'lao_rao': 0, 'cran_caud': 0, 'wigwag': 0, 
                   'lateral': 0, 'vertical': 0, 'horizontal': 0},
        table_pose={'vertical': 0, 'longitudinal': 0.7, 'transverse': 0},
        test_name="Table Extended Forward (longitudinal = 70cm)"
    )
    
    # Test 4: Table shifted left
    write_test_pose(
        c_arm_pose={'lao_rao': 0, 'cran_caud': 0, 'wigwag': 0, 
                   'lateral': 0, 'vertical': 0, 'horizontal': 0},
        table_pose={'vertical': 0, 'longitudinal': 0, 'transverse': -0.13},
        test_name="Table Shifted Left (transverse = -13cm)"
    )
    
    # Test 5: Table shifted right
    write_test_pose(
        c_arm_pose={'lao_rao': 0, 'cran_caud': 0, 'wigwag': 0, 
                   'lateral': 0, 'vertical': 0, 'horizontal': 0},
        table_pose={'vertical': 0, 'longitudinal': 0, 'transverse': 0.13},
        test_name="Table Shifted Right (transverse = +13cm)"
    )
    
    # Test 6: C-arm angled with table raised (likely collision)
    write_test_pose(
        c_arm_pose={'lao_rao': 30, 'cran_caud': 30, 'wigwag': 0, 
                   'lateral': 0, 'vertical': 0.2, 'horizontal': 0},
        table_pose={'vertical': 0.3, 'longitudinal': 0.3, 'transverse': 0},
        test_name="C-arm Angled + Table Raised (potential collision)"
    )
    
    # Test 7: Complex pose with all DOF
    write_test_pose(
        c_arm_pose={'lao_rao': -45, 'cran_caud': 20, 'wigwag': 5, 
                   'lateral': 0.2, 'vertical': 0.15, 'horizontal': 0.1},
        table_pose={'vertical': 0.18, 'longitudinal': 0.35, 'transverse': 0.05},
        test_name="Complex Multi-DOF Configuration"
    )
    
    print("\n" + "=" * 70)
    print("TEST SUITE COMPLETE")
    print("=" * 70)
    print("\nCheck collision_server.py console for detailed collision reports")
    print("You can also run collision_visualizer.py and press SPACEBAR")
    print("to visualize the last test pose.\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
