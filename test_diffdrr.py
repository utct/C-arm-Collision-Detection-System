"""
Test DiffDRR - Generate a sample DRR image
"""

import torch
import numpy as np
from PIL import Image
import time

print("=" * 60)
print("DiffDRR Test - Generating X-ray from CT")
print("=" * 60)

# Import DiffDRR
from diffdrr.drr import DRR
from diffdrr.data import load_example_ct

# Load the example CT (DeepFluoro dataset)
print("\n[1/4] Loading DeepFluoro CT volume...")
subject = load_example_ct()
print(f"      CT volume shape: {subject.volume.shape}")

# Set device (GPU if available)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"\n[2/4] Using device: {device}")
if device.type == "cuda":
    print(f"      GPU: {torch.cuda.get_device_name(0)}")

# Initialize DRR module
print("\n[3/4] Initializing DRR renderer...")
drr = DRR(
    subject,
    sdd=1020.0,    # Source-to-detector distance (mm)
    height=256,    # Image height (smaller for faster CPU rendering)
    delx=2.0,      # Pixel spacing (mm)
).to(device)
print("      DRR module ready!")

# Set camera pose (similar to C-arm at 0 degrees)
print("\n[4/4] Rendering DRR...")
rotations = torch.tensor([[0.0, 0.0, 0.0]], device=device)  # yaw, pitch, roll
translations = torch.tensor([[0.0, 850.0, 0.0]], device=device)  # x, y, z in mm

# Render!
start_time = time.time()
with torch.no_grad():
    img = drr(rotations, translations, parameterization="euler_angles", convention="ZXY")
render_time = (time.time() - start_time) * 1000

print(f"      Rendered in {render_time:.1f}ms")
print(f"      Output shape: {img.shape}")

# Convert to image and save
img_np = img.cpu().numpy()[0, 0]  # [B, C, H, W] -> [H, W]
img_np = (img_np - img_np.min()) / (img_np.max() - img_np.min())  # Normalize to 0-1
img_uint8 = (img_np * 255).astype(np.uint8)

# Save the image
output_path = "test_drr_output.png"
Image.fromarray(img_uint8).save(output_path)
print(f"\n✅ SUCCESS! DRR saved to: {output_path}")

# Also test a different angle (like LAO 30)
print("\n[Bonus] Testing LAO 30° angle...")
rotations_lao = torch.tensor([[30.0, 0.0, 0.0]], device=device)
start_time = time.time()
with torch.no_grad():
    img_lao = drr(rotations_lao, translations, parameterization="euler_angles", convention="ZXY")
render_time = (time.time() - start_time) * 1000
print(f"      Rendered LAO 30° in {render_time:.1f}ms")

img_lao_np = img_lao.cpu().numpy()[0, 0]
img_lao_np = (img_lao_np - img_lao_np.min()) / (img_lao_np.max() - img_lao_np.min())
img_lao_uint8 = (img_lao_np * 255).astype(np.uint8)
Image.fromarray(img_lao_uint8).save("test_drr_lateral.png")
print(f"✅ LAO 30° DRR saved to: test_drr_lateral.png")

print("\n" + "=" * 60)
print("DiffDRR is working! Ready for integration.")
print("=" * 60)
