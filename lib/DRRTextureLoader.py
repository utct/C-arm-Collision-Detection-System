"""
DRR Texture Loader - Reloads DRR image from drr_live.png
=========================================================

This script periodically checks if drr_live.png has been updated
and reloads the texture in H3D.

Used in conjunction with drr_server.py for photorealistic X-ray display.
"""

from H3DInterface import *
import os
import time

# Global state
drr_texture = None
last_mod_time = 0
check_interval = 0.5  # Check every 500ms
last_check_time = 0
drr_file_path = "drr_live.png"

def initialize():
    """Initialize the DRR texture loader."""
    global drr_texture
    
    refs = references.getValue()
    if len(refs) >= 1:
        drr_texture = refs[0]
        print("[DRR Loader] Initialized - watching: " + drr_file_path)
        print("[DRR Loader] Make sure drr_server.py is running!")
    else:
        print("[DRR Loader ERROR] No texture reference provided!")

def traverseSG():
    """Called every frame - check if DRR file was updated."""
    global drr_texture, last_mod_time, last_check_time
    
    if drr_texture is None:
        return
    
    # Throttle checks
    current_time = time.time()
    if current_time - last_check_time < check_interval:
        return
    last_check_time = current_time
    
    # Check if file exists and was modified
    if not os.path.exists(drr_file_path):
        return
    
    try:
        mod_time = os.path.getmtime(drr_file_path)
        if mod_time > last_mod_time:
            last_mod_time = mod_time
            # Reload texture by setting URL again
            # Adding a cache-buster query string
            drr_texture.url.setValue([drr_file_path + "?" + str(mod_time)])
            print("[DRR Loader] Reloaded texture: " + drr_file_path)
    except Exception as e:
        print("[DRR Loader ERROR] " + str(e))

# Initialize on load
initialize()
