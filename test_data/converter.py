from H3DInterface import *

class CvtMatrix(TypedField(SFMatrix4f, SFMatrix4d)):

	def update(self, event):
		return Matrix4f(event.getValue())
		
m2m = CvtMatrix()