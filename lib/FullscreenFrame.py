
from H3DInterface import*
import math

#
# function that calculates a 4x4 transformation matrix that aligns a rectangle
# positioned at (0,0,0) that has the specified size to fit the entire viewport
# taking the set FOV, viewpoint position, orientation and size into account
#
class ViewPlaneMatrixField(TypedField(SFMatrix4f, (SFVec3f, SFRotation, SFFloat, SFFloat, SFVec2f, SFInt32, SFInt32))):

	def update(self, event):
		ri = self.getRoutesIn()
		if len(ri) != 7:
			return Matrix4f()

		viewPos = ri[0].getValue()
		viewOr = ri[1].getValue()
		ViewFov = ri[2].getValue()
		dis = ri[3].getValue()
		size = ri[4].getValue()
		windowwidth = ri[5].getValue()
		windowheight = ri[6].getValue()

		rotationMatrix = Matrix4f(viewOr)
		translation = viewPos + Matrix4f(viewOr) * Vec3f(0,0,-dis)
		translationMatrix = Matrix4f()
		scaleMatrix = Matrix4f()
		translationMatrix.setElement(0,3,translation.x)
		translationMatrix.setElement(1,3,translation.y)
		translationMatrix.setElement(2,3,translation.z)
		if windowwidth >= windowheight:
			#fov is heightAngle
			scale = ( 2 * dis * math.tan(ViewFov/2) ) / size.y
			scaleMatrix.setElement(1,1,scale)
			scaleMatrix.setElement(0,0,scale*windowwidth/windowheight*size.y/size.x)
		else:
			#fov is widthAngle
			scale = ( 2 * dis * math.tan(ViewFov/2) ) / size.x
			scaleMatrix.setElement(0,0,scale)
			scaleMatrix.setElement(1,1,scale*windowheight/windowwidth*size.x/size.y)
		return translationMatrix * rotationMatrix * scaleMatrix


ViewpointPosition = SFVec3f()
ViewpointOrientation = SFRotation()
ViewpointFOV = SFFloat()
DistanceToViewplane = SFFloat()
SizeOfViewplane	= SFVec2f()
ViewplaneMatrix = ViewPlaneMatrixField()

# set up routes
ViewpointPosition.route(ViewplaneMatrix)
ViewpointOrientation.route(ViewplaneMatrix)
ViewpointFOV.route(ViewplaneMatrix)
DistanceToViewplane.route(ViewplaneMatrix)
SizeOfViewplane.route(ViewplaneMatrix)
getCurrentScenes()[0].window.getValue()[0].getField('width').route(ViewplaneMatrix)
getCurrentScenes()[0].window.getValue()[0].getField('height').route(ViewplaneMatrix)
