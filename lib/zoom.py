from H3DInterface import*

#
# Field class that transforms a SFFloat into a SFVec3f for zooming
#
class slider2Zoom( TypedField( SFVec3f, SFFloat ) ):
	def update(self, event):
		sliderValue = self.getRoutesIn()[0].getValue()
		#print sliderValue
		return Vec3f(sliderValue*50, sliderValue*50, 1)

slider2Zoom = slider2Zoom()
