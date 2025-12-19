"""
Automated script to run all collision detection tests
"""
import sys
import os

# Add lib directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

from CollisionDetection import CollisionDetector
import numpy as np


def print_header(title):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def print_test_result(test_name, collision, details):
    """Print formatted test result"""
    status = "[!] COLLISION DETECTED" if collision else "[OK] SAFE"
    print(f"\n[Test] {test_name}")
    print("-"*70)
    print(f"\n  Status: {status}")
    
    if collision:
        print("  Collision Points:")
        print(f"    Table Top:    {details['table_top']} points")
        print(f"    Table Body:   {details['table_body']} points")
        print(f"    Table Base:   {details['table_base']} points")
        print(f"    TOTAL:        {details['total_points']} points")


def test_standard_positions(detector):
    """Test standard surgical positions"""
    print_header("STANDARD SURGICAL POSITIONS TEST")
    
    positions = {
        "PA (Posterior-Anterior)": {
            'c_arm': {'lateral': 0.0, 'vertical': 0.0, 'wigwag': 0.0, 'horizontal': 0.0, 'tilt': 0.0, 'orbital': 0.0},
            'table': {'vertical': 0.0, 'trend': 0.0, 'tilt': 0.0, 'longitudinal': 0.0, 'transverse': 0.0}
        },
        "AP (Anterior-Posterior)": {
            'c_arm': {'lateral': 0.0, 'vertical': 0.0, 'wigwag': 0.0, 'horizontal': 0.0, 'tilt': 0.0, 'orbital': np.pi},
            'table': {'vertical': 0.0, 'trend': 0.0, 'tilt': 0.0, 'longitudinal': 0.0, 'transverse': 0.0}
        },
        "Lateral": {
            'c_arm': {'lateral': 0.0, 'vertical': 0.0, 'wigwag': 0.0, 'horizontal': 0.0, 'tilt': 0.0, 'orbital': np.pi/2},
            'table': {'vertical': 0.0, 'trend': 0.0, 'tilt': 0.0, 'longitudinal': 0.0, 'transverse': 0.0}
        },
        "Vascular 1 (RAO/LAO)": {
            'c_arm': {'lateral': 0.0, 'vertical': 0.0, 'wigwag': 0.0, 'horizontal': 0.0, 'tilt': np.pi/6, 'orbital': np.pi/4},
            'table': {'vertical': 0.0, 'trend': 0.0, 'tilt': 0.0, 'longitudinal': 0.0, 'transverse': 0.0}
        },
        "Vascular 2": {
            'c_arm': {'lateral': 0.0, 'vertical': 0.0, 'wigwag': 0.0, 'horizontal': 0.0, 'tilt': -np.pi/6, 'orbital': -np.pi/4},
            'table': {'vertical': 0.0, 'trend': 0.0, 'tilt': 0.0, 'longitudinal': 0.0, 'transverse': 0.0}
        }
    }
    
    results = []
    for name, config in positions.items():
        collision = detector.check_collision(
            config['c_arm'],
            config['table']
        )
        details = detector.get_collision_details()
        print_test_result(name, collision, details)
        results.append((name, collision, details))
    
    return results


