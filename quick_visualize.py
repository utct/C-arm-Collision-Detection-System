"""
Quick visualization of a single collision scenario
"""
import sys
import os
import numpy as np

# Add lib directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

from CollisionDetection import CollisionDetector
import vedo


# Test different scenarios
scenarios = {
    "pa": {
        'name': "PA (Posterior-Anterior) - SAFE",
        'c_arm': {'lateral': 0.0, 'vertical': 0.0, 'wigwag': 0.0, 'horizontal': 0.0, 'tilt': 0.0, 'orbital': 0.0},
        'table': {'vertical': 0.0, 'trend': 0.0, 'tilt': 0.0, 'longitudinal': 0.0, 'transverse': 0.0}
    },
    "lateral": {
        'name': "Lateral - SAFE",
        'c_arm': {'lateral': 0.0, 'vertical': 0.0, 'wigwag': 0.0, 'horizontal': 0.0, 'tilt': 0.0, 'orbital': np.pi/2},
        'table': {'vertical': 0.0, 'trend': 0.0, 'tilt': 0.0, 'longitudinal': 0.0, 'transverse': 0.0}
    },
    "collision1": {
        'name': "Max Lateral Right - COLLISION (903 pts)",
        'c_arm': {'lateral': 0.4, 'vertical': 0.0, 'wigwag': 0.0, 'horizontal': 0.0, 'tilt': 0.0, 'orbital': 0.0},
        'table': {'vertical': 0.0, 'trend': 0.0, 'tilt': 0.0, 'longitudinal': 0.0, 'transverse': 0.0}
    },
    "collision2": {
        'name': "Max Vertical Down - COLLISION (281 pts)",
        'c_arm': {'lateral': 0.0, 'vertical': -0.8, 'wigwag': 0.0, 'horizontal': 0.0, 'tilt': 0.0, 'orbital': 0.0},
        'table': {'vertical': 0.0, 'trend': 0.0, 'tilt': 0.0, 'longitudinal': 0.0, 'transverse': 0.0}
    }
}

# Get scenario from command line or use default
if len(sys.argv) > 1:
    scenario_key = sys.argv[1]
else:
    scenario_key = "pa"

if scenario_key not in scenarios:
    print(f"Unknown scenario: {scenario_key}")
    print(f"Available scenarios: {', '.join(scenarios.keys())}")
    sys.exit(1)

scenario = scenarios[scenario_key]

print(f"\n{'='*70}")
print(f"Visualizing: {scenario['name']}")
print(f"{'='*70}\n")

# Initialize detector
detector = CollisionDetector()

# Check collision
has_collision = detector.check_collision(scenario['c_arm'], scenario['table'])
details = detector.get_collision_details()

# Print results
print(f"Status: {'COLLISION DETECTED' if has_collision else 'SAFE'}")
if has_collision:
    print(f"Total Collision Points: {details['total_points']}")
    print(f"  - Table Top: {details['table_top']}")
    print(f"  - Table Body: {details['table_body']}")
    print(f"  - Table Base: {details['table_base']}")

# Get transformed geometries
c_arm_transformed = detector.c_arm_pc.clone()
c_arm_transformed.apply_transform(T=detector.c_arm_pose)

table_top_transformed = detector.table_top_mesh.clone()
table_top_transformed.apply_transform(T=detector.table_top_pose)

table_body_transformed = detector.table_body_mesh.clone()
table_body_transformed.apply_transform(T=detector.transf_c_arm_base_to_table_body)

table_base_transformed = detector.table_wheels_base_mesh.clone()
table_base_transformed.apply_transform(T=detector.transf_c_arm_base_to_table_wheels_base)

# Color based on collision
if has_collision:
    # Red for collision
    table_top_transformed.c(color=(1, 0, 0), alpha=0.7)
    table_body_transformed.c(color=(1, 0, 0), alpha=0.7)
    table_base_transformed.c(color=(1, 0, 0), alpha=0.7)
    
    # Highlight collision points in yellow
    collision_points_list = []
    if details['table_top'] > 0:
        table_top_collision = table_top_transformed.inside_points(c_arm_transformed.points())
        collision_points_list.append(table_top_collision.points())
    if details['table_body'] > 0:
        table_body_collision = table_body_transformed.inside_points(c_arm_transformed.points())
        collision_points_list.append(table_body_collision.points())
    if details['table_base'] > 0:
        table_base_collision = table_base_transformed.inside_points(c_arm_transformed.points())
        collision_points_list.append(table_base_collision.points())
    
    if collision_points_list:
        all_collision_pts = np.vstack(collision_points_list)
        collision_pc = vedo.Points(all_collision_pts, r=15, c='yellow')
else:
    # Green for safe
    table_top_transformed.c(color=(0, 1, 0), alpha=0.7)
    table_body_transformed.c(color=(0, 1, 0), alpha=0.7)
    table_base_transformed.c(color=(0, 1, 0), alpha=0.7)
    collision_pc = None

# C-arm in blue
c_arm_transformed.c(color=(0, 0, 1), alpha=0.8)

# Create plotter
plt = vedo.Plotter(title=scenario['name'], size=(1400, 900))

# Add objects
actors = [table_top_transformed, table_body_transformed, table_base_transformed, c_arm_transformed]
if collision_pc is not None:
    actors.append(collision_pc)

print(f"\n{'='*70}")
print("Opening 3D visualization window...")
print("Colors: Blue=C-arm, Red=Collision, Green=Safe, Yellow=Collision Points")
print(f"{'='*70}\n")

# Show
plt.show(*actors)
plt.close()

print("\nVisualization closed.")
