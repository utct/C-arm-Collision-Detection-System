from H3DInterface import*

#
# Field class that gets the keysensor's keyPress and isActive field routed in,
# boolean is routed out to a toggle group. At the same time the slider is
# activated or deactivated via reference.
#
class showZoom( TypedField( SFBool, ( SFString, SFBool ) ) ):
	def update(self, event):
		key = self.getRoutesIn()[0].getValue()
		isActive = self.getRoutesIn()[1].getValue()
		if isActive and key == "z":
			references.getValue()[0].getField("enabled").setValue(True)
			return True
		references.getValue()[0].getField("enabled").setValue(False)	
		return False
		
showZoom = showZoom()
