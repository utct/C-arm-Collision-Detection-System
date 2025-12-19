"""
DRR Mode Controller - Toggles between volume rendering and DiffDRR
===================================================================

This script handles:
1. Toggle button state for switching X-ray rendering modes
2. Reloading DRR texture when drr_live.png is updated
3. Visual feedback for current mode
"""

from H3DInterface import *
import os
import time

# Global state
volume_toggle = None      # ToggleGroup for volume rendering
drr_toggle = None         # ToggleGroup for DRR display
drr_texture = None        # ImageTexture for DRR
mode_button = None        # Toggle button
last_mod_time = 0
check_interval = 0.5      # Check every 500ms
last_check_time = 0
drr_file_path = "drr_live.png"
drr_mode_active = True  # Start with DRR mode ON by default

def initialize():
    """Initialize references from main.x3d."""
    global volume_toggle, drr_toggle, drr_texture, mode_button
    
    refs = references.getValue()
    if len(refs) >= 4:
        volume_toggle = refs[0]   # cArmCircle ToggleGroup
        drr_toggle = refs[1]      # DRRCircle ToggleGroup
        drr_texture = refs[2]     # DRRTexture ImageTexture
        mode_button = refs[3]     # DRRModeToggle TouchButton
        print("[DRR Controller] Initialized successfully")
        print("[DRR Controller] DRR mode ON by default")
        # Ensure DRR mode is active on startup
        set_drr_mode(True)
    else:
        print("[DRR Controller ERROR] Not enough references! Need 4, got " + str(len(refs)))

def set_drr_mode(enabled):
    """Switch between volume rendering and DRR mode."""
    global drr_mode_active, volume_toggle, drr_toggle, mode_button
    
    drr_mode_active = enabled
    
    if volume_toggle is not None:
        volume_toggle.graphicsOn.setValue(not enabled)
    
    if drr_toggle is not None:
        drr_toggle.graphicsOn.setValue(enabled)
    
    # Update button text (MFString needs a list)
    if mode_button is not None:
        if enabled:
            mode_button.text.setValue(["DRR Mode: ON"])
            print("[DRR Controller] Switched to DRR mode (photorealistic)")
        else:
            mode_button.text.setValue(["DRR Mode: OFF"])
            print("[DRR Controller] Switched to volume rendering mode")

def reload_drr_texture():
    """Reload the DRR texture if file was updated."""
    global drr_texture, last_mod_time
    
    if drr_texture is None or not drr_mode_active:
        return
    
    if not os.path.exists(drr_file_path):
        return
    
    try:
        mod_time = os.path.getmtime(drr_file_path)
        if mod_time > last_mod_time:
            last_mod_time = mod_time
            # Force texture reload by clearing and re-setting URL
            # H3D doesn't support query strings, so we toggle the URL
            drr_texture.url.setValue([])  # Clear first
            drr_texture.url.setValue([drr_file_path])  # Then set again
            print("[DRR Controller] Texture reloaded")
    except Exception as e:
        print("[DRR Controller ERROR] " + str(e))

def traverseSG():
    """Called every frame - check for texture updates."""
    global last_check_time
    
    current_time = time.time()
    if current_time - last_check_time < check_interval:
        return
    last_check_time = current_time
    
    reload_drr_texture()

# Event handler for toggle button
class DRRModeHandler(AutoUpdate(SFBool)):
    """Handles DRR mode toggle button state changes."""
    def update(self, event):
        state = event.getValue()
        set_drr_mode(state)
        return state

# Create input field for route
drrModeToggle = DRRModeHandler()

# Initialize on load
initialize()
