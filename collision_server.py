"""
Collision Detection Server (Python 3)
Uses point cloud + mesh intersection (research paper method)
Communicates with H3D via JSON files
"""

import numpy as np
import vedo
import json
import time
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))
from TransformationMats import calc_transf_mat_c_arm_base_to_ee, calc_transf_mat_table_base_to_ee


class CollisionServer:
    def __init__(self):
        print("=" * 70)
        print("COLLISION DETECTION SERVER")
        print("=" * 70)
        
        self._load_models()
        self.check_count = 0
        self.transf_c_arm_base_to_table_base = self._get_table_base_transform()
        
        print("\n" + "=" * 70)
        print("SERVER READY - Waiting for collision check requests")
        print("=" * 70 + "\n")
    
    def _load_models(self):
        """Load all 3D models and meshes"""
        print("\n[1/5] Loading C-arm point cloud...")
        self.c_arm_pc = vedo.Points(np.load('3d_inputs/c_arm_pcd_pts.npy'))
        print(f"        Loaded {self.c_arm_pc.points().shape[0]} points")
        
        print("\n[2/5] Loading table top mesh...")
        self.table_top_mesh = vedo.load('3d_inputs/table_top_watertight_mesh.ply')
        print(f"        Loaded {self.table_top_mesh.npoints} vertices")
        
        print("\n[3/5] Loading table body mesh...")
        self.table_body_mesh = vedo.load('3d_inputs/table_body_sphere_watertight_mesh.ply')
        print(f"        Loaded {self.table_body_mesh.npoints} vertices")
        
        print("\n[4/5] Loading table wheels mesh...")
        self.table_wheels_base_mesh = vedo.load('3d_inputs/table_wheels_base_watertight_mesh.ply')
        print(f"        Loaded {self.table_wheels_base_mesh.npoints} vertices")
        
        print("\n[5/5] Loading patient model...")
        self.patient_mesh = vedo.load('models/patient_model.ply')
        print(f"        Loaded {self.patient_mesh.npoints} vertices")
    
    def _get_table_base_transform(self):
        """Get transformation from C-arm base to table base"""
        transform = np.eye(4)
        transform[0, 3] = 0.4
        transform[1, 3] = 1.35
        return transform
    
    def check_collision(self, lao_rao_deg, cran_caud_deg, wigwag_deg=0, 
                        lateral_m=0, vertical_m=0, horizontal_m=0,
                        table_vertical_m=0, table_longitudinal_m=0, table_transverse_m=0):
        """Check collision using DH transformations for 9 DOF (6 C-arm + 3 table)"""
        self.check_count += 1
        
        # Calculate C-arm pose using DH transformation WITHOUT wigwag
        # Wigwag will be applied as rotation around origin
        c_arm_pose = calc_transf_mat_c_arm_base_to_ee(
            horizontal_m, vertical_m, 0,  # wigwag=0 in DH chain
            lateral_m, cran_caud_deg, lao_rao_deg
        )
        
        # Apply wigwag as pure rotation to orientation only (no position change)
        if abs(wigwag_deg) > 0.01:
            wigwag_rad = np.radians(wigwag_deg)
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
        c_arm_pc_cpy = self.c_arm_pc.clone()
        c_arm_pc_cpy.apply_transform(T=c_arm_pose, reset=False, concatenate=False)
        
        # Calculate table poses based on current DOF
        # Table top uses full DH transformation (no trend/tilt yet)
        transf_table_base_to_ee = calc_transf_mat_table_base_to_ee(
            table_vertical_m, 0.0, 0.0,  # vertical, trend=0, tilt=0
            table_longitudinal_m, table_transverse_m
        )
        table_top_pose = self.transf_c_arm_base_to_table_base @ transf_table_base_to_ee
        
        # Table body pose (extends upward with vertical movement)
        # Z-axis is vertical in world frame (after 90° Y rotation)
        transf_c_arm_base_to_table_body = np.eye(4)
        transf_c_arm_base_to_table_body[0, 3] = 0.4
        transf_c_arm_base_to_table_body[1, 3] = 1.35
        transf_c_arm_base_to_table_body[2, 3] = table_vertical_m  # Extends upward in Z
        
        # Table wheels base pose (stays on ground - does NOT move vertically)
        transf_c_arm_base_to_table_wheels_base = np.eye(4)
        transf_c_arm_base_to_table_wheels_base[0, 3] = 0.4 - 0.15
        transf_c_arm_base_to_table_wheels_base[1, 3] = 1.35  # Fixed height
        transf_c_arm_base_to_table_wheels_base[2, 3] = 0.0  # Fixed Z
        
        # Transform table meshes (using copies)
        table_top_mesh_cpy = self.table_top_mesh.clone()
        table_top_mesh_cpy.apply_transform(T=table_top_pose, reset=False, concatenate=False)
        
        table_body_mesh_cpy = self.table_body_mesh.clone()
        table_body_mesh_cpy.apply_transform(T=transf_c_arm_base_to_table_body, reset=False, concatenate=False)
        
        table_wheels_base_mesh_cpy = self.table_wheels_base_mesh.clone()
        table_wheels_base_mesh_cpy.apply_transform(T=transf_c_arm_base_to_table_wheels_base, reset=False, concatenate=False)
        
        # Transform patient mesh (external transform from main.x3d only)
        # Internal X3D transform is already baked into the PLY file
        patient_mesh_cpy = self.patient_mesh.clone()
        
        # External transform from main.x3d: translation='0.22 -0.15 -0.2' scale="-1.35 1.35 -1.35"
        # Plus 90-degree rotation around Z-axis to align with table
        patient_transform = np.eye(4)
        
        # Apply 270-degree Z rotation (to flip head/feet orientation)
        cos_z = np.cos(3 * np.pi / 2)
        sin_z = np.sin(3 * np.pi / 2)
        patient_transform[0, 0] = cos_z
        patient_transform[0, 1] = -sin_z
        patient_transform[1, 0] = sin_z
        patient_transform[1, 1] = cos_z
        
        # Apply translation
        patient_transform[0, 3] = 0.3  # X translation
        patient_transform[1, 3] = 1.35   # left right
        patient_transform[2, 3] = 0.8   # up
        
        # Apply scale (need to combine with rotation) - matches visualizer
        scale_transform = np.eye(4)
        scale_transform[0, 0] = -1.0  # X scale
        scale_transform[1, 1] = 1.0   # Y scale
        scale_transform[2, 2] = -1.0  # Z scale
        
        patient_transform = patient_transform @ scale_transform
        
        patient_mesh_cpy.apply_transform(T=patient_transform, reset=False, concatenate=False)
        
        # Check for collision (C-arm points inside table meshes + patient)
        table_top_collision_pcd = table_top_mesh_cpy.inside_points(c_arm_pc_cpy.points(), return_ids=False)
        table_body_collision_pcd = table_body_mesh_cpy.inside_points(c_arm_pc_cpy.points(), return_ids=False)
        table_base_collision_pcd = table_wheels_base_mesh_cpy.inside_points(c_arm_pc_cpy.points(), return_ids=False)
        patient_collision_pcd = patient_mesh_cpy.inside_points(c_arm_pc_cpy.points(), return_ids=False)
        
        # Count collision points
        top_count = table_top_collision_pcd.points().shape[0]
        body_count = table_body_collision_pcd.points().shape[0]
        base_count = table_base_collision_pcd.points().shape[0]
        patient_count = patient_collision_pcd.points().shape[0]
        total_count = top_count + body_count + base_count + patient_count
        
        has_collision = total_count > 0
        
        result = {
            'collision': has_collision,
            'collision_points': {
                'table_top': int(top_count),
                'table_body': int(body_count),
                'table_base': int(base_count),
                'patient': int(patient_count),
                'total': int(total_count)
            },
            'pose': {
                'lao_rao': lao_rao_deg,
                'cran_caud': cran_caud_deg,
                'wigwag': wigwag_deg,
                'lateral': lateral_m,
                'vertical': vertical_m,
                'horizontal': horizontal_m,
                'table_vertical': table_vertical_m,
                'table_longitudinal': table_longitudinal_m,
                'table_transverse': table_transverse_m
            },
            'check_count': self.check_count
        }
        
        # Print status
        status = "COLLISION" if has_collision else "SAFE"
        print(f"[Check #{self.check_count}] C-arm: ORB={lao_rao_deg:5.1f}° TILT={cran_caud_deg:5.1f}° " +
              f"WIG={wigwag_deg:5.1f}° LAT={lateral_m:5.2f}m VER={vertical_m:5.2f}m HOR={horizontal_m:5.2f}m | " +
              f"Table: V={table_vertical_m:5.2f}m L={table_longitudinal_m:5.2f}m T={table_transverse_m:5.2f}m → " +
              f"{status:9s} (pts: {total_count})")
        
        return result
    
    def run_server(self, pose_file='collision_pose.json', result_file='collision_result.json'):
        """
        Run server loop: read pose file, check collision, write result file
        """
        print(f"Monitoring: {pose_file}")
        print(f"Writing to: {result_file}\n")
        
        last_check_time = 0
        check_interval = 0.1  # Check every 100ms
        
        try:
            while True:
                time.sleep(check_interval)
                
                # Check if pose file exists and was recently modified
                pose_path = Path(pose_file)
                if not pose_path.exists():
                    continue
                
                mod_time = pose_path.stat().st_mtime
                if mod_time <= last_check_time:
                    continue
                
                last_check_time = mod_time
                
                # Read pose
                try:
                    with open(pose_file, 'r') as f:
                        pose_data = json.load(f)
                    
                    # Extract all 6 C-arm DOF
                    lao_rao = pose_data.get('lao_rao', 0.0)
                    cran_caud = pose_data.get('cran_caud', 0.0)
                    wigwag = pose_data.get('wigwag', 0.0)
                    lateral = pose_data.get('lateral', 0.0)
                    vertical = pose_data.get('vertical', 0.0)
                    horizontal = pose_data.get('horizontal', 0.0)
                    
                    # Extract table 3 DOF (optional, defaults to 0)
                    table_vertical = pose_data.get('table_vertical', 0.0)
                    table_longitudinal = pose_data.get('table_longitudinal', 0.0)
                    table_transverse = pose_data.get('table_transverse', 0.0)
                    
                    # Check collision
                    result = self.check_collision(
                        lao_rao, cran_caud, wigwag,
                        lateral, vertical, horizontal,
                        table_vertical, table_longitudinal, table_transverse
                    )
                    
                    # Write result
                    with open(result_file, 'w') as f:
                        json.dump(result, f, indent=2)
                
                except Exception as e:
                    print(f"ERROR processing request: {e}")
                    continue
        
        except KeyboardInterrupt:
            print("\n\nServer stopped by user.")
            print(f"Total collision checks performed: {self.check_count}")
            print("=" * 70)

def main():
    """Main entry point"""
    # Initialize server
    try:
        server = CollisionServer()
    except Exception as e:
        print(f"\nERROR: Failed to initialize server: {e}")
        print("\nMake sure you have installed required packages:")
        print("  pip install numpy vedo")
        print("\nAnd that 3D mesh files exist in 3d_inputs/ directory")
        sys.exit(1)
    
    # Run server loop
    server.run_server()

if __name__ == '__main__':
    main()