def test_extreme_positions(detector):
    """Test extreme joint positions (near limits)"""
    print_header("EXTREME POSITIONS TEST (Joint Limits)")
    
    positions = {
        "Max Lateral Left": {
            'c_arm': {'lateral': -0.4, 'vertical': 0.0, 'wigwag': 0.0, 'horizontal': 0.0, 'tilt': 0.0, 'orbital': 0.0},
            'table': {'vertical': 0.0, 'trend': 0.0, 'tilt': 0.0, 'longitudinal': 0.0, 'transverse': 0.0}
        },
        "Max Lateral Right": {
            'c_arm': {'lateral': 0.4, 'vertical': 0.0, 'wigwag': 0.0, 'horizontal': 0.0, 'tilt': 0.0, 'orbital': 0.0},
            'table': {'vertical': 0.0, 'trend': 0.0, 'tilt': 0.0, 'longitudinal': 0.0, 'transverse': 0.0}
        },
        "Max Vertical Up": {
            'c_arm': {'lateral': 0.0, 'vertical': 0.8, 'wigwag': 0.0, 'horizontal': 0.0, 'tilt': 0.0, 'orbital': 0.0},
            'table': {'vertical': 0.0, 'trend': 0.0, 'tilt': 0.0, 'longitudinal': 0.0, 'transverse': 0.0}
        },
        "Max Vertical Down": {
            'c_arm': {'lateral': 0.0, 'vertical': -0.8, 'wigwag': 0.0, 'horizontal': 0.0, 'tilt': 0.0, 'orbital': 0.0},
            'table': {'vertical': 0.0, 'trend': 0.0, 'tilt': 0.0, 'longitudinal': 0.0, 'transverse': 0.0}
        },
        "Max Tilt + Max Orbital": {
            'c_arm': {'lateral': 0.0, 'vertical': 0.0, 'wigwag': 0.0, 'horizontal': 0.0, 'tilt': np.pi/3, 'orbital': np.pi},
            'table': {'vertical': 0.0, 'trend': 0.0, 'tilt': 0.0, 'longitudinal': 0.0, 'transverse': 0.0}
        },
        "Table Max Height": {
            'c_arm': {'lateral': 0.0, 'vertical': 0.0, 'wigwag': 0.0, 'horizontal': 0.0, 'tilt': 0.0, 'orbital': 0.0},
            'table': {'vertical': 0.5, 'trend': 0.0, 'tilt': 0.0, 'longitudinal': 0.0, 'transverse': 0.0}
        },
        "Table Max Trend": {
            'c_arm': {'lateral': 0.0, 'vertical': 0.0, 'wigwag': 0.0, 'horizontal': 0.0, 'tilt': 0.0, 'orbital': 0.0},
            'table': {'vertical': 0.0, 'trend': np.pi/6, 'tilt': 0.0, 'longitudinal': 0.0, 'transverse': 0.0}
        },
        "Table Max Tilt": {
            'c_arm': {'lateral': 0.0, 'vertical': 0.0, 'wigwag': 0.0, 'horizontal': 0.0, 'tilt': 0.0, 'orbital': 0.0},
            'table': {'vertical': 0.0, 'trend': 0.0, 'tilt': np.pi/6, 'longitudinal': 0.0, 'transverse': 0.0}
        },
        "Table Max Longitudinal": {
            'c_arm': {'lateral': 0.0, 'vertical': 0.0, 'wigwag': 0.0, 'horizontal': 0.0, 'tilt': 0.0, 'orbital': 0.0},
            'table': {'vertical': 0.0, 'trend': 0.0, 'tilt': 0.0, 'longitudinal': 0.6, 'transverse': 0.0}
        },
        "Combined Extreme 1": {
            'c_arm': {'lateral': -0.3, 'vertical': 0.5, 'wigwag': 0.0, 'horizontal': 0.0, 'tilt': np.pi/4, 'orbital': np.pi/2},
            'table': {'vertical': 0.3, 'trend': 0.0, 'tilt': 0.0, 'longitudinal': 0.4, 'transverse': 0.2}
        }
    }
    
    results = []
    for name, config in positions.items():
        collision = detector.check_collision(
            config['c_arm'],
            config['table']
        )
        details = detector.get_collision_details()
        print_test_result(name, collision, details)
        results.append((name, collision, details))
    
    return results


def print_summary(standard_results, extreme_results):
    """Print overall summary"""
    print_header("OVERALL SUMMARY")
    
    total_tests = len(standard_results) + len(extreme_results)
    total_collisions = sum(1 for _, collision, _ in standard_results + extreme_results if collision)
    total_safe = total_tests - total_collisions
    
    print(f"  Total Tests:     {total_tests}")
    print(f"  Safe Positions:  {total_safe}")
    print(f"  Collisions:      {total_collisions}")
    print(f"  Safety Rate:     {(total_safe/total_tests)*100:.1f}%\n")
    
    print("  Standard Surgical Positions:")
    for name, collision, details in standard_results:
        status = "[!] COLLISION" if collision else "[OK] SAFE"
        points = details['total_points'] if collision else 0
        print(f"    {status:20} {name:30} ({points} pts)")
    
    print("\n  Extreme Positions:")
    for name, collision, details in extreme_results:
        status = "[!] COLLISION" if collision else "[OK] SAFE"
        points = details['total_points'] if collision else 0
        print(f"    {status:20} {name:30} ({points} pts)")


def main():
    print_header("COMPREHENSIVE COLLISION DETECTION TEST SUITE")
    
    print("Initializing Collision Detector...")
    detector = CollisionDetector()
    print("[OK] Initialized successfully\n")
    
    # Run all tests
    standard_results = test_standard_positions(detector)
    extreme_results = test_extreme_positions(detector)
    
    # Print summary
    print_summary(standard_results, extreme_results)
    
    print("\n" + "="*70)
    print("  ALL TESTS COMPLETED")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
