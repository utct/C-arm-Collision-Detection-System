#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Collision Detection Demo
=========================

Standalone demonstration and testing script for the collision detection system.
Tests various C-arm and table configurations and visualizes collisions.

Usage:
    python collision_demo.py
"""

import sys
import os
from pathlib import Path

# Add lib directory to path
lib_path = Path(__file__).parent / 'lib'
sys.path.insert(0, str(lib_path))

import numpy as np
# Import the actual collision server class
import sys
sys.path.insert(0, '.')
from collision_server import CollisionServer


class CollisionDetector:
    """Wrapper class to adapt CollisionServer to demo API"""
    def __init__(self):
        self.server = CollisionServer()
        self.last_result = None
    
    def check_collision(self, c_arm, table):
        """Check collision with joint dictionaries"""
        # Convert from demo format to server format
        result = self.server.check_collision(
            lao_rao_deg=c_arm.get('orbital', 0.0),
            cran_caud_deg=c_arm.get('tilt', 0.0),
            wigwag_deg=c_arm.get('wigwag', 0.0),
            lateral_m=c_arm.get('lateral', 0.0),
            vertical_m=c_arm.get('vertical', 0.2),
            horizontal_m=c_arm.get('horizontal', 0.1),
            table_vertical_m=table.get('vertical', 0.15),
            table_longitudinal_m=table.get('longitudinal', 0.3),
            table_transverse_m=table.get('transverse', 0.0)
        )
        self.last_result = result
        return result['collision']
    
    def get_collision_details(self):
        """Get details from last collision check"""
        if self.last_result:
            points = self.last_result.get('collision_points', {})
            return {
                'table_top': points.get('table_top', 0),
                'table_body': points.get('table_body', 0),
                'table_base': points.get('table_wheels', 0),
                'patient': points.get('patient', 0),
                'total_points': points.get('total', 0)
            }
        return {'table_top': 0, 'table_body': 0, 'table_base': 0, 'patient': 0, 'total_points': 0}
    
    def visualize_collision(self, c_arm, table, show=True):
        """Visualize collision - use collision_visualizer.py separately"""
        print("\n  To visualize:")
        print("  1. Save these values to collision_pose.json")
        print("  2. Run: python collision_visualizer.py")
        print("  3. Press SPACEBAR in the visualizer window")


def print_header(text):
    """Print formatted section header."""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def print_configuration(c_arm_joints, table_joints):
    """Print joint configuration in a readable format."""
    print("\n  C-arm Configuration:")
    print(f"    Lateral:    {c_arm_joints['lateral']:7.3f} m")
    print(f"    Vertical:   {c_arm_joints['vertical']:7.3f} m")
    print(f"    Wigwag:     {c_arm_joints['wigwag']:7.1f}°")
    print(f"    Horizontal: {c_arm_joints['horizontal']:7.3f} m")
    print(f"    Tilt:       {c_arm_joints['tilt']:7.1f}°")
    print(f"    Orbital:    {c_arm_joints['orbital']:7.1f}°")
    
    print("\n  Table Configuration:")
    print(f"    Vertical:     {table_joints['vertical']:7.3f} m")
    print(f"    Longitudinal: {table_joints['longitudinal']:7.3f} m")
    print(f"    Transverse:   {table_joints['transverse']:7.3f} m")


def test_standard_positions():
    """Test collision detection with standard surgical positions."""
    print_header("STANDARD SURGICAL POSITIONS TEST")
    
    # Initialize detector
    print("\nInitializing Collision Detector...")
    detector = CollisionDetector()
    
    # Standard table position (3 DOF)
    table_standard = {
        'vertical': 0.15,
        'longitudinal': 0.3,
        'transverse': 0.0
    }
    
    # Test positions based on typical surgical configurations
    test_positions = [
        {
            'name': 'PA (Posterior-Anterior)',
            'c_arm': {
                'lateral': 0.0,
                'vertical': 0.2,
                'wigwag': 0.0,
                'horizontal': 0.1,
                'tilt': 0.0,
                'orbital': 0.0
            }
        },
        {
            'name': 'AP (Anterior-Posterior)',
            'c_arm': {
                'lateral': 0.0,
                'vertical': 0.2,
                'wigwag': 0.0,
                'horizontal': 0.1,
                'tilt': 180.0,
                'orbital': 0.0
            }
        },
        {
            'name': 'Lateral',
            'c_arm': {
                'lateral': 0.0,
                'vertical': 0.2,
                'wigwag': 0.0,
                'horizontal': 0.1,
                'tilt': 0.0,
                'orbital': -90.0
            }
        },
        {
            'name': 'Vascular 1 (RAO/LAO)',
            'c_arm': {
                'lateral': 0.0,
                'vertical': 0.2,
                'wigwag': 0.0,
                'horizontal': 0.1,
                'tilt': -30.0,
                'orbital': -30.0
            }
        },
        {
            'name': 'Vascular 2',
            'c_arm': {
                'lateral': 0.0,
                'vertical': 0.2,
                'wigwag': 0.0,
                'horizontal': 0.1,
                'tilt': 25.0,
                'orbital': 45.0
            }
        }
    ]
    
    results = []
    for idx, position in enumerate(test_positions, 1):
        print(f"\n[Test {idx}] {position['name']}")
        print("-" * 70)
        
        collision = detector.check_collision(position['c_arm'], table_standard)
        details = detector.get_collision_details()
        
        status = "[COLLISION] COLLISION DETECTED" if collision else "[SAFE]"
        print(f"\n  Status: {status}")
        
        if collision:
            print(f"  Collision Points:")
            print(f"    Table Top:    {details['table_top']} points")
            print(f"    Table Body:   {details['table_body']} points")
            print(f"    Table Base:   {details['table_base']} points")
            print(f"    Patient:      {details['patient']} points")
            print(f"    TOTAL:        {details['total_points']} points")
        
        results.append({
            'name': position['name'],
            'collision': collision,
            'details': details
        })
    
    # Summary
    print_header("SUMMARY")
    safe_count = sum(1 for r in results if not r['collision'])
    collision_count = sum(1 for r in results if r['collision'])
    
    print(f"\n  Total Tests:     {len(results)}")
    print(f"  Safe Positions:  {safe_count}")
    print(f"  Collisions:      {collision_count}")
    
    print("\n  Detailed Results:")
    for r in results:
        status = "COLLISION" if r['collision'] else "SAFE"
        symbol = "[X] " if r['collision'] else "[OK] "
        print(f"    {symbol} {r['name']:<30} {status}")


def test_extreme_positions():
    """Test collision detection at joint limits."""
    print_header("EXTREME POSITIONS TEST")
    
    print("\nInitializing Collision Detector...")
    detector = CollisionDetector()
    
    # Standard table (3 DOF)
    table_standard = {
        'vertical': 0.15,
        'longitudinal': 0.3,
        'transverse': 0.0
    }
    
    extreme_tests = [
        {
            'name': 'C-arm Full Extension',
            'c_arm': {
                'lateral': 0.5,
                'vertical': 0.46,
                'wigwag': 10.0,
                'horizontal': 0.15,
                'tilt': 0.0,
                'orbital': 0.0
            }
        },
        {
            'name': 'C-arm Minimum Height',
            'c_arm': {
                'lateral': 0.0,
                'vertical': 0.0,
                'wigwag': 0.0,
                'horizontal': 0.0,
                'tilt': 0.0,
                'orbital': 0.0
            }
        },
        {
            'name': 'C-arm Maximum Tilt',
            'c_arm': {
                'lateral': 0.0,
                'vertical': 0.2,
                'wigwag': 0.0,
                'horizontal': 0.1,
                'tilt': 270.0,
                'orbital': 0.0
            }
        },
        {
            'name': 'C-arm Maximum Orbital',
            'c_arm': {
                'lateral': 0.0,
                'vertical': 0.2,
                'wigwag': 0.0,
                'horizontal': 0.1,
                'tilt': 0.0,
                'orbital': 100.0
            }
        }
    ]
    
    for idx, test in enumerate(extreme_tests, 1):
        print(f"\n[Test {idx}] {test['name']}")
        print("-" * 70)
        
        collision = detector.check_collision(test['c_arm'], table_standard)
        details = detector.get_collision_details()
        
        status = "[COLLISION]" if collision else "[SAFE]"
        print(f"  Status: {status}")
        
        if collision:
            print(f"  Collision Points: {details['total_points']}")


def interactive_test():
    """Interactive collision testing with user input."""
    print_header("INTERACTIVE COLLISION TEST")
    
    print("\nInitializing Collision Detector...")
    detector = CollisionDetector()
    
    print("\nEnter joint values (press Enter for default):")
    
    # Get C-arm joints
    print("\nC-arm Configuration:")
    c_arm = {}
    c_arm['lateral'] = float(input("  Lateral (m) [-0.5 to 0.5, default 0.0]: ") or "0.0")
    c_arm['vertical'] = float(input("  Vertical (m) [0 to 0.46, default 0.2]: ") or "0.2")
    c_arm['wigwag'] = float(input("  Wigwag (°) [-10 to 10, default 0.0]: ") or "0.0")
    c_arm['horizontal'] = float(input("  Horizontal (m) [0 to 0.15, default 0.1]: ") or "0.1")
    c_arm['tilt'] = float(input("  Tilt (°) [-90 to 270, default 0.0]: ") or "0.0")
    c_arm['orbital'] = float(input("  Orbital (°) [-100 to 100, default 0.0]: ") or "0.0")
    
    # Get table joints (3 DOF)
    print("\nTable Configuration:")
    table = {}
    table['vertical'] = float(input("  Vertical (m) [0 to 0.36, default 0.15]: ") or "0.15")
    table['longitudinal'] = float(input("  Longitudinal (m) [0 to 0.7, default 0.3]: ") or "0.3")
    table['transverse'] = float(input("  Transverse (m) [-0.13 to 0.13, default 0.0]: ") or "0.0")
    
    # Check collision
    print("\nChecking for collisions...")
    print_configuration(c_arm, table)
    
    collision = detector.check_collision(c_arm, table)
    details = detector.get_collision_details()
    
    print("\n" + "="*70)
    if collision:
        print("  [COLLISION] COLLISION DETECTED!")
        print("="*70)
        print(f"\n  Collision Points:")
        print(f"    Table Top:    {details['table_top']} points")
        print(f"    Table Body:   {details['table_body']} points")
        print(f"    Table Base:   {details['table_base']} points")
        print(f"    Patient:      {details['patient']} points")
        print(f"    TOTAL:        {details['total_points']} points")
    else:
        print("  [SAFE] NO COLLISION - CONFIGURATION IS SAFE")
        print("="*70)
    
    # Ask if user wants to visualize
    visualize = input("\nVisualize this configuration? (y/n): ").lower().strip()
    if visualize == 'y':
        print("\nOpening visualization window...")
        detector.visualize_collision(c_arm, table, show=True)


def main():
    """Main demo function."""
    print("\n")
    print("╔" + "═"*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "    C-ARM & PATIENT TABLE COLLISION DETECTION DEMO".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "═"*68 + "╝")
    
    while True:
        print("\n\nSelect Test Mode:")
        print("  1. Standard Surgical Positions")
        print("  2. Extreme Positions (Joint Limits)")
        print("  3. Interactive Manual Test")
        print("  4. Run All Tests")
        print("  5. Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == '1':
            test_standard_positions()
        elif choice == '2':
            test_extreme_positions()
        elif choice == '3':
            interactive_test()
        elif choice == '4':
            test_standard_positions()
            test_extreme_positions()
        elif choice == '5':
            print("\nExiting demo. Goodbye!")
            break
        else:
            print("\n❌ Invalid choice. Please enter 1-5.")
    
    print("\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
