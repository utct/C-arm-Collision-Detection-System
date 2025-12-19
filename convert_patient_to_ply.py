"""
Convert patient X3D model to PLY format for collision detection
Applies the internal X3D transformation (rotation="0 1 0 3.1415" scale="1 1 -1")
"""

import xml.etree.ElementTree as ET
import numpy as np

# Parse X3D file
tree = ET.parse('models/patient-model.x3d')
root = tree.getroot()

# Find IndexedFaceSet
for elem in root.iter():
    if 'IndexedFaceSet' in elem.tag:
        coord_index = elem.attrib['coordIndex']
        
    if 'Coordinate' in elem.tag:
        points_str = elem.attrib['point']

# Parse coordinate points
points = []
for coord_str in points_str.split():
    try:
        points.append(float(coord_str))
    except:
        pass

# Reshape to Nx3
vertices = np.array(points).reshape(-1, 3)
print(f"Loaded {len(vertices)} vertices")

# Apply transformations to make patient lie on table
# 1. First apply internal X3D rotation: 180° around Y-axis
# Rotation matrix for 180° around Y: [[-1, 0, 0], [0, 1, 0], [0, 0, -1]]
rot_y_180 = np.array([[-1, 0, 0], [0, 1, 0], [0, 0, -1]])
vertices = vertices @ rot_y_180.T

# 2. Apply internal scale from X3D: (1, 1, -1)
vertices[:, 2] *= -1

# 3. Flip upside down (rotate 180° around X-axis)
# Rotation matrix for 180° around X: [[1, 0, 0], [0, -1, 0], [0, 0, -1]]
rot_x_180 = np.array([[1, 0, 0], [0, -1, 0], [0, 0, -1]])
vertices = vertices @ rot_x_180.T

# 4. Rotate 90° around X-axis to lay down
# Rotation matrix for 90° around X: [[1, 0, 0], [0, 0, -1], [0, 1, 0]]
rot_x_90 = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])
vertices = vertices @ rot_x_90.T

print(f"Applied transformations: 180°Y -> scale -> 180°X -> 90°X")

# Apply internal X3D transformation: rotation="0 1 0 3.1415" (180° around Y) scale="1 1 -1"
# 180° rotation around Y-axis: x' = -x, y' = y, z' = -z
# Combined with scale (1, 1, -1): z gets another flip
# Removed X flip to match H3D orientation
transform_matrix = np.array([
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, 1]
])
vertices = vertices @ transform_matrix.T
print(f"Applied internal X3D transformation (no X flip to match H3D)")

# Parse face indices
faces = []
current_face = []
for idx_str in coord_index.split():
    if idx_str == '-1':
        if len(current_face) == 3:  # Only triangles
            faces.append(current_face)
        current_face = []
    else:
        current_face.append(int(idx_str))

print(f"Loaded {len(faces)} triangular faces")

# Write PLY file
with open('models/patient_model.ply', 'w') as f:
    f.write('ply\n')
    f.write('format ascii 1.0\n')
    f.write(f'element vertex {len(vertices)}\n')
    f.write('property float x\n')
    f.write('property float y\n')
    f.write('property float z\n')
    f.write(f'element face {len(faces)}\n')
    f.write('property list uchar int vertex_indices\n')
    f.write('end_header\n')
    
    # Write vertices
    for v in vertices:
        f.write(f'{v[0]} {v[1]} {v[2]}\n')
    
    # Write faces
    for face in faces:
        f.write(f'3 {face[0]} {face[1]} {face[2]}\n')

print("\nSuccessfully saved to models/patient_model.ply")
