# Import to access H3D types
from H3DInterface import*

widthRatio = 16.0
heightRatio = 9.0

oldPixelHeight = 0 # height of window in pixels
oldPixelWidth = 0 # width of window in pixels

sceneRef = None

#
# sets sceneRef to reference of the scene (needed so windowWidth and height can be read)
#
def initialize():
	global sceneRef
	sceneRef = getCurrentScenes()[0]
	# Reset original width and height of the window
	sceneRef.window.getValue()[0].getField('width').setValue(768)
	sceneRef.window.getValue()[0].getField('height').setValue(432)

#
# sets height and width of window to always force set aspect ratio
#
def traverseSG():
	global oldPixelHeight
	global oldPixelWidth
	if not ((int (sceneRef.window.getValue()[0].getField('width').getValue() * (heightRatio/widthRatio) )) == oldPixelHeight):
		sceneRef.window.getValue()[0].getField('height').setValue( int (sceneRef.window.getValue()[0].getField('width').getValue() * (heightRatio/widthRatio) ))
		oldPixelHeight = int (sceneRef.window.getValue()[0].getField('width').getValue() * (heightRatio/widthRatio) )
	if not ((int (sceneRef.window.getValue()[0].getField('height').getValue() * (widthRatio/heightRatio) )) == oldPixelWidth):
		sceneRef.window.getValue()[0].getField('width').setValue( int (sceneRef.window.getValue()[0].getField('height').getValue() * (widthRatio/heightRatio) ))
		oldPixelWidth = int (sceneRef.window.getValue()[0].getField('height').getValue() * (widthRatio/heightRatio) )

#
# setter for heightRatio
#	
class setHeigthRatio( AutoUpdate(SFFloat) ):
	def update(self, event):
		routes_in = self.getRoutesIn()
		global heightRatio
		heightRatio = routes_in[0].getValue()
		return heightRatio

#
# setter for widthRatio
#		
class setWidthRatio( AutoUpdate(SFFloat) ):
	def update(self, event):
		routes_in = self.getRoutesIn()
		global widthRatio
		widthRatio = routes_in[0].getValue()
		return widthRatio	

setHeigthRatio = setHeigthRatio()
setWidthRatio = setWidthRatio()
