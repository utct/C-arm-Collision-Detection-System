"""
Collision Visualization using Vedo
Shows C-arm point cloud, table meshes, and patient model
Press SPACEBAR to update from collision_pose.json
"""

import numpy as np
import vedo
import json
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))
from TransformationMats import calc_transf_mat_c_arm_base_to_ee

class SimpleCollisionVisualizer:
    def __init__(self):
        print("=" * 70)
        print("COLLISION VISUALIZER")
        print("=" * 70)
        
        self._load_models()
        self.check_count = 0
        self.last_mod_time = 0
        
        print("\n" + "=" * 70)
        print("VISUALIZER READY")
        print("=" * 70)
        print("\nPress SPACEBAR in the vedo window to update")
        print("Or close the window to exit")
        print("=" * 70 + "\n")
    
    def _load_models(self):
        """Load all 3D models and meshes"""
        print("\n[1/5] Loading C-arm point cloud...")
        c_arm_pts = np.load('3d_inputs/c_arm_pcd_pts.npy')
        self.c_arm_pc = vedo.Points(c_arm_pts).color('cyan').point_size(3)
        print(f"        Loaded {c_arm_pts.shape[0]} points")
        
        print("\n[2/5] Loading table top mesh...")
        self.table_top_mesh = vedo.load('3d_inputs/table_top_watertight_mesh.ply')
        self.table_top_mesh.color('orange').alpha(0.8)
        print(f"        Loaded {self.table_top_mesh.npoints} vertices")
        
        print("\n[3/5] Loading table body mesh...")
        self.table_body_mesh = vedo.load('3d_inputs/table_body_sphere_watertight_mesh.ply')
        self.table_body_mesh.color('red').alpha(0.7)
        print(f"        Loaded {self.table_body_mesh.npoints} vertices")
        
        print("\n[4/5] Loading table wheels mesh...")
        self.table_wheels_base_mesh = vedo.load('3d_inputs/table_wheels_base_watertight_mesh.ply')
        self.table_wheels_base_mesh.color('darkgray').alpha(0.8)
        print(f"        Loaded {self.table_wheels_base_mesh.npoints} vertices")
        
        print("\n[5/5] Loading patient model...")
        self.patient_mesh = vedo.load('models/patient_model.ply')
        self.patient_mesh.color('beige').alpha(0.9)
        print(f"        Loaded {self.patient_mesh.npoints} vertices")
    
    def update_from_file(self):
        """Read pose from file and return updated C-arm"""
        pose_file = 'collision_pose.json'
        pose_path = Path(pose_file)
        
        if not pose_path.exists():
            return None
        
        mod_time = pose_path.stat().st_mtime
        if mod_time <= self.last_mod_time:
            return None  # No update
        
        self.last_mod_time = mod_time
        
        try:
            with open(pose_file, 'r') as f:
                pose_data = json.load(f)
            
            # Get C-arm pose in the format H3D uses (degrees for angles)
            lao_rao = pose_data.get('lao_rao', 0.0)  # Already in degrees
            cran_caud = pose_data.get('cran_caud', 0.0)  # Already in degrees
            wigwag = pose_data.get('wigwag', 0.0)  # Already in degrees
            lateral = pose_data.get('lateral', 0.0)
            vertical = pose_data.get('vertical', 0.0)
            horizontal = pose_data.get('horizontal', 0.0)
            
            # Get table pose (optional, defaults to 0)
            table_vertical = pose_data.get('table_vertical', 0.0)
            table_longitudinal = pose_data.get('table_longitudinal', 0.0)
            table_transverse = pose_data.get('table_transverse', 0.0)
            
            # Calculate C-arm pose WITHOUT wigwag in DH chain
            # Swap horizontal/lateral to match H3D coordinate system
            c_arm_pose = calc_transf_mat_c_arm_base_to_ee(
                horizontal, vertical, 0,  # wigwag=0 in DH chain
                lateral, cran_caud, lao_rao
            )
            
            # Apply wigwag as pure rotation to orientation only (no position change)
            if abs(wigwag) > 0.01:
                wigwag_rad = np.radians(wigwag)
                cos_w = np.cos(wigwag_rad)
                sin_w = np.sin(wigwag_rad)
                
                rot_z = np.array([
                    [cos_w, -sin_w, 0, 0],
                    [sin_w, cos_w, 0, 0],
                    [0, 0, 1, 0],
                    [0, 0, 0, 1]
                ])
                
                # Apply rotation to orientation only (no position change)
                c_arm_pose[:3, :3] = rot_z[:3, :3] @ c_arm_pose[:3, :3]
            
            # Transform C-arm point cloud
            c_arm_transformed = self.c_arm_pc.clone()
            c_arm_transformed.apply_transform(c_arm_pose)
            
            # Calculate table poses based on current DOF
            from TransformationMats import calc_transf_mat_table_base_to_ee
            transf_table_base_to_ee = calc_transf_mat_table_base_to_ee(
                table_vertical, 0.0, 0.0,  # vertical, trend=0, tilt=0
                table_longitudinal, table_transverse
            )
            
            transf_c_arm_base_to_table_base = np.eye(4)
            transf_c_arm_base_to_table_base[0, 3] = 0.4
            transf_c_arm_base_to_table_base[1, 3] = 1.35  # Closer to match main.x3d
            
            table_top_pose = transf_c_arm_base_to_table_base @ transf_table_base_to_ee
            
            # Table body pose (extends upward with vertical movement)
            # Z-axis is vertical in world frame (after 90° Y rotation)
            transf_c_arm_base_to_table_body = np.eye(4)
            transf_c_arm_base_to_table_body[0, 3] = 0.4
            transf_c_arm_base_to_table_body[1, 3] = 1.35
            transf_c_arm_base_to_table_body[2, 3] = table_vertical  # Extends upward in Z
            
            # Table wheels base pose (stays on ground - does NOT move vertically)
            transf_c_arm_base_to_table_wheels_base = np.eye(4)
            transf_c_arm_base_to_table_wheels_base[0, 3] = 0.4 - 0.15
            transf_c_arm_base_to_table_wheels_base[1, 3] = 1.35  # Fixed height
            transf_c_arm_base_to_table_wheels_base[2, 3] = 0.0  # Fixed Z
            
            # Transform table meshes (create copies for display)
            table_top_transformed = self.table_top_mesh.clone()
            table_top_transformed.apply_transform(table_top_pose)
            
            table_body_transformed = self.table_body_mesh.clone()
            table_body_transformed.apply_transform(transf_c_arm_base_to_table_body)
            
            table_wheels_transformed = self.table_wheels_base_mesh.clone()
            table_wheels_transformed.apply_transform(transf_c_arm_base_to_table_wheels_base)
            
            # Transform patient mesh - ORIGINAL placement + table movement
            patient_transformed = self.patient_mesh.clone()
            
            # Original working transform (patient lying on table)
            patient_transform = np.eye(4)
            
            # Apply 270-degree Z rotation (to flip head/feet orientation)
            cos_z = np.cos(3 * np.pi / 2)
            sin_z = np.sin(3 * np.pi / 2)
            patient_transform[0, 0] = cos_z
            patient_transform[0, 1] = -sin_z
            patient_transform[1, 0] = sin_z
            patient_transform[1, 1] = cos_z
            
            # Base position (original working values)
            patient_transform[0, 3] = 0.3   # X translation
            patient_transform[1, 3] = 1.35  # Y (left/right)
            patient_transform[2, 3] = 0.8   # Z (up)
            
            # Add table movement offsets (negate longitudinal/transverse to match table direction)
            patient_transform[2, 3] += table_vertical       # Move up/down with table
            patient_transform[0, 3] -= table_longitudinal   # Move along table (negated)
            patient_transform[1, 3] -= table_transverse     # Move across table (negated)
            
            # Apply scale
            scale_transform = np.eye(4)
            scale_transform[0, 0] = -1.0
            scale_transform[1, 1] = 1.0
            scale_transform[2, 2] = -1.0
            
            patient_transform = patient_transform @ scale_transform
            
            patient_transformed.apply_transform(patient_transform)
            
            # Check collision using transformed meshes
            has_collision, collision_count, collision_points = self.check_collision_with_meshes(
                c_arm_transformed.points(),
                table_top_transformed,
                table_body_transformed,
                table_wheels_transformed,
                patient_transformed
            )
            
            # Update C-arm color based on collision
            if has_collision:
                # Color all points cyan first
                c_arm_transformed.color('cyan').point_size(3)
                # Create red points for colliding points only
                collision_point_cloud = vedo.Points(collision_points).color('red').point_size(8)
                status = f"[COLLISION] {collision_count} points"
            else:
                c_arm_transformed.color('cyan').point_size(3)
                collision_point_cloud = None
                status = f"[SAFE]"
            
            # Print status to console
            self.check_count += 1
            print(f"[Check #{self.check_count}] C-arm: ORB={lao_rao:.1f}° TILT={cran_caud:.1f}° WIG={wigwag:.1f}° "
                  f"LAT={lateral:.2f}m VER={vertical:.2f}m HOR={horizontal:.2f}m | "
                  f"Table: V={table_vertical:.2f}m L={table_longitudinal:.2f}m T={table_transverse:.2f}m → {status}")
            
            return c_arm_transformed, collision_point_cloud, table_top_transformed, table_body_transformed, table_wheels_transformed, patient_transformed
            
        except Exception as e:
            print(f"[ERROR] {e}")
            return None
    
    def check_collision_with_meshes(self, c_arm_points, table_top_mesh, table_body_mesh, table_wheels_mesh, patient_mesh):
        """Check collision between C-arm points and table meshes + patient"""
        c_arm_vedo = vedo.Points(c_arm_points)
        table_top_collision_pcd = table_top_mesh.inside_points(c_arm_vedo, return_ids=False)
        table_body_collision_pcd = table_body_mesh.inside_points(c_arm_vedo, return_ids=False)
        table_base_collision_pcd = table_wheels_mesh.inside_points(c_arm_vedo, return_ids=False)
        patient_collision_pcd = patient_mesh.inside_points(c_arm_vedo, return_ids=False)
        
        # Collect all collision points
        all_collision_points = []
        if table_top_collision_pcd.points().shape[0] > 0:
            all_collision_points.append(table_top_collision_pcd.points())
        if table_body_collision_pcd.points().shape[0] > 0:
            all_collision_points.append(table_body_collision_pcd.points())
        if table_base_collision_pcd.points().shape[0] > 0:
            all_collision_points.append(table_base_collision_pcd.points())
        if patient_collision_pcd.points().shape[0] > 0:
            all_collision_points.append(patient_collision_pcd.points())
        
        if all_collision_points:
            collision_points = np.vstack(all_collision_points)
            total_count = collision_points.shape[0]
        else:
            collision_points = np.empty((0, 3))
            total_count = 0
        
        return total_count > 0, total_count, collision_points
    
    def run(self):
        """Run the visualizer with manual key press updates"""
        # Create plotter with Helvetica font
        vedo.settings.default_font = 'Helvetica'
        plt = vedo.Plotter(title="Collision Visualizer - Press SPACEBAR to update", 
                          bg='white')
        
        # Start with default table positions
        table_top_display = self.table_top_mesh.clone()
        table_body_display = self.table_body_mesh.clone()
        table_wheels_display = self.table_wheels_base_mesh.clone()
        
        # Apply default transformations
        transf_c_arm_base_to_table_base = np.eye(4)
        transf_c_arm_base_to_table_base[0, 3] = 0.4
        transf_c_arm_base_to_table_base[1, 3] = 1.35  # Closer to match main.x3d
        
        from TransformationMats import calc_transf_mat_table_base_to_ee
        transf_table_base_to_ee = calc_transf_mat_table_base_to_ee(0, 0, 0, 0, 0)
        table_top_pose = transf_c_arm_base_to_table_base @ transf_table_base_to_ee
        
        table_top_display.apply_transform(table_top_pose)
        
        transf_body = np.eye(4)
        transf_body[0, 3] = 0.4
        transf_body[1, 3] = 1.35
        table_body_display.apply_transform(transf_body)
        
        transf_wheels = np.eye(4)
        transf_wheels[0, 3] = 0.25
        transf_wheels[1, 3] = 1.35
        table_wheels_display.apply_transform(transf_wheels)
        
        # Add initial table meshes
        plt.add(table_top_display)
        plt.add(table_body_display)
        plt.add(table_wheels_display)
        
        # Add patient mesh - original working placement
        patient_display = self.patient_mesh.clone()
        
        patient_transform = np.eye(4)
        
        # Apply 270-degree Z rotation (to flip head/feet orientation)
        cos_z = np.cos(3 * np.pi / 2)
        sin_z = np.sin(3 * np.pi / 2)
        patient_transform[0, 0] = cos_z
        patient_transform[0, 1] = -sin_z
        patient_transform[1, 0] = sin_z
        patient_transform[1, 1] = cos_z
        
        # Apply translation
        patient_transform[0, 3] = 0.3   # X translation
        patient_transform[1, 3] = 1.35  # left right
        patient_transform[2, 3] = 0.8   # up
        
        # Apply scale
        scale_transform = np.eye(4)
        scale_transform[0, 0] = -1.0
        scale_transform[1, 1] = 1.0
        scale_transform[2, 2] = -1.0
        
        patient_transform = patient_transform @ scale_transform
        
        patient_display.apply_transform(patient_transform)
        plt.add(patient_display)
        
        # Don't add C-arm initially - wait for first pose update
        c_arm_display = None
        collision_display = None
        
        def update_callback(evt):
            """Called when spacebar is pressed"""
            nonlocal c_arm_display, collision_display, table_top_display, table_body_display, table_wheels_display, patient_display
            
            if evt.keypress == 'space':
                result = self.update_from_file()
                if result is not None:
                    new_c_arm, new_collision, new_table_top, new_table_body, new_table_wheels, new_patient = result
                    
                    # Remove old meshes
                    if c_arm_display is not None:
                        plt.remove(c_arm_display)
                    if collision_display is not None:
                        plt.remove(collision_display)
                    plt.remove(table_top_display)
                    plt.remove(table_body_display)
                    plt.remove(table_wheels_display)
                    plt.remove(patient_display)
                    
                    # Add new meshes
                    c_arm_display = new_c_arm
                    collision_display = new_collision
                    table_top_display = new_table_top
                    table_body_display = new_table_body
                    table_wheels_display = new_table_wheels
                    patient_display = new_patient
                    
                    plt.add(c_arm_display)
                    if collision_display is not None:
                        plt.add(collision_display)
                    plt.add(table_top_display)
                    plt.add(table_body_display)
                    plt.add(table_wheels_display)
                    plt.add(patient_display)
                    plt.render()
        
        # Set up keyboard callback
        plt.add_callback('KeyPress', update_callback)
        
        # Show window
        plt.show(interactive=True)

def main():
    """Main entry point"""
    try:
        visualizer = SimpleCollisionVisualizer()
        visualizer.run()
    except KeyboardInterrupt:
        print("\n\nVisualizer stopped by user.")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
