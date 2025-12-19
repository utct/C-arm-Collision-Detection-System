#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Convert X3D mesh to NPY point cloud
Extracts coordinate points from X3D file and saves as numpy array
Applies transformations to match the H3D main.x3d scene
Supports dense surface sampling for better collision detection
"""

import numpy as np
import re
import sys

# Scale factor from main.x3d: <Transform DEF='TCArmTransform' scale='1.35 1.35 1.35'>
H3D_SCALE = 1.35

# Number of points to sample from mesh surface (higher = denser point cloud)
TARGET_POINTS = 15000  # Adjust this for density

def sample_triangle(v0, v1, v2, n_samples):
    """
    Sample random points uniformly on a triangle surface.
    Uses barycentric coordinates for uniform sampling.
    """
    # Generate random barycentric coordinates
    r1 = np.random.random(n_samples)
    r2 = np.random.random(n_samples)
    
    # Ensure points are inside triangle (not in the other half of parallelogram)
    mask = r1 + r2 > 1
    r1[mask] = 1 - r1[mask]
    r2[mask] = 1 - r2[mask]
    
    # Convert to Cartesian coordinates
    # P = (1 - r1 - r2) * v0 + r1 * v1 + r2 * v2
    w0 = 1 - r1 - r2
    points = np.outer(w0, v0) + np.outer(r1, v1) + np.outer(r2, v2)
    
    return points

def triangle_area(v0, v1, v2):
    """Calculate the area of a triangle given its vertices"""
    edge1 = v1 - v0
    edge2 = v2 - v0
    cross = np.cross(edge1, edge2)
    return 0.5 * np.linalg.norm(cross)

def sample_mesh_surface(vertices, faces, n_points):
    """
    Sample points uniformly on a mesh surface.
    
    Args:
        vertices: Nx3 array of vertex positions
        faces: Mx3 array of triangle indices
        n_points: Total number of points to sample
        
    Returns:
        Sampled points as Nx3 array
    """
    # Calculate area of each triangle
    areas = np.zeros(len(faces))
    for i, face in enumerate(faces):
        v0, v1, v2 = vertices[face[0]], vertices[face[1]], vertices[face[2]]
        areas[i] = triangle_area(v0, v1, v2)
    
    total_area = areas.sum()
    if total_area == 0:
        return vertices  # Degenerate mesh, return vertices
    
    # Number of samples per triangle (proportional to area)
    samples_per_tri = np.round(areas / total_area * n_points).astype(int)
    
    # Ensure we get at least n_points total
    while samples_per_tri.sum() < n_points:
        # Add samples to largest triangles
        idx = np.argmax(areas)
        samples_per_tri[idx] += 1
    
    # Sample each triangle
    all_points = []
    for i, face in enumerate(faces):
        if samples_per_tri[i] > 0:
            v0, v1, v2 = vertices[face[0]], vertices[face[1]], vertices[face[2]]
            points = sample_triangle(v0, v1, v2, samples_per_tri[i])
            all_points.append(points)
    
    return np.vstack(all_points)

def extract_points_from_x3d(x3d_file, apply_transforms=True, dense_sampling=True):
    """
    Extract points from an X3D file, optionally with dense surface sampling.
    
    Args:
        x3d_file: Path to the X3D file
        apply_transforms: If True, apply scale to match H3D scene
        dense_sampling: If True, sample mesh surface for denser point cloud
        
    Returns:
        numpy array of shape (N, 3) with all points
    """
    print(f"Reading X3D file: {x3d_file}")
    
    with open(x3d_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all point attributes in Coordinate nodes
    point_pattern = r'<Coordinate[^>]*point="([^"]+)"'
    point_matches = re.findall(point_pattern, content, re.DOTALL)
    
    # Find all IndexedFaceSet coordIndex (face indices)
    face_pattern = r'<IndexedFaceSet[^>]*coordIndex="([^"]+)"'
    face_matches = re.findall(face_pattern, content, re.DOTALL)
    
    all_vertices = []
    all_faces = []
    vertex_offset = 0
    
    for i, point_match in enumerate(point_matches):
        # Parse vertices
        values_str = point_match.strip()
        values = values_str.split()
        
        try:
            float_values = [float(v) for v in values]
        except ValueError as e:
            print(f"  Warning: Could not parse vertices in set {i+1}: {e}")
            continue
        
        # Group into (x, y, z) triplets
        num_verts = len(float_values) // 3
        vertices = []
        for j in range(num_verts):
            vertices.append([float_values[j*3], float_values[j*3+1], float_values[j*3+2]])
        
        print(f"  Mesh {i+1}: {num_verts} vertices", end="")
        
        # Parse faces if available
        if i < len(face_matches):
            face_str = face_matches[i].strip()
            face_indices = face_str.split()
            
            # Parse triangles (indices separated by -1)
            current_face = []
            faces = []
            for idx_str in face_indices:
                idx = int(idx_str)
                if idx == -1:
                    if len(current_face) >= 3:
                        # Triangulate if more than 3 vertices (fan triangulation)
                        for k in range(1, len(current_face) - 1):
                            faces.append([
                                current_face[0] + vertex_offset,
                                current_face[k] + vertex_offset,
                                current_face[k+1] + vertex_offset
                            ])
                    current_face = []
                else:
                    current_face.append(idx)
            
            print(f", {len(faces)} triangles")
            all_faces.extend(faces)
        else:
            print("")
        
        all_vertices.extend(vertices)
        vertex_offset += num_verts
    
    if not all_vertices:
        print("ERROR: No vertices found in the X3D file!")
        return None
    
    vertices_array = np.array(all_vertices, dtype=np.float32)
    
    print(f"\nTotal vertices: {len(vertices_array)}")
    print(f"Total triangles: {len(all_faces)}")
    
    # Either use dense sampling or just vertices
    if dense_sampling and all_faces:
        print(f"\nPerforming dense surface sampling ({TARGET_POINTS} target points)...")
        faces_array = np.array(all_faces, dtype=np.int32)
        sampled_points = sample_mesh_surface(vertices_array, faces_array, TARGET_POINTS)
        print(f"  Sampled {len(sampled_points)} points from mesh surface")
        output_points = sampled_points
    else:
        # Just use unique vertices
        output_points = np.unique(vertices_array, axis=0)
        print(f"Using {len(output_points)} unique vertices")
    
    print(f"\nRaw point cloud bounds:")
    print(f"  X: [{output_points[:, 0].min():.4f}, {output_points[:, 0].max():.4f}]")
    print(f"  Y: [{output_points[:, 1].min():.4f}, {output_points[:, 1].max():.4f}]")
    print(f"  Z: [{output_points[:, 2].min():.4f}, {output_points[:, 2].max():.4f}]")
    
    if apply_transforms:
        print(f"\nApplying scale: {H3D_SCALE}x (from main.x3d TCArmTransform)")
        output_points *= H3D_SCALE
        
        print(f"\nFinal point cloud bounds:")
        print(f"  X: [{output_points[:, 0].min():.4f}, {output_points[:, 0].max():.4f}]")
        print(f"  Y: [{output_points[:, 1].min():.4f}, {output_points[:, 1].max():.4f}]")
        print(f"  Z: [{output_points[:, 2].min():.4f}, {output_points[:, 2].max():.4f}]")
    
    return output_points.astype(np.float32)

def main():
    # Input and output files
    input_file = 'models/carm_c_shape.x3d'
    output_file = '3d_inputs/c_arm_pcd_pts.npy'
    backup_file = '3d_inputs/c_arm_pcd_pts_BACKUP.npy'
    
    print("=" * 60)
    print("X3D to NPY Point Cloud Converter")
    print("=" * 60)
    
    # Backup existing file
    try:
        import shutil
        import os
        if os.path.exists(output_file) and not os.path.exists(backup_file):
            shutil.copy(output_file, backup_file)
            print(f"\nBacked up existing file to: {backup_file}")
    except Exception as e:
        print(f"Warning: Could not backup existing file: {e}")
    
    # Extract points
    points = extract_points_from_x3d(input_file)
    
    if points is None:
        print("\nFailed to extract points!")
        sys.exit(1)
    
    # Save to NPY file
    print(f"\nSaving to: {output_file}")
    np.save(output_file, points)
    
    # Verify the saved file
    loaded = np.load(output_file)
    print(f"Verification: Loaded {loaded.shape[0]} points from saved file")
    
    print("\n" + "=" * 60)
    print("Conversion complete!")
    print("=" * 60)

if __name__ == '__main__':
    main()

