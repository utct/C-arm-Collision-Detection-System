from H3DInterface import *
import sys
import os

class sideButtonTranslate( TypedField( SFVec3f , (SFBool , SFBool , SFBool) )):
	def update(self, event):
		"""
		Simplified for NRRD volumes - just resets view
		Uses same volume file for all options since side-specific files have positioning issues
		"""
		
		# Get references
		volume 		= references.getValue()[0]
		rightButton = references.getValue()[1]
		leftButton  = references.getValue()[2]
		bothButton  = references.getValue()[3]
		
		rightButtonsToggle = references.getValue()[4]
		leftButtonsToggle  = references.getValue()[5]
		
		carm = references.getValue()[6]
		
		trans1 = references.getValue()[7]
		trans2 = references.getValue()[8]
		trans3 = references.getValue()[9]
		
		routes_in = self.getRoutesIn()
		
		# All buttons just reset to center - no volume switching
		# (Side-specific volumes have positioning/zoom issues)
		
		# Both Sides
		if (routes_in[0].getValue()):
			print("[Sides] Both Sides - Center view")
			bothButton.getField("state").setValue(0)
			trans1.getField("value").setValue(0)
			trans2.getField("value").setValue(0)
			trans3.getField("value").setValue(0)
			return Vec3f(0, 0, 0)
			
		# Right Side
		elif (routes_in[1].getValue()):
			print("[Sides] Right Side - Center view")
			rightButton.getField("state").setValue(0)
			trans1.getField("value").setValue(0)
			trans2.getField("value").setValue(0)
			trans3.getField("value").setValue(0)
			return Vec3f(0, 0, 0)
			
		# Left Side
		elif (routes_in[2].getValue()):
			print("[Sides] Left Side - Center view")
			leftButton.getField("state").setValue(0)
			trans1.getField("value").setValue(0)
			trans2.getField("value").setValue(0)
			trans3.getField("value").setValue(0)
			return Vec3f(0, 0, 0)
		
		# Default
		return carm.getField("translation").getValue()

translateSide = sideButtonTranslate()	
