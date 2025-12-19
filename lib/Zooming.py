from H3DInterface import *
import os

class zoomingInOut( TypedField( SFFloat , (SFBool) )):
	def update(self, event):
		"""
		Toggle between zoomed in (default) and zoomed out (full view) states
		"""
		
		zoomed_in  = 0.13  # Default view - closer/zoomed in
		zoomed_out = 0.16  # Full view - just slightly further back (was 0.20, reduced to avoid box edges)
		
		button 	  = references.getValue()[0]
		routes_in = self.getRoutesIn()
		
		if (routes_in[0].getValue()):
			# Button is pressed - zoom out to full view
			button.getField("text").setValue(["Zoom In"])
			print("[Zoom] Zooming out to full view")
			return(zoomed_out)
		else:
			# Button is not pressed - return to default zoomed view
			button.getField("text").setValue(["Zoom Out"])
			print("[Zoom] Returning to zoomed view")
			return(zoomed_in)			
zoom = zoomingInOut()	
