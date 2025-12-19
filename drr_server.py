"""
DRR Server - Photorealistic X-ray Generation using DiffDRR
Monitors collision_pose.json and generates DRR images with optional segmentation overlay
Communicates with H3D via JSON files and PNG images
"""

import torch
import numpy as np
from PIL import Image
import json
import time
import sys
from pathlib import Path
import colorsys

from diffdrr.drr import DRR
from diffdrr.data import load_example_ct


class DRRServer:
    def __init__(self, height=256, sdd=1020.0, delx=2.0):
        """Initialize DRR server with CT volume and segmentation support"""
        print("=" * 70)
        print("DRR SERVER - Photorealistic X-ray with Segmentation")
        print("=" * 70)
        
        print("\n[1/3] Loading DeepFluoro CT volume with labels...")
        self.subject = load_example_ct()
        print(f"        Volume: {self.subject.volume.shape}")
        print(f"        Mask: {self.subject.mask.shape}")
        print(f"        Structures: {len(self.subject.structures)} anatomical labels")
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"\n[2/3] Using device: {self.device}")
        if self.device.type == "cpu":
            print("        [WARNING] CPU mode - slow rendering (~4s per frame)")
            print("        [TIP] For real-time: use Python 3.11 with CUDA PyTorch")
        
        print("\n[3/3] Initializing DRR renderer...")
        self.drr = DRR(self.subject, sdd=sdd, height=height, delx=delx).to(self.device)
        
        self.height = height
        self.render_count = 0
        self._setup_structure_groups()
        
        print("\n" + "=" * 70)
        print("SERVER READY - Waiting for pose updates")
        print(f"Segmentation categories: {list(self.structure_groups.keys())}")
        print("=" * 70 + "\n")
    
    def _setup_structure_groups(self):
        """Setup structure groups from TotalSegmentator labels"""
        structures = self.subject.structures
        self.structure_groups = {}
        self.structure_colors = {}
        
        for group_name in structures['group'].unique():
            group_df = structures[structures['group'] == group_name]
            self.structure_groups[group_name] = group_df['id'].tolist()
            print(f"        {group_name}: {len(group_df)} structures")
        
        self._generate_colors()
    
    def _generate_colors(self):
        """Generate distinct colors for each structure."""
        # Define base hue ranges for each group
        hue_ranges = {
            'ribs': (0.0, 0.35),           # Red to Green
            'vertebrae': (0.5, 0.65),      # Cyan to Blue
            'organs': (0.25, 0.45),        # Green to Cyan
            'cardiovascular': (0.95, 1.05), # Red/Magenta
            'muscles': (0.85, 0.95),       # Pink/Magenta
            'appendicular skeleton': (0.1, 0.2),  # Orange
        }
        
        self.structure_colors = {}
        
        for group_name, struct_ids in self.structure_groups.items():
            hue_start, hue_end = hue_ranges.get(group_name, (0.0, 1.0))
            
            for i, struct_id in enumerate(struct_ids):
                # Generate color based on position in group
                if len(struct_ids) > 1:
                    hue = hue_start + (i / (len(struct_ids) - 1)) * (hue_end - hue_start)
                else:
                    hue = (hue_start + hue_end) / 2
                
                hue = hue % 1.0  # Wrap around
                rgb = colorsys.hsv_to_rgb(hue, 0.9, 1.0)
                self.structure_colors[struct_id] = tuple(c for c in rgb)
    
    def carm_pose_to_diffdrr(self, lao_rao_deg, cran_caud_deg, wigwag_deg=0,
                              lateral_m=0, vertical_m=0, horizontal_m=0, zoom=1.0):
        """Convert C-arm DOF to DiffDRR camera pose.
        
        Args:
            lao_rao_deg: LAO/RAO angle (Orbital rotation)
            cran_caud_deg: CRAN/CAUD angle (Tilt rotation) - paper range: [-90, 270]
            wigwag_deg: Wigwag rotation
            lateral_m: Lateral translation in meters
            vertical_m: Vertical translation in meters (C-arm height, affects SOD physically)
            horizontal_m: Horizontal translation in meters
            zoom: Magnification factor (0.5 = zoomed out, 1.0 = normal, 2.0 = zoomed in)
        """
        # Apply tilt with scaling for gradual effect
        # Scale factor makes full slider range produce reasonable tilt
        tilt_scaled = float(cran_caud_deg) * 0.05  # 5% of slider value
        
        rotations = torch.tensor([
            [float(lao_rao_deg), tilt_scaled, float(wigwag_deg)]
        ], device=self.device)
        
        # Store tilt for image flip compensation in render functions
        self._current_tilt = tilt_scaled
        
        # Source-to-Isocenter distance (mm)
        # Base distance at which zoom=1.0 gives normal magnification
        base_soi = 850.0
        
        # Vertical DOF: Physically correct - C-arm UP = source farther = zoom OUT
        # vertical_m range: [0, 0.46]m according to the paper
        vertical_offset = float(vertical_m) * 500.0  # 500mm per meter of vertical movement
        
        # Zoom control: Independent magnification (inverse relationship - higher zoom = closer source)
        # zoom range: 0.5 to 2.0 (slider value)
        # At zoom=1.0: normal view, zoom=2.0: source at half distance (2x magnification)
        zoom_factor = 1.0 / max(float(zoom), 0.1)  # Prevent division by zero
        
        # Combined: SOI = (base + vertical_offset) * zoom_factor
        soi = (base_soi + vertical_offset) * zoom_factor
        soi = max(soi, 300.0)  # Minimum distance to prevent extreme zoom
        soi = min(soi, 2000.0)  # Maximum distance
        
        translations = torch.tensor([
            [
                float(lateral_m) * 1000,
                soi,
                float(horizontal_m) * 1000
            ]
        ], device=self.device)
        
        return rotations, translations
    
    def render_drr(self, lao_rao_deg, cran_caud_deg, wigwag_deg=0,
                   lateral_m=0, vertical_m=0, horizontal_m=0, zoom=1.0):
        """Render DRR without segmentation overlay"""
        rotations, translations = self.carm_pose_to_diffdrr(
            lao_rao_deg, cran_caud_deg, wigwag_deg,
            lateral_m, vertical_m, horizontal_m, zoom
        )
        
        with torch.no_grad():
            img = self.drr(
                rotations, translations,
                parameterization="euler_angles",
                convention="ZXY"
            )
        
        img_np = img.cpu().numpy()[0, 0]
        
        # Normalize to 0-255
        img_min, img_max = img_np.min(), img_np.max()
        if img_max > img_min:
            img_np = (img_np - img_min) / (img_max - img_min)
        img_uint8 = (img_np * 255).astype(np.uint8)
        
        # Rotate 90 degrees counter-clockwise to match H3D display orientation
        img_uint8 = np.rot90(img_uint8, k=1)
        
        # Compensate for image flipping at certain tilt angles
        tilt = getattr(self, '_current_tilt', 0)
        if tilt < -5:  # Flip compensation threshold
            img_uint8 = np.flipud(img_uint8)
        
        return img_uint8
    
    def render_with_segmentation(self, lao_rao_deg, cran_caud_deg, wigwag_deg=0,
                                  lateral_m=0, vertical_m=0, horizontal_m=0,
                                  zoom=1.0, active_groups=None):
        """Render DRR with colored anatomical segmentation overlay"""
        rotations, translations = self.carm_pose_to_diffdrr(
            lao_rao_deg, cran_caud_deg, wigwag_deg,
            lateral_m, vertical_m, horizontal_m, zoom
        )
        
        # Render with all structure channels
        with torch.no_grad():
            output = self.drr(
                rotations, translations,
                parameterization="euler_angles",
                convention="ZXY",
                mask_to_channels=True  # Returns [1, num_structures+1, H, W]
            )
        
        output = output.cpu().numpy()[0]  # (num_channels, H, W)
        
        # Channel 0 is the base DRR
        drr_img = output[0]
        drr_img = (drr_img - drr_img.min()) / (drr_img.max() - drr_img.min() + 1e-8)
        drr_img = np.rot90(drr_img, k=1)
        
        # Start with grayscale base
        h, w = drr_img.shape
        result = np.zeros((h, w, 3), dtype=np.float32)
        result[:, :, 0] = drr_img
        result[:, :, 1] = drr_img
        result[:, :, 2] = drr_img
        
        if not active_groups:
            return (np.clip(result * 255, 0, 255)).astype(np.uint8)
        
        # Get structure IDs to overlay
        active_struct_ids = set()
        for group_name in active_groups:
            if group_name in self.structure_groups:
                active_struct_ids.update(self.structure_groups[group_name])
        
        # Overlay each active structure with its color
        for struct_id in active_struct_ids:
            if struct_id >= output.shape[0]:
                continue
            
            # Get projected mask for this structure
            mask = output[struct_id]
            mask = np.rot90(mask, k=1)
            
            # Normalize mask
            if mask.max() > 0:
                mask = mask / mask.max()
            
            # Get color for this structure
            rgb = self.structure_colors.get(struct_id, (1.0, 1.0, 1.0))
            
            # Alpha based on mask intensity
            alpha = np.clip(mask * 0.75, 0, 1)
            threshold = 0.08
            
            # Blend color onto result
            for c in range(3):
                result[:, :, c] = np.where(
                    mask > threshold,
                    (1 - alpha) * result[:, :, c] + alpha * rgb[c],
                    result[:, :, c]
                )
        
        img_uint8 = (np.clip(result * 255, 0, 255)).astype(np.uint8)
        
        # Compensate for image flipping at certain tilt angles
        tilt = getattr(self, '_current_tilt', 0)
        if tilt < -5:  # Flip compensation threshold
            img_uint8 = np.flipud(img_uint8)
        
        return img_uint8
    
    def run_server(self, pose_file='collision_pose.json', 
                   output_file='drr_live.png',
                   seg_file='segmentation_settings.json',
                   check_interval=0.1):
        """Main server loop - monitors pose file and generates DRRs"""
        print(f"Monitoring: {pose_file}")
        print(f"Segmentation: {seg_file}")
        print(f"Output: {output_file}")
        print(f"Check interval: {check_interval}s\n")
        
        last_mod_time = 0
        last_seg_mod_time = 0
        last_pose = None
        active_groups = set()
        
        try:
            while True:
                time.sleep(check_interval)
                
                seg_path = Path(seg_file)
                if seg_path.exists():
                    seg_mod_time = seg_path.stat().st_mtime
                    if seg_mod_time > last_seg_mod_time:
                        last_seg_mod_time = seg_mod_time
                        try:
                            with open(seg_file, 'r') as f:
                                seg_data = json.load(f)
                            active_groups = set(seg_data.get('active', []))
                            print(f"[Segments] {active_groups if active_groups else 'None'}")
                        except:
                            pass
                
                pose_path = Path(pose_file)
                if not pose_path.exists():
                    continue
                
                mod_time = pose_path.stat().st_mtime
                if mod_time <= last_mod_time:
                    continue
                
                last_mod_time = mod_time
                
                try:
                    with open(pose_file, 'r') as f:
                        pose_data = json.load(f)
                except (json.JSONDecodeError, IOError):
                    continue
                
                lao_rao = pose_data.get('lao_rao', 0.0)
                cran_caud = pose_data.get('cran_caud', 0.0)
                wigwag = pose_data.get('wigwag', 0.0)
                lateral = pose_data.get('lateral', 0.0)
                vertical = pose_data.get('vertical', 0.0)
                horizontal = pose_data.get('horizontal', 0.0)
                zoom = pose_data.get('zoom', 1.0)
                
                current_pose = (lao_rao, cran_caud, wigwag, lateral, vertical, 
                               horizontal, zoom, tuple(sorted(active_groups)))
                if current_pose == last_pose:
                    continue
                last_pose = current_pose
                
                self.render_count += 1
                start_time = time.time()
                
                if active_groups:
                    img = self.render_with_segmentation(
                        lao_rao, cran_caud, wigwag,
                        lateral, vertical, horizontal,
                        zoom, active_groups
                    )
                else:
                    img = self.render_drr(
                        lao_rao, cran_caud, wigwag,
                        lateral, vertical, horizontal, zoom
                    )
                
                # Save image
                Image.fromarray(img).save(output_file)
                
                render_time = (time.time() - start_time) * 1000
                
                # Log
                seg_info = f" +{list(active_groups)}" if active_groups else ""
                zoom_info = f" zoom={zoom:.2f}" if zoom != 1.0 else ""
                print(f"[#{self.render_count:04d}] LAO={lao_rao:6.1f}° CRAN={cran_caud:6.1f}° "
                      f"WIG={wigwag:5.1f}°{zoom_info} | {render_time:6.0f}ms{seg_info}")
                
        except KeyboardInterrupt:
            print("\n\nServer stopped.")
            print(f"Total renders: {self.render_count}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='DRR Server for C-arm simulation')
    parser.add_argument('--height', type=int, default=256,
                        help='Output image size (default: 256)')
    parser.add_argument('--sdd', type=float, default=1020.0,
                        help='Source-to-detector distance in mm (default: 1020)')
    parser.add_argument('--interval', type=float, default=0.1,
                        help='Check interval in seconds (default: 0.1)')
    
    args = parser.parse_args()
    
    try:
        server = DRRServer(height=args.height, sdd=args.sdd)
        server.run_server(check_interval=args.interval)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        print("\nMake sure you have installed:")
        print("  pip install diffdrr torch torchvision")
        sys.exit(1)


if __name__ == '__main__':
    main()
