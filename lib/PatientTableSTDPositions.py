#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Patient Table Standard Positions
=================================

This module provides predefined standard medical positions for the patient table
in the EVAR training simulator. These positions are commonly used in medical
procedures and provide quick setup for typical surgical scenarios.

Standard Positions Include:
- Neutral/Supine: Standard flat position
- Trendelenburg: Head down, feet up (for hypotension management)
- Reverse Trendelenburg: Head up, feet down (for respiratory comfort)
- High Position: Elevated table for surgeon ergonomics
- Low Position: Lowered table for equipment access
- Lateral Decubitus: Side-lying positions
- Custom positions for specific procedures

"""

from H3DInterface import *
import math

# Import the patient table movement system
try:
    from PatientTableMovement import patientTableMovements
except ImportError:
    print("Warning: PatientTableMovement module not found")
    patientTableMovements = None


class PatientTableStandardPositions:
    """
    Standard medical positions for patient table positioning.
    
    This class provides methods to quickly set the patient table to
    commonly used medical positions with appropriate safety constraints.
    """
    
    def __init__(self):
        """Initialize standard positions with medical parameters."""
        
        # Standard position definitions (all values in appropriate units)
        self.positions = {
            'neutral': {
                'name': 'Neutral/Supine Position',
                'description': 'Standard flat position for most procedures',
                'height': 0.0,           # Table at neutral height
                'tilt': 0.0,             # No Trendelenburg
                'lateral': 0.0,          # Centered laterally
                'longitudinal': 0.0,     # Centered longitudinally
                'rotation': 0.0,         # No rotation
                'flex': 0.0              # No flexion
            },
            
            'trendelenburg': {
                'name': 'Trendelenburg Position',
                'description': 'Head down 15° for hypotension management',
                'height': 0.0,
                'tilt': -0.262,          # -15 degrees (head down)
                'lateral': 0.0,
                'longitudinal': 0.0,
                'rotation': 0.0,
                'flex': 0.0
            },
            
            'reverse_trendelenburg': {
                'name': 'Reverse Trendelenburg Position', 
                'description': 'Head up 15° for respiratory comfort',
                'height': 0.0,
                'tilt': 0.262,           # +15 degrees (head up)
                'lateral': 0.0,
                'longitudinal': 0.0,
                'rotation': 0.0,
                'flex': 0.0
            },
            
            'steep_trendelenburg': {
                'name': 'Steep Trendelenburg Position',
                'description': 'Head down 30° for specific procedures',
                'height': 0.0,
                'tilt': -0.524,          # -30 degrees (maximum safe tilt)
                'lateral': 0.0,
                'longitudinal': 0.0,
                'rotation': 0.0,
                'flex': 0.0
            },
            
            'high_position': {
                'name': 'High Table Position',
                'description': 'Elevated table for surgeon ergonomics',
                'height': 0.2,           # +20cm elevation
                'tilt': 0.0,
                'lateral': 0.0,
                'longitudinal': 0.0,
                'rotation': 0.0,
                'flex': 0.0
            },
            
            'low_position': {
                'name': 'Low Table Position',
                'description': 'Lowered table for equipment access',
                'height': -0.2,          # -20cm lowered
                'tilt': 0.0,
                'lateral': 0.0,
                'longitudinal': 0.0,
                'rotation': 0.0,
                'flex': 0.0
            },
            
            'left_lateral': {
                'name': 'Left Lateral Decubitus',
                'description': 'Patient on left side for right-side access',
                'height': 0.0,
                'tilt': 0.0,
                'lateral': 0.0,
                'longitudinal': 0.0,
                'rotation': -0.262,      # -15 degrees (left side down)
                'flex': 0.0
            },
            
            'right_lateral': {
                'name': 'Right Lateral Decubitus',
                'description': 'Patient on right side for left-side access',
                'height': 0.0,
                'tilt': 0.0,
                'lateral': 0.0,
                'longitudinal': 0.0,
                'rotation': 0.262,       # +15 degrees (right side down)
                'flex': 0.0
            },
            
            'flexed_position': {
                'name': 'Flexed Position',
                'description': 'Table flexed at waist for spinal procedures',
                'height': 0.0,
                'tilt': 0.0,
                'lateral': 0.0,
                'longitudinal': 0.0,
                'rotation': 0.0,
                'flex': 0.175            # +10 degrees flexion
            },
            
            'evar_standard': {
                'name': 'EVAR Standard Position',
                'description': 'Optimized position for EVAR procedures',
                'height': 0.1,           # Slightly elevated
                'tilt': -0.087,          # Slight Trendelenburg (-5°)
                'lateral': 0.0,
                'longitudinal': 0.0,
                'rotation': 0.0,
                'flex': 0.0
            }
        }
        
        print("Patient Table Standard Positions initialized")
    
    def setPosition(self, position_name):
        """
        Set the patient table to a predefined standard position.
        
        Args:
            position_name: Name of the standard position to set
            
        Returns:
            bool: True if position was set successfully, False otherwise
        """
        if not patientTableMovements:
            print("Error: Patient table movement system not available")
            return False
            
        if position_name not in self.positions:
            print(f"Error: Unknown position '{position_name}'")
            print(f"Available positions: {list(self.positions.keys())}")
            return False
        
        position = self.positions[position_name]
        
        try:
            print(f"Setting patient table to: {position['name']}")
            print(f"Description: {position['description']}")
            
            # Set all DOF parameters
            patientTableMovements.setPosition({
                'height': position['height'],
                'tilt': position['tilt'],
                'lateral': position['lateral'],
                'longitudinal': position['longitudinal'],
                'rotation': position['rotation'],
                'flex': position['flex']
            })
            
            return True
            
        except Exception as e:
            print(f"Error setting position '{position_name}': {e}")
            return False
    
    def getNeutralPosition(self):
        """Set patient table to neutral/supine position."""
        return self.setPosition('neutral')
    
    def getTrendelenburgPosition(self):
        """Set patient table to Trendelenburg position (head down)."""
        return self.setPosition('trendelenburg')
    
    def getReverseTrendelenburgPosition(self):
        """Set patient table to reverse Trendelenburg position (head up)."""
        return self.setPosition('reverse_trendelenburg')
    
    def getSupinePosition(self):
        """Set patient table to supine position (same as neutral)."""
        return self.setPosition('neutral')
    
    def getEVARPosition(self):
        """Set patient table to optimal EVAR procedure position."""
        return self.setPosition('evar_standard')
    
    def getHighPosition(self):
        """Set patient table to elevated position."""
        return self.setPosition('high_position')
    
    def getLowPosition(self):
        """Set patient table to lowered position."""
        return self.setPosition('low_position')
    
    def getLeftLateralPosition(self):
        """Set patient table to left lateral decubitus position."""
        return self.setPosition('left_lateral')
    
    def getRightLateralPosition(self):
        """Set patient table to right lateral decubitus position."""
        return self.setPosition('right_lateral')
    
    def getFlexedPosition(self):
        """Set patient table to flexed position."""
        return self.setPosition('flexed_position')
    
    def listAvailablePositions(self):
        """
        Get list of all available standard positions.
        
        Returns:
            dict: Dictionary of position names and descriptions
        """
        return {name: pos['name'] + ' - ' + pos['description'] 
                for name, pos in self.positions.items()}
    
    def getPositionParameters(self, position_name):
        """
        Get the parameters for a specific position.
        
        Args:
            position_name: Name of the position
            
        Returns:
            dict: Position parameters or None if not found
        """
        return self.positions.get(position_name)
    
    def calculatePosition(self, height=0, tilt_degrees=0, lateral=0, 
                         longitudinal=0, rotation_degrees=0, flex_degrees=0):
        """
        Calculate a custom position with degree inputs converted to radians.
        
        Args:
            height: Height in meters (±0.3)
            tilt_degrees: Tilt in degrees (±30)
            lateral: Lateral position in meters (±0.2)
            longitudinal: Longitudinal position in meters (±0.5)
            rotation_degrees: Rotation in degrees (±30)
            flex_degrees: Flexion in degrees (±15)
            
        Returns:
            dict: Position parameters ready for use
        """
        # Convert degrees to radians
        tilt_rad = math.radians(tilt_degrees)
        rotation_rad = math.radians(rotation_degrees)
        flex_rad = math.radians(flex_degrees)
        
        # Apply safety constraints
        height = max(-0.3, min(0.3, height))
        tilt_rad = max(-0.524, min(0.524, tilt_rad))
        lateral = max(-0.2, min(0.2, lateral))
        longitudinal = max(-0.5, min(0.5, longitudinal))
        rotation_rad = max(-0.524, min(0.524, rotation_rad))
        flex_rad = max(-0.262, min(0.262, flex_rad))
        
        return {
            'height': height,
            'tilt': tilt_rad,
            'lateral': lateral,
            'longitudinal': longitudinal,
            'rotation': rotation_rad,
            'flex': flex_rad
        }
    
    def setCustomPosition(self, height=0, tilt_degrees=0, lateral=0,
                         longitudinal=0, rotation_degrees=0, flex_degrees=0):
        """
        Set a custom position with degree inputs.
        
        Args:
            height: Height in meters
            tilt_degrees: Tilt in degrees
            lateral: Lateral position in meters
            longitudinal: Longitudinal position in meters
            rotation_degrees: Rotation in degrees
            flex_degrees: Flexion in degrees
        """
        if not patientTableMovements:
            print("Error: Patient table movement system not available")
            return False
        
        position = self.calculatePosition(
            height, tilt_degrees, lateral, longitudinal, 
            rotation_degrees, flex_degrees
        )
        
        try:
            patientTableMovements.setPosition(position)
            print(f"Custom position set: Height={height:.2f}m, "
                  f"Tilt={tilt_degrees:.1f}°, Lateral={lateral:.2f}m, "
                  f"Longitudinal={longitudinal:.2f}m, Rotation={rotation_degrees:.1f}°, "
                  f"Flex={flex_degrees:.1f}°")
            return True
        except Exception as e:
            print(f"Error setting custom position: {e}")
            return False


# Button callback functions for UI integration
def neutralPositionCallback(event=None):
    """Callback for neutral position button."""
    if standardPositions:
        standardPositions.getNeutralPosition()

def trendelenburgPositionCallback(event=None):
    """Callback for Trendelenburg position button."""
    if standardPositions:
        standardPositions.getTrendelenburgPosition()

def reverseTrendelenburgPositionCallback(event=None):
    """Callback for reverse Trendelenburg position button."""
    if standardPositions:
        standardPositions.getReverseTrendelenburgPosition()

def supinePositionCallback(event=None):
    """Callback for supine position button."""
    if standardPositions:
        standardPositions.getSupinePosition()

def resetPositionCallback(event=None):
    """Callback for reset position button."""
    if patientTableMovements:
        patientTableMovements.resetToNeutral()


# Initialize the global standard positions instance
standardPositions = PatientTableStandardPositions()