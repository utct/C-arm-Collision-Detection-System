from H3DInterface import*
import os
import inspect

xRayTex = None
heatTex = None
number = 0
counter = 1

SAVE_TEXTURE_SIZE = 256


injectXRay = SFBool()

def initialize():
	global injectXRay
	takeXRay.setValue("NEXT_FRAME_ONLY")
	injectXRay.setValue(False)
	injectXRay.route(takeXRay)
	
def traverseSG():
	if injectXRay.getValue():
		injectXRay.setValue(False)

class setXRayTextureReference( AutoUpdate( MFNode ) ):
	def update(self, event):
		routes_in = self.getRoutesIn()
		global xRayTex
		try:
			xRayTex = routes_in[0].getValue()
			self.setValue(xRayTex)
			#Set save size of the framebuffertexturegenerator to 256*256 because
			#in the original size of 1024*1024 as defined in the x3d saving takes
			#FOREVER (ca 2 seconds)
			xRayTex[0].saveHeight.setValue(SAVE_TEXTURE_SIZE)
			xRayTex[0].saveWidth.setValue(SAVE_TEXTURE_SIZE)
		except AttributeError:
			pass
		except IndexError:
			pass
		return [Node()]
		
		

		
class saveScreenshots( AutoUpdate( TypedField( SFBool, ( SFString, SFBool ) ) ) ):
	def update(self, event):
		global counter
		routes_in = self.getRoutesIn()
		try:
			keyPress = routes_in[0].getValue()
			isActive = routes_in[1].getValue()
			if isActive and keyPress == "2":
				counter = (counter + 1) % 2
				if counter == 0:
					global number
					global xRayTex
					number = number + 1
					path = os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))) + "\\drr"
					#print "Saving X-Ray"
					ctr = 0
					for i in xRayTex:
						i.saveToUrl.setValue(path + "\\drr" + str(number) + "_" + str(ctr) + "_xray.png")
						print "X-Ray saved to " + path + "\\drr" + str(number) + "_" + str(ctr) + "_xray.png"
						ctr= ctr + 1
					ctr = 0
					for i in heatTex:
						i.saveToUrl.setValue(path + "\\drr" + str(number) + "_" + str(ctr) + "_heat.png")
						print "X-Ray saved to " + path + "\\drr" + str(number) + "_" + str(ctr) + "_heat.png"
						ctr= ctr + 1
					return True
		except IndexError:
			pass
		return False



class takeXRay( AutoUpdate(TypedField( SFString,(SFBool, SFString, SFBool, SFBool ) ) ) ):
	def update(self, event):
		global injectedCounter
		routes_in = self.getRoutesIn()
		try:
			injectXRayValue = routes_in[0].getValue()
			keyPress = routes_in[1].getValue()
			isActive = routes_in[2].getValue()
			joystick = routes_in[3].getValue()
			if joystick:
				return "NEXT_FRAME_ONLY"
			if isActive and keyPress == "1":
				return "NEXT_FRAME_ONLY"
			if injectXRayValue:
				return "NEXT_FRAME_ONLY"
		except IndexError:
			pass
		return self.getValue()
		
oldTransversal0 = None
oldTransversal1 = None

class Matrix2ViewpointTranslation( (TypedField( SFVec3f , (SFMatrix4f) ) ) ):
	def update(self, event):

		try:
			routes_in = self.getRoutesIn()
			matrix = routes_in[0].getValue()


			return matrix.getTranslationPart()
		except IndexError:
			pass
		return self.getValue()
		
oldIsHorizontal = None
		
class Matrix2ViewpointRotation( (TypedField( SFRotation , ( SFMatrix4f ) ) ) ):
	def update(self, event):


		try:
			routes_in = self.getRoutesIn()
			matrix = routes_in[0].getValue()
			#print Rotation((matrix).getRotationPart().toEulerAngles())
			#print matrix
			#print (matrix).getRotationPart().toEulerAngles()
			return Rotation((matrix).getRotationPart().toEulerAngles())
			
		except IndexError:
			pass
		return self.getValue()


takeXRay = takeXRay()
setXRayTextureReference = setXRayTextureReference()
saveScreenshots = saveScreenshots()
matrix2ViewpointTranslation = Matrix2ViewpointTranslation()
matrix2ViewpointRotation = Matrix2ViewpointRotation()
