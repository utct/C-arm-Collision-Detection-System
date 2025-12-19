# EARLY IMPLEMENTATION FOR CONVERTING NII TO NRRD
# THIS FILE IS NOT USED IN THE PROJECT AND IS DEPRECATED

#!/usr/bin/env python3
"""
Proper NIfTI to NRRD Converter using pynrrd library
This ensures correct NRRD format for H3D MedX3D
"""

import os
import sys
import numpy as np
import nibabel as nib
import nrrd
import argparse

def convert_nii_to_nrrd_proper(nii_path, output_path=None):
    """
    Convert a NIfTI file to NRRD format using proper pynrrd library
    """
    
    if not os.path.exists(nii_path):
        print(f"Error: File not found: {nii_path}")
        return False
    
    # Load the NIfTI file
    print(f"Loading: {nii_path}")
    nii_img = nib.load(nii_path)
    nii_data = nii_img.get_fdata()
    
    print(f"Original data shape: {nii_data.shape}")
    print(f"Original data range: {np.min(nii_data):.2f} to {np.max(nii_data):.2f}")
    print(f"Original data type: {nii_data.dtype}")
    
    # Get voxel spacing from NIfTI header
    header = nii_img.header
    spacing = header.get_zooms()[:3]  # Get x, y, z spacing
    print(f"Voxel spacing: {spacing}")
    
    # Set output path
    if output_path is None:
        base_name = os.path.splitext(nii_path)[0]
        output_path = base_name + "_proper.nrrd"
    
    # Prepare data for NRRD
    # Keep the original data type and range 
    if nii_data.dtype == np.float64 or nii_data.dtype == np.float32:
        # Convert float to appropriate integer format
        data_min = np.min(nii_data)
        data_max = np.max(nii_data)
        
        if data_max <= 255:
            # Can fit in uint8
            nrrd_data = nii_data.astype(np.uint8)
            data_type = 'uint8'
        elif data_max <= 65535:
            # Can fit in uint16
            nrrd_data = nii_data.astype(np.uint16)
            data_type = 'uint16'
        else:
            # Keep as float32
            nrrd_data = nii_data.astype(np.float32)
            data_type = 'float32'
    else:
        nrrd_data = nii_data
        data_type = str(nii_data.dtype)
    
    print(f"NRRD data shape: {nrrd_data.shape}")
    print(f"NRRD data range: {np.min(nrrd_data):.2f} to {np.max(nrrd_data):.2f}")
    print(f"NRRD data type: {data_type}")
    
    # Create NRRD header with proper spacing information
    header_dict = {
        'type': data_type,
        'dimension': 3,
        'sizes': nrrd_data.shape,
        'spacings': list(spacing),
        'encoding': 'raw',
        'endian': 'little'
    }
    
    # Write NRRD file using pynrrd
    try:
        nrrd.write(output_path, nrrd_data, header=header_dict)
        print(f"Successfully wrote: {output_path}")
        
        # Verify the file by reading it back
        verify_data, verify_header = nrrd.read(output_path)
        print(f"Verification - Shape: {verify_data.shape}, Type: {verify_data.dtype}")
        print(f"Verification - Range: {np.min(verify_data):.2f} to {np.max(verify_data):.2f}")
        
        return True
        
    except Exception as e:
        print(f"Error writing NRRD file: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Convert NIfTI files to proper NRRD format for H3D')
    parser.add_argument('input', help='Input .nii file or directory containing .nii files')
    parser.add_argument('-o', '--output', help='Output directory')
    
    args = parser.parse_args()
    
    input_path = args.input
    output_dir = args.output
    
    if os.path.isfile(input_path):
        # Single file
        if output_dir:
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_path = os.path.join(output_dir, base_name + "_proper.nrrd")
        else:
            output_path = None
        convert_nii_to_nrrd_proper(input_path, output_path)
    elif os.path.isdir(input_path):
        # Directory - process all .nii files
        nii_files = [f for f in os.listdir(input_path) if f.endswith('.nii')]
        
        if not nii_files:
            print(f"No .nii files found in {input_path}")
            return
        
        print(f"Found {len(nii_files)} .nii files")
        
        for nii_file in nii_files:
            nii_path = os.path.join(input_path, nii_file)
            
            if output_dir:
                base_name = os.path.splitext(nii_file)[0]
                output_path = os.path.join(output_dir, base_name + "_proper.nrrd")
            else:
                output_path = None
                
            print(f"\n{'='*50}")
            convert_nii_to_nrrd_proper(nii_path, output_path)
    else:
        print(f"Error: {input_path} is not a valid file or directory")

if __name__ == "__main__":
    main()