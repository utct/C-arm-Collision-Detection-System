"""
Segmentation Controller - Manages segmentation overlay toggles
==============================================================

This script handles toggle buttons for different anatomical structures
and writes the active segments to segmentation_settings.json for the
DRR server to read.

Group names match the DeepFluoro dataset bundled with DiffDRR:
- ribs: Individual ribs (24 structures)
- vertebrae: Individual vertebrae (26 structures)  
- organs: Internal organs (24 structures)
- cardiac: Heart and blood vessels (18 structures)
- skeleton: Appendicular skeleton (11 structures)
- muscles: Muscle groups (12 structures)
"""

from H3DInterface import *
import json
import os
import time

# Global state
active_segments = set()
segment_buttons = {}

# Available segmentation categories (matches DiffDRR's DeepFluoro dataset)
SEGMENT_CATEGORIES = ['ribs', 'vertebrae', 'organs', 'cardiac', 'skeleton', 'muscles']

def initialize():
    """Initialize references from main.x3d."""
    global segment_buttons
    
    refs = references.getValue()
    print("[Segmentation] Initializing with " + str(len(refs)) + " references")
    
    # Map buttons to categories
    for i, cat in enumerate(SEGMENT_CATEGORIES):
        if i < len(refs):
            segment_buttons[cat] = refs[i]
            print("[Segmentation] Mapped button for: " + cat)
    
    print("[Segmentation] Ready! Categories: " + str(SEGMENT_CATEGORIES))

def write_settings():
    """Write active segments to JSON file for DRR server."""
    global active_segments
    
    settings = {
        'active': list(active_segments)
    }
    
    try:
        with open('segmentation_settings.json', 'w') as f:
            json.dump(settings, f)
        print("[Segmentation] Updated: " + str(list(active_segments)))
    except Exception as e:
        print("[Segmentation ERROR] " + str(e))

def trigger_drr_refresh():
    """
    Trigger a DRR refresh by updating the timestamp in collision_pose.json.
    This causes the DRR server to re-render with the new segment settings.
    """
    pose_file = 'collision_pose.json'
    try:
        # Read current pose
        with open(pose_file, 'r') as f:
            pose_data = json.load(f)
        
        # Update timestamp to trigger refresh
        pose_data['timestamp'] = time.time()
        
        # Write back
        with open(pose_file, 'w') as f:
            json.dump(pose_data, f)
        
        print("[Segmentation] Triggered DRR refresh")
    except Exception as e:
        print("[Segmentation] Could not trigger refresh: " + str(e))

def toggle_segment(category, enabled):
    """Toggle a segment category on/off."""
    global active_segments
    
    if enabled:
        active_segments.add(category)
    else:
        active_segments.discard(category)
    
    # Write new settings
    write_settings()
    
    # Trigger DRR to refresh immediately
    trigger_drr_refresh()

# Event handler classes for each category
class RibsHandler(AutoUpdate(SFBool)):
    def update(self, event):
        toggle_segment('ribs', event.getValue())
        return event.getValue()

class VertebraeHandler(AutoUpdate(SFBool)):
    def update(self, event):
        toggle_segment('vertebrae', event.getValue())
        return event.getValue()

class OrgansHandler(AutoUpdate(SFBool)):
    def update(self, event):
        toggle_segment('organs', event.getValue())
        return event.getValue()

class CardiacHandler(AutoUpdate(SFBool)):
    def update(self, event):
        toggle_segment('cardiac', event.getValue())
        return event.getValue()

class SkeletonHandler(AutoUpdate(SFBool)):
    def update(self, event):
        toggle_segment('skeleton', event.getValue())
        return event.getValue()

class MusclesHandler(AutoUpdate(SFBool)):
    def update(self, event):
        toggle_segment('muscles', event.getValue())
        return event.getValue()

# Create input fields for routes
ribsToggle = RibsHandler()
vertebraeToggle = VertebraeHandler()
organsToggle = OrgansHandler()
cardiacToggle = CardiacHandler()
skeletonToggle = SkeletonHandler()
musclesToggle = MusclesHandler()

# Initialize on load
initialize()
