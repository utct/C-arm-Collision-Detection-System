#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Patient Table Movement Control (3 DOF - Simple Translation)
===========================================================

This module controls the 3 translational DOF of the patient table:
- Vertical: Extends telescoping column up/down (0 to 36cm)
- Longitudinal: Table top slides head-to-foot (0 to 70cm)  
- Transverse: Table top slides left-right (-13 to 13cm)

Simplified version for H3D Python 2.7 - doesn't use DH transformations.
"""

from H3DInterface import *

# Global references to table transforms
table_top_transform = None
table_body_transform = None
table_wheels_transform = None
patient_transform = None

# Current table joint values (in meters)
current_vertical = 0.0
current_longitudinal = 0.0
current_transverse = 0.0

def initialize():
    """Initialize transform node references from X3D scene."""
    global table_top_transform, table_body_transform, table_wheels_transform, patient_transform
    
    # Get references passed from main.x3d
    # refs[0] = TTableTopBase (top that slides)
    # refs[1] = TTableBodyTransform (middle column that lifts)
    # refs[2] = TTableWheelsTransform (base wheels - stay on ground)
    # refs[3] = TPatientTransform (patient - rises with table)
    
    refs = references.getValue()
    if len(refs) >= 4:
        table_top_transform = refs[0]
        table_body_transform = refs[1]
        table_wheels_transform = refs[2]
        patient_transform = refs[3]
        print("[TableMovement] Initialized with 3 table transforms + patient")
        print("[TableMovement] Ready for table DOF control")
    else:
        print("[TableMovement ERROR] Not enough references! Need 4 transforms, got " + str(len(refs)))

def update_table_transforms(vertical_cm, longitudinal_cm, transverse_cm):
    """
    Update table transforms based on slider values.
    
    Args:
        vertical_cm: Vertical position in centimeters (0 to 36)
        longitudinal_cm: Longitudinal position in centimeters (0 to 70)
        transverse_cm: Transverse position in centimeters (-13 to 13)
    """
    global table_top_transform, table_body_transform, table_wheels_transform, patient_transform
    global current_vertical, current_longitudinal, current_transverse
    
    if table_top_transform is None or table_body_transform is None or table_wheels_transform is None or patient_transform is None:
        print("[TableMovement] Transforms not initialized yet")
        return
    
    # Convert cm to meters
    vertical_m = vertical_cm / 100.0
    longitudinal_m = longitudinal_cm / 100.0
    transverse_m = transverse_cm / 100.0
    
    # Store current values
    current_vertical = vertical_m
    current_longitudinal = longitudinal_m
    current_transverse = transverse_m
    
    try:
        # Table is rotated 90° around Y in main.x3d: rotation='0 1 0 1.5708'
        # In the rotated frame: longitudinal → X, transverse → Z
        
        # Table top: moves in longitudinal (X) and transverse (Z) directions
        # AND rises with vertical extension (Y)
        # Base position is 0.325, 0, 0
        table_top_x = 0.325 - longitudinal_m  # Negative to match collision system direction
        table_top_y = 0.0 + vertical_m  # Top rises with column extension
        table_top_z = transverse_m
        table_top_transform.translation.setValue(Vec3f(table_top_x, table_top_y, table_top_z))
        
        # Table body: extends upward with vertical movement (Y-axis)
        # Base position is 0.4, -0.6, 0
        table_body_transform.translation.setValue(Vec3f(0.4, -0.6 + vertical_m, 0.0))
        
        # Table wheels: stay on ground (fixed position)
        table_wheels_transform.translation.setValue(Vec3f(0.25, -0.6, 0.0))
        
        # Patient: moves with table in all directions
        # Base position is 0.3, -0.15, -0.34 (matches patient_table_only.x3d)
        # Patient is NOT inside the table rotation, so we need to apply movements in world coordinates
        # The table is rotated 90° around Y, so: table X → world Z, table Z → world -X
        patient_x = 0.3 + transverse_m  # Transverse (table Z) → X in world
        patient_y = -0.15 + vertical_m   # Vertical stays as Y
        patient_z = -0.34 + longitudinal_m  # Longitudinal
        patient_transform.translation.setValue(Vec3f(patient_x, patient_y, patient_z))
        
        # Debug output
        print("[TableMovement] Updated: V={0:.2f}cm L={1:.2f}cm T={2:.2f}cm".format(
            vertical_cm, longitudinal_cm, transverse_cm))
        
    except Exception as e:
        print("[TableMovement ERROR] Failed to update transforms: " + str(e))

# Event handler classes for slider changes
class TableVerticalHandler(AutoUpdate(SFFloat)):
    """Handles vertical slider changes."""
    def update(self, event):
        value_cm = event.getValue()
        print("[TableMovement] Vertical slider changed to: {0:.2f}cm".format(value_cm))
        global current_longitudinal, current_transverse
        update_table_transforms(value_cm, current_longitudinal * 100, current_transverse * 100)
        return value_cm

class TableLongitudinalHandler(AutoUpdate(SFFloat)):
    """Handles longitudinal slider changes."""
    def update(self, event):
        value_cm = event.getValue()
        print("[TableMovement] Longitudinal slider changed to: {0:.2f}cm".format(value_cm))
        global current_vertical, current_transverse
        update_table_transforms(current_vertical * 100, value_cm, current_transverse * 100)
        return value_cm

class TableTransverseHandler(AutoUpdate(SFFloat)):
    """Handles transverse slider changes."""
    def update(self, event):
        value_cm = event.getValue()
        print("[TableMovement] Transverse slider changed to: {0:.2f}cm".format(value_cm))
        global current_vertical, current_longitudinal
        update_table_transforms(current_vertical * 100, current_longitudinal * 100, value_cm)
        return value_cm

# Create input fields for routes
tableVertical = TableVerticalHandler()
tableLongitudinal = TableLongitudinalHandler()
tableTransverse = TableTransverseHandler()

# Initialize on load
initialize()
