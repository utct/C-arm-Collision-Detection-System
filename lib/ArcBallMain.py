from H3DInterface import *


import copy
from math import cos, sin, sqrt, atan2
import numpy

		
		
#from ArcBall import *				# ArcBallT and this tutorials set of points/vectors/matrix types
PI = 3.1415926535
PI2 = 2.0*3.1415926535			# 2 * PI (not squared!)			// PI Squared
Epsilon = 1.0e-5

lastLength = 0
length = 0
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
class ArcBallT:
	def __init__ (self, NewWidth, NewHeight):
		self.m_StVec = Vector3fT ()
		self.m_EnVec = Vector3fT ()
		self.m_AdjustWidth = 1.0
		self.m_AdjustHeight = 1.0
		self.setBounds (NewWidth, NewHeight)
		self.transform = [ [1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0] ]
		self.lastRot   = [ [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0] ]
		self.thisRot   = [ [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0] ]

	def __str__ (self):
		str_rep = ""
		str_rep += "StVec = " + str (self.m_StVec)
		str_rep += "\nEnVec = " + str (self.m_EnVec)
		str_rep += "\n scale coords %f %f" % (self.m_AdjustWidth, self.m_AdjustHeight)
		return str_rep

	def setBounds (self, NewWidth, NewHeight):
		# //Set new bounds
		assert (NewWidth > 1.0 and NewHeight > 1.0), "Invalid width or height for bounds."
		# //Set adjustment factor for width/height
		self.m_AdjustWidth = 1.0 / ((NewWidth - 1.0) * 0.5)
		self.m_AdjustHeight = 1.0 / ((NewHeight - 1.0) * 0.5)

	def _mapToSphere (self, NewPt):
		# Given a new window coordinate, will modify NewVec in place
		global lastLength , length
		X = 0
		Y = 1
		Z = 2
		global global_center_of_sphere
		NewVec = Vector3fT ()
		# //Copy paramter into temp point
		TempPt = copy.copy (NewPt)
		
		# //Adjust point coords and scale down to range of [-1 ... 1]
		TempPt [X] = (NewPt [X] * self.m_AdjustWidth) - 1.0
		TempPt [Y] = 1.0 - (NewPt [Y] * self.m_AdjustHeight)
		# //Compute the square of the length of the vector to the point from the center
		length = numpy.dot (TempPt, TempPt) 
		#print length
		# //If the point is mapped outside of the sphere... (length > radius squared)
		if (length > 2.25):
			# //Compute a normalizing factor (radius / sqrt(length))
			norm	= 1.5 / sqrt (length);
			# //Return the "normalized" vector, a point on the sphere
			NewVec [X] = TempPt [X] * norm;
			NewVec [Y] = TempPt [Y] * norm;
			NewVec [Z] = 0.0;
		else:			# //Else it's on the inside
			# //Return a vector to a point mapped inside the sphere sqrt(radius squared - length)
			NewVec [X] = TempPt [X]
			NewVec [Y] = TempPt [Y]
			NewVec [Z] = sqrt (2.25 - length)

		return NewVec

	def click (self, NewPt):
		# //Mouse down (Point2fT
		self.m_StVec = self._mapToSphere (NewPt)
		return

	def drag (self, NewPt):
		# //Mouse drag, calculate rotation (Point2fT Quat4fT)
		""" drag (Point2fT mouse_coord) -> new_quaternion_rotation_vec
		"""
		X = 0
		Y = 1
		Z = 2
		W = 3
		
		self.m_EnVec = self._mapToSphere (NewPt)
		# //Compute the vector PerpendicularVecendicular to the begin and end vectors
		# PerpendicularVec = Vector3fT ()
		PerpendicularVec = Vector3fCross(self.m_StVec, self.m_EnVec);
		NewRot = Quat4fT ()
		# //Compute the length of the PerpendicularVecendicular vector
		if (Vector3fLength(PerpendicularVec) > Epsilon):		#	 //if its non-zero
			# //We're ok, so return the PerpendicularVecendicular vector as the transform after all
			NewRot[X] = PerpendicularVec[X];
			NewRot[Y] = PerpendicularVec[Y];
			NewRot[Z] = PerpendicularVec[Z];
			# //In the quaternion values, w is cosine (theta / 2), where theta is rotation angle
			NewRot[W] = Vector3fDot(self.m_StVec, self.m_EnVec);
		else:		#							 //if its zero
			# //The begin and end vectors coincide, so return a quaternion of zero matrix (no rotation)
			NewRot[X] = NewRot[Y] = NewRot[Z] = NewRot[W] = 0.0;

	
		return NewRot

	def getTransform( self ):
		return self.transform
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
def Matrix4fT ():
	return numpy.identity (4, 'f')

def Matrix3fT ():
	return numpy.identity (3, 'f')

def Quat4fT ():
	return numpy.zeros (4, 'f')

def Vector3fT ():
	return numpy.zeros (3, 'f')

def Point2fT (x = 0.0, y = 0.0):
	pt = numpy.zeros (2, 'f')
	pt [0] = x
	pt [1] = y
	return pt

def Vector3fDot(u, v):
	# Dot product of two 3f vectors
	dotprod = numpy.dot (u,v)
	return dotprod

def Vector3fCross(u, v):
	# Cross product of two 3f vectors
	X = 0
	Y = 1
	Z = 2
	cross = numpy.zeros (3, 'f')
	cross [X] = (u[Y] * v[Z]) - (u[Z] * v[Y])
	cross [Y] = (u[Z] * v[X]) - (u[X] * v[Z])
	cross [Z] = (u[X] * v[Y]) - (u[Y] * v[X])
	return cross

def Vector3fLength (u):
	mag_squared = numpy.dot (u,u)
	mag = sqrt (mag_squared)
	return mag
	
def Matrix3fSetIdentity ():
	return numpy.identity (3, 'f')

def Matrix3fMulMatrix3f (matrix_a, matrix_b):
	return numpy.dot (matrix_a, matrix_b)

def Matrix4fSVD (NewObj):
	X = 0
	Y = 1
	Z = 2
	s = sqrt ( 
		( (NewObj [X][X] * NewObj [X][X]) + (NewObj [X][Y] * NewObj [X][Y]) + (NewObj [X][Z] * NewObj [X][Z]) +
		(NewObj [Y][X] * NewObj [Y][X]) + (NewObj [Y][Y] * NewObj [Y][Y]) + (NewObj [Y][Z] * NewObj [Y][Z]) +
		(NewObj [Z][X] * NewObj [Z][X]) + (NewObj [Z][Y] * NewObj [Z][Y]) + (NewObj [Z][Z] * NewObj [Z][Z]) ) / 3.0 )
	return s

def Matrix4fSetRotationScaleFromMatrix3f(NewObj, three_by_three_matrix):
	# Modifies NewObj in-place by replacing its upper 3x3 portion from the 
	# passed in 3x3 matrix.
	# NewObj = Matrix4fT ()
	for i in range( 3 ):
		for j in range( 3 ):
			NewObj[i][j] = three_by_three_matrix[i][j]
	return NewObj

# /**
# * Sets the rotational component (upper 3x3) of this matrix to the matrix
# * values in the T precision Matrix3d argument; the other elements of
# * this matrix are unchanged; a singular value decomposition is performed
# * on this object's upper 3x3 matrix to factor out the scale, then this
# * object's upper 3x3 matrix components are replaced by the passed rotation
# * components, and then the scale is reapplied to the rotational
# * components.
# * @param three_by_three_matrix T precision 3x3 matrix
# */
def Matrix4fSetRotationFromMatrix3f (NewObj, three_by_three_matrix):
	scale = Matrix4fSVD (NewObj)

	NewObj = Matrix4fSetRotationScaleFromMatrix3f(NewObj, three_by_three_matrix);
	scaled_NewObj = copy.copy( NewObj )
	for i in range( 4 ):
		for j in range( 4 ):
			scaled_NewObj[i][j] *= scale
	#scaled_NewObj = NewObj * scale			  # Matrix4fMulRotationScale(NewObj, scale);
	return scaled_NewObj

def Matrix3fSetRotationFromQuat4f (q1):
	# Converts the H quaternion q1 into a new equivalent 3x3 rotation matrix. 
	X = 0
	Y = 1
	Z = 2
	W = 3

	Rotation_mat = Matrix3fT ()
	n = numpy.dot (q1, q1)
	s = 0.0
	if (n > 0.0):
		s = 2.0 / n
	xs = q1 [X] * s;  ys = q1 [Y] * s;	zs = q1 [Z] * s
	wx = q1 [W] * xs; wy = q1 [W] * ys; wz = q1 [W] * zs
	xx = q1 [X] * xs; xy = q1 [X] * ys; xz = q1 [X] * zs
	yy = q1 [Y] * ys; yz = q1 [Y] * zs; zz = q1 [Z] * zs
	# This math all comes about by way of algebra, complex math, and trig identities.
	# See Lengyel pages 88-92
	Rotation_mat [X][X] = 1.0 - (yy + zz);	  Rotation_mat [Y][X] = xy - wz;			Rotation_mat [Z][X] = xz + wy;
	Rotation_mat [X][Y] =		xy + wz;	  Rotation_mat [Y][Y] = 1.0 - (xx + zz);	Rotation_mat [Z][Y] = yz - wx;
	Rotation_mat [X][Z] =		xz - wy;	  Rotation_mat [Y][Z] = yz + wx;			Rotation_mat [Z][Z] = 1.0 - (xx + yy)

	return Rotation_mat
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#


# *********************** Globals *********************** 
# Python 2.2 defines these directly
try:
	True
except NameError:
	True = 1==1
	False = 1==0

def Upon_Drag (cursor_x, cursor_y):
	""" Mouse cursor is moving
		Glut calls this function (when mouse button is down)
		and pases the mouse cursor postion in window coords as the mouse moves.
	"""
	global g_isDragging, g_LastRot, g_Transform, g_ThisRot
	#print g_isDragging
	if (g_isDragging):
		mouse_pt = Point2fT (cursor_x, cursor_y)
		ThisQuat = g_ArcBall.drag (mouse_pt)						# // Update End Vector And Get Rotation As Quaternion
		g_ThisRot = Matrix3fSetRotationFromQuat4f (ThisQuat)		# // Convert Quaternion Into Matrix3fT
		# Use correct Linear Algebra matrix multiplication C = A * B
		g_LastRot = [ [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0] ]
		g_ThisRot = Matrix3fMulMatrix3f (g_LastRot, g_ThisRot)		# // Accumulate Last Rotation Into This One
		g_Transform = Matrix4fSetRotationFromMatrix3f (g_Transform, g_ThisRot)	# // Set Our Final Transform's Rotation From This One
		#print g_ThisRot
	return

def Upon_Click (cursor_x, cursor_y):
	""" Mouse button clicked.
		Glut calls this function when a mouse button is
		clicked or released.
	"""
	global g_isDragging, g_LastRot, g_Transform, g_ThisRot, leftButtonStatus

	g_isDragging = False
	# if (button == GLUT_RIGHT_BUTTON and button_state == GLUT_UP):
		# # Right button click
		# g_LastRot = Matrix3fSetIdentity ();							# // Reset Rotation
		# g_ThisRot = Matrix3fSetIdentity ();							# // Reset Rotation
		# g_Transform = Matrix4fSetRotationFromMatrix3f (g_Transform, g_ThisRot);	# // Reset Rotation
	# elif (button == GLUT_LEFT_BUTTON and button_state == GLUT_UP):
		# # Left button released
		# g_LastRot = copy.copy (g_ThisRot);							# // Set Last Static Rotation To Last Dynamic One
	if (leftButtonStatus):
		# Left button clicked down
		g_LastRot = copy.copy (g_ThisRot);							# // Set Last Static Rotation To Last Dynamic One
		g_isDragging = True											# // Prepare For Dragging
		mouse_pt = Point2fT (cursor_x, cursor_y)
		g_ArcBall.click (mouse_pt);								# // Update Start Vector And Prepare For Dragging

	return
	

dragging = False	

ImagePlaneWidthPixels  = [64 , 326]
ImagePlaneHeightPixels = [44 , 288]
OriginalWindowWidth	 = 0
OriginalWindowHeight = 0


def initialize():
	global sceneRef, g_isDragging, g_LastRot, g_Transform, g_ThisRot, dragging, g_ArcBall, OriginalWindowWidth, OriginalWindowHeight
	global LastDragPos
	sceneRef = getCurrentScenes()[0]
	
	g_Transform = Matrix4fT ()
	g_LastRot = Matrix3fT ()
	g_ThisRot = Matrix3fT ()
	
	OriginalWindowWidth	 = sceneRef.window.getValue()[0].getField('width').getValue() 
	OriginalWindowHeight = sceneRef.window.getValue()[0].getField('height').getValue()
	
	g_ArcBall = ArcBallT (OriginalWindowWidth + OriginalWindowWidth/8 , OriginalWindowHeight + OriginalWindowHeight/8)
	# g_ArcBall = ArcBallT (OriginalWindowWidth, OriginalWindowHeight)
	LastDragPos = [OriginalWindowWidth/2,OriginalWindowHeight/2]
	g_isDragging = False
	g_quadratic = None
	dragging = False
	
	carmRot1	= references.getValue()[1]
	carmRot2	= references.getValue()[2]
	carmRot3	= references.getValue()[3]
	carmtrans	= references.getValue()[4]
	
	carmRot1.getField("rotation").setValue( Rotation( 0, 0, 1, ( 0 * PI) / 180 ) )
	carmRot2.getField("rotation").setValue( Rotation( 0, 0, 1, ( 0 * PI) / 180 ) )
	carmRot3.getField("rotation").setValue( Rotation( 0, 1, 0, ( 0 * PI) / 180 ) )
	
LastDragPosTemp = [0,0]
LastDragPos = [0,0]
CurrentClickPos = [0,0]
firstTime = True
	
	
	
slot0 = [0,0]	
slot0Clicked = False
slot0inUse = False

slot1 = [0,0]	
slot1Clicked = False
slot1inUse = False

slot2 = [0,0]	
slot2Clicked = False
slot2inUse = False

slot3 = [0,0]	
slot3Clicked = False
slot3inUse = False

slot4 = [0,0]	
slot4Clicked = False
slot4inUse = False

slot5 = [0,0]	
slot5Clicked = False
slot5inUse = False

slot6 = [0,0]	
slot6Clicked = False
slot6inUse = False

slot7 = [0,0]	
slot7Clicked = False
slot7inUse = False

slot8 = [0,0]	
slot8Clicked = False
slot8inUse = False

slot9 = [0,0]	
slot9Clicked = False
slot9inUse = False

ABChecked = False
class ArcBallComputationClass( TypedField( SFBool, ( SFVec2f, SFBool, SFRotation, SFRotation ) ) ):
	def update(self, event):
		global g_ArcBall, g_isDragging, g_LastRot, g_Transform, g_ThisRot, leftButtonStatus, dragging, ROT_angular
		global ImagePlaneWidthPixels, ImagePlaneHeightPixels, OriginalWindowWidth, OriginalWindowHeight
		global LastDragPos, length, lastLength, firstTime, CurrentClickPos, LastDragPosTemp , ABChecked
		
		global slot0, slot0inUse, slot0Clicked
		global slot1, slot1inUse, slot1Clicked
		global slot2, slot2inUse, slot2Clicked
		global slot3, slot3inUse, slot3Clicked
		global slot4, slot4inUse, slot4Clicked
		global slot5, slot5inUse, slot5Clicked
		global slot6, slot6inUse, slot6Clicked
		global slot7, slot7inUse, slot7Clicked
		global slot8, slot8inUse, slot8Clicked
		global slot9, slot9inUse, slot9Clicked
		
		routes_in = self.getRoutesIn()
		
		position 		 = routes_in[0].getValue()
		leftButtonStatus = routes_in[1].getValue()
		ROT_orbital 	 = routes_in[2].getValue()
		ROT_angular 	 = routes_in[3].getValue()
		#ROT = routes_in[2].getValue()
		
		sceneRef 		 = getCurrentScenes()[0]
		
		carmRot1		 = references.getValue()[1]
		carmRot2		 = references.getValue()[2]
		rotation1Slider	 = references.getValue()[5]
		rotation2Slider	 = references.getValue()[6]

		saveSlot0 = references.getValue()[7].isPressed.getValue() 
		saveSlot1 = references.getValue()[8].isPressed.getValue() 
		saveSlot2 = references.getValue()[9].isPressed.getValue() 
		saveSlot3 = references.getValue()[10].isPressed.getValue() 
		saveSlot4 = references.getValue()[11].isPressed.getValue() 
		saveSlot5 = references.getValue()[12].isPressed.getValue() 
		saveSlot6 = references.getValue()[13].isPressed.getValue() 
		saveSlot7 = references.getValue()[14].isPressed.getValue()
		saveSlot8 = references.getValue()[15].isPressed.getValue() 
		saveSlot9 = references.getValue()[16].isPressed.getValue()  
		
		APButton = references.getValue()[17].isPressed.getValue()  
		
		CurrentWindowWidth	= sceneRef.window.getValue()[0].getField('width').getValue() 
		CurrentWindowHeight = sceneRef.window.getValue()[0].getField('height').getValue()
		
		if saveSlot0 and not(slot0inUse) :
			slot0[0] = LastDragPos[0] 
			slot0[1] = LastDragPos[1] 
			slot0inUse = True
		elif saveSlot0 and slot0inUse:
			slot0Clicked = True
			slot1Clicked = False
			slot2Clicked = False
			slot3Clicked = False
			slot4Clicked = False
			slot5Clicked = False
			slot6Clicked = False
			slot7Clicked = False
			slot8Clicked = False
			slot9Clicked = False
			ABChecked = False
			
		if saveSlot1 and not(slot1inUse) :
			slot1[0] = LastDragPos[0] 
			slot1[1] = LastDragPos[1] 
			slot1inUse = True
		elif saveSlot1 and slot1inUse:
			slot0Clicked = False
			slot1Clicked = True
			slot2Clicked = False
			slot3Clicked = False
			slot4Clicked = False
			slot5Clicked = False
			slot6Clicked = False
			slot7Clicked = False
			slot8Clicked = False
			slot9Clicked = False
			ABChecked = False
			
		if saveSlot2 and not(slot2inUse) :
			slot2[0] = LastDragPos[0] 
			slot2[1] = LastDragPos[1] 
			slot2inUse = True
		elif saveSlot2 and slot2inUse:
			slot0Clicked = False
			slot1Clicked = False
			slot2Clicked = True
			slot3Clicked = False
			slot4Clicked = False
			slot5Clicked = False
			slot6Clicked = False
			slot7Clicked = False
			slot8Clicked = False
			slot9Clicked = False
			ABChecked = False
			
		if saveSlot3 and not(slot3inUse) :
			slot3[0] = LastDragPos[0] 
			slot3[1] = LastDragPos[1] 
			slot3inUse = True
		elif saveSlot3 and slot3inUse:
			slot0Clicked = False
			slot1Clicked = False
			slot2Clicked = False
			slot3Clicked = True
			slot4Clicked = False
			slot5Clicked = False
			slot6Clicked = False
			slot7Clicked = False
			slot8Clicked = False
			slot9Clicked = False
			ABChecked = False
			
		if saveSlot4 and not(slot4inUse) :
			slot4[0] = LastDragPos[0] 
			slot4[1] = LastDragPos[1] 
			slot4inUse = True
		elif saveSlot4 and slot4inUse:
			slot0Clicked = False
			slot1Clicked = False
			slot2Clicked = False
			slot3Clicked = False
			slot4Clicked = True
			slot5Clicked = False
			slot6Clicked = False
			slot7Clicked = False
			slot8Clicked = False
			slot9Clicked = False
			ABChecked = False
			
		if saveSlot5 and not(slot5inUse) :
			slot5[0] = LastDragPos[0] 
			slot5[1] = LastDragPos[1] 
			slot5inUse = True
		elif saveSlot5 and slot5inUse:
			slot0Clicked = False
			slot1Clicked = False
			slot2Clicked = False
			slot3Clicked = False
			slot4Clicked = False
			slot5Clicked = True
			slot6Clicked = False
			slot7Clicked = False
			slot8Clicked = False
			slot9Clicked = False
			ABChecked = False
			
		if saveSlot6 and not(slot6inUse) :
			slot6[0] = LastDragPos[0] 
			slot6[1] = LastDragPos[1] 
			slot6inUse = True
		elif saveSlot6 and slot6inUse:
			slot0Clicked = False
			slot1Clicked = False
			slot2Clicked = False
			slot3Clicked = False
			slot4Clicked = False
			slot5Clicked = False
			slot6Clicked = True
			slot7Clicked = False
			slot8Clicked = False
			slot9Clicked = False
			ABChecked = False
			
		if saveSlot7 and not(slot7inUse) :
			slot7[0] = LastDragPos[0] 
			slot7[1] = LastDragPos[1] 
			slot7inUse = True
		elif saveSlot7 and slot7inUse:
			slot0Clicked = False
			slot1Clicked = False
			slot2Clicked = False
			slot3Clicked = False
			slot4Clicked = False
			slot5Clicked = False
			slot6Clicked = False
			slot7Clicked = True
			slot8Clicked = False
			slot9Clicked = False
			ABChecked = False
			
		if saveSlot8 and not(slot8inUse) :
			slot8[0] = LastDragPos[0] 
			slot8[1] = LastDragPos[1] 
			slot8inUse = True
		elif saveSlot8 and slot8inUse:
			slot0Clicked = False
			slot1Clicked = False
			slot2Clicked = False
			slot3Clicked = False
			slot4Clicked = False
			slot5Clicked = False
			slot6Clicked = False
			slot7Clicked = False
			slot8Clicked = True
			slot9Clicked = False
			ABChecked = False
			
		if saveSlot9 and not(slot9inUse) :
			slot9[0] = LastDragPos[0] 
			slot9[1] = LastDragPos[1] 
			slot9inUse = True
		elif saveSlot9 and slot9inUse:
			slot0Clicked = False
			slot1Clicked = False
			slot2Clicked = False
			slot3Clicked = False
			slot4Clicked = False
			slot5Clicked = False
			slot6Clicked = False
			slot7Clicked = False
			slot8Clicked = False
			slot9Clicked = True
			ABChecked = False
			
		if APButton:
			carmRot1.getField("rotation").setValue(Rotation(0,0,1,0))
			carmRot2.getField("rotation").setValue(Rotation(0,0,1,0))
			rotation1Slider.getField("value").setValue(-1 * 0 * 180/PI)
			rotation2Slider.getField("value").setValue(-1 * 0 * 180/PI)
			ABChecked = True
			slot0Clicked = False
			slot1Clicked = False
			slot2Clicked = False
			slot3Clicked = False
			slot4Clicked = False
			slot5Clicked = False
			slot6Clicked = False
			slot7Clicked = False
			slot8Clicked = False
			slot9Clicked = False

		if(CurrentWindowWidth != OriginalWindowWidth or CurrentWindowHeight != OriginalWindowHeight):
			g_ArcBall.setBounds(CurrentWindowWidth + CurrentWindowWidth/8, CurrentWindowHeight + CurrentWindowHeight/8)
			# g_ArcBall.setBounds(CurrentWindowWidth, CurrentWindowHeight)
			LastDragPos[0] = LastDragPos[0]*CurrentWindowWidth/OriginalWindowWidth
			LastDragPos[1] = LastDragPos[1]*CurrentWindowHeight/OriginalWindowHeight
			
			slot0[0] = slot0[0]*CurrentWindowWidth/OriginalWindowWidth
			slot0[1] = slot0[1]*CurrentWindowHeight/OriginalWindowHeight
			
			slot1[0] = slot1[0]*CurrentWindowWidth/OriginalWindowWidth
			slot1[1] = slot1[1]*CurrentWindowHeight/OriginalWindowHeight
			
			slot2[0] = slot2[0]*CurrentWindowWidth/OriginalWindowWidth
			slot2[1] = slot2[1]*CurrentWindowHeight/OriginalWindowHeight
			
			slot3[0] = slot3[0]*CurrentWindowWidth/OriginalWindowWidth
			slot3[1] = slot3[1]*CurrentWindowHeight/OriginalWindowHeight
			
			slot4[0] = slot4[0]*CurrentWindowWidth/OriginalWindowWidth
			slot4[1] = slot4[1]*CurrentWindowHeight/OriginalWindowHeight
			
			slot5[0] = slot5[0]*CurrentWindowWidth/OriginalWindowWidth
			slot5[1] = slot5[1]*CurrentWindowHeight/OriginalWindowHeight
			
			slot6[0] = slot6[0]*CurrentWindowWidth/OriginalWindowWidth
			slot6[1] = slot6[1]*CurrentWindowHeight/OriginalWindowHeight
			
			slot7[0] = slot7[0]*CurrentWindowWidth/OriginalWindowWidth
			slot7[1] = slot7[1]*CurrentWindowHeight/OriginalWindowHeight
			
			slot8[0] = slot8[0]*CurrentWindowWidth/OriginalWindowWidth
			slot8[1] = slot8[1]*CurrentWindowHeight/OriginalWindowHeight
			
			slot9[0] = slot9[0]*CurrentWindowWidth/OriginalWindowWidth
			slot9[1] = slot9[1]*CurrentWindowHeight/OriginalWindowHeight
			
			ImagePlaneWidthPixels[0]  = ImagePlaneWidthPixels[0]*CurrentWindowWidth/OriginalWindowWidth
			ImagePlaneWidthPixels[1]  = ImagePlaneWidthPixels[1]*CurrentWindowWidth/OriginalWindowWidth
			ImagePlaneHeightPixels[0] = ImagePlaneHeightPixels[0]*CurrentWindowHeight/OriginalWindowHeight
			ImagePlaneHeightPixels[1] = ImagePlaneHeightPixels[1]*CurrentWindowHeight/OriginalWindowHeight
			
			OriginalWindowWidth  = CurrentWindowWidth
			OriginalWindowHeight = CurrentWindowHeight
			
		if leftButtonStatus and dragging == False:
			if ((position.x > ImagePlaneWidthPixels[0]) and (position.x < ImagePlaneWidthPixels[1])):
				if ((position.y > ImagePlaneHeightPixels[0]) and (position.y < ImagePlaneHeightPixels[1])):
					dragging = True
					#currentPosition = position
					# Sitting the center point (Middle of the window) as the point to be dragged
					
					if not firstTime:
						CurrentClickPos[0] = position.x
						CurrentClickPos[1] = position.y
						#print "upon click", CurrentWindowWidth/2
						LastDragPosTemp[0] = LastDragPos[0]
						LastDragPosTemp[1] = LastDragPos[1]
						
						
						if slot0Clicked:
							LastDragPosTemp[0] = slot0[0]
							LastDragPosTemp[1] = slot0[1]
							slot0Clicked = False
							
						if slot1Clicked:
							LastDragPosTemp[0] = slot1[0]
							LastDragPosTemp[1] = slot1[1]
							slot1Clicked = False
							
						if slot2Clicked:
							LastDragPosTemp[0] = slot2[0]
							LastDragPosTemp[1] = slot2[1]
							slot2Clicked = False
							
						if slot3Clicked:
							LastDragPosTemp[0] = slot3[0]
							LastDragPosTemp[1] = slot3[1]
							slot3Clicked = False
							
						if slot4Clicked:
							LastDragPosTemp[0] = slot4[0]
							LastDragPosTemp[1] = slot4[1]
							slot4Clicked = False
							
						if slot5Clicked:
							LastDragPosTemp[0] = slot5[0]
							LastDragPosTemp[1] = slot5[1]
							slot5Clicked = False
							
						if slot6Clicked:
							LastDragPosTemp[0] = slot6[0]
							LastDragPosTemp[1] = slot6[1]
							slot6Clicked = False
							
						if slot7Clicked:
							LastDragPosTemp[0] = slot7[0]
							LastDragPosTemp[1] = slot7[1]
							slot7Clicked = False
							
						if slot8Clicked:
							LastDragPosTemp[0] = slot8[0]
							LastDragPosTemp[1] = slot8[1]
							slot8Clicked = False
							
						if slot9Clicked:
							LastDragPosTemp[0] = slot9[0]
							LastDragPosTemp[1] = slot9[1]
							slot9Clicked = False
							
						if ABChecked:
							CurrentClickPos[0] = 0
							CurrentClickPos[1] = 0
							LastDragPosTemp[0] = 0
							LastDragPosTemp[1] = 0
							slot0Clicked = False
							slot1Clicked = False
							slot2Clicked = False
							slot3Clicked = False
							slot4Clicked = False
							slot5Clicked = False
							slot6Clicked = False
							slot7Clicked = False
							slot8Clicked = False
							slot9Clicked = False
							firstTime = True
							ABChecked = False
							
						Upon_Click(CurrentWindowWidth/2,  CurrentWindowHeight/2)
						#print "l " , lastLength
					else:
						Upon_Click(CurrentWindowWidth/2,  CurrentWindowHeight/2)
					#return ROT_orbital
		#	return ROT_orbital # generally return ROT
		elif leftButtonStatus and dragging == True:
			#print "click ", CurrentClickPos [0]
			#print "drag ", position.x
			#print "diff ", position.x - CurrentClickPos[0]
			
			# currentPosition = position
			LastDragPos[0] = position.x
			LastDragPos[1] = position.y
			
			if not firstTime:
				#print "here2" , LastDragPosTemp[0]
				
				if (ROT_orbital.angle == 1.2217304764 and position.x - CurrentClickPos[0] > 0) or (ROT_orbital.angle == -1.2217304764 and position.x - CurrentClickPos[0] < 0):
					
					newDrag1 = LastDragPosTemp[0]
					#Upon_Drag(LastDragPosTemp[0],LastDragPosTemp[1])
				else:
					newDrag1 = LastDragPosTemp[0] + (position.x - CurrentClickPos[0])
					if newDrag1 > sceneRef.window.getValue()[0].getField('width').getValue():
						newDrag1 = sceneRef.window.getValue()[0].getField('width').getValue()
					elif newDrag1 < 0:
						newDrag1 = 0
					#print "upon drag ", newDrag1
					#Upon_Drag(newDrag1,LastDragPosTemp[1] + (position.y - CurrentClickPos[1]))
					LastDragPos[0] = newDrag1
					#LastDragPos[1] = LastDragPosTemp[1] + (position.y - CurrentClickPos[1])
				#print "l " , lastLength
			# else:
				# newDrag1 = LastDragPos[0]
				
				if (ROT_angular.angle == 1.2217304764 and position.y - CurrentClickPos[1] > 0) or (ROT_angular.angle == -1.2217304764 and position.y - CurrentClickPos[1] < 0):
					
					newDrag2 = LastDragPosTemp[1]
					#Upon_Drag(LastDragPosTemp[0],LastDragPosTemp[1])
				else:
					newDrag2 = LastDragPosTemp[1] + (position.y - CurrentClickPos[1])
					if newDrag2 > sceneRef.window.getValue()[0].getField('height').getValue():
						newDrag2 = sceneRef.window.getValue()[0].getField('height').getValue()
					elif newDrag2 < 0:
						newDrag2 = 0
					#print "upon drag ", newDrag1
					#Upon_Drag(newDrag1,LastDragPosTemp[1] + (position.y - CurrentClickPos[1]))
					LastDragPos[1] = newDrag2
					#LastDragPos[1] = LastDragPosTemp[1] + (position.y - CurrentClickPos[1])
				#print "l " , lastLength
			else:
				newDrag1 = LastDragPos[0]
				newDrag2 = LastDragPos[1]
				firstTime = False
				#print "here"
				#Upon_Drag(LastDragPos[0],LastDragPos[1])
			Upon_Drag(newDrag1, newDrag2) 	
			
			TempMat = Matrix4f(g_Transform[0][0],g_Transform[0][1],g_Transform[0][2],g_Transform[0][3],g_Transform[1][0],g_Transform[1][1],g_Transform[1][2],g_Transform[1][3],g_Transform[2][0],g_Transform[2][1],g_Transform[2][2],g_Transform[2][3],g_Transform[3][0],g_Transform[3][1],g_Transform[3][2],g_Transform[3][3])

			angleX = atan2(g_ThisRot[2][1], g_ThisRot[2][2])
			angleY = atan2(-1*g_ThisRot[2][0] , sqrt(g_ThisRot[2][1]*g_ThisRot[2][1] + g_ThisRot[2][2]*g_ThisRot[2][2]))
			angleZ = atan2(g_ThisRot[1][0],g_ThisRot[0][0])
			# print "x ", angleX , " y ", angleY, " z ", angleZ
			theta = 0		# Use only two axes X and Y. Limite Arc ball to use only X and Y
			beta  = angleY
			alpha = angleX
			#limiting angle to 70 degrees. 70 = 1.2217304764
			if beta > 1.2217304764: 
				beta = 1.2217304764 
			elif beta < -1.2217304764:
				beta = -1.2217304764 
			if alpha > 1.2217304764:
				alpha = 1.2217304764 
			elif alpha < -1.2217304764:
				alpha = -1.2217304764 
				
			#multiplied by -1 to swap RAO with LAO and Caudal with Cranial
			rotation1Slider.getField("value").setValue(-1 * beta * 180/PI)
				
			rotation2Slider.getField("value").setValue(-1 * alpha * 180/PI)
			
			r1 = [	[cos(theta)	  , sin(theta) , 0.0], 
					[-1*sin(theta), cos(theta) , 0.0], 
					[0.0				, 0.0	 , 1.0] ]
					
			r2 = [	[cos(beta)	 , 0.0, sin(beta)], 
					[0.0		  , 1.0,		0.0], 
					[-1*sin(beta), 0.0, cos(beta)] ]
					
			r3 = [	[1.0, 0.0			,		  0.0], 
					[0.0, cos(alpha)   , sin(alpha)], 
					[0.0, -1*sin(alpha), cos(alpha)] ]
					
			r3temp = r3
			r2temp = r2
			
			RotMultiplication = numpy.matmul(r1,numpy.matmul(r2,r3))
			RotMultiplication2 = numpy.matmul(r1,numpy.matmul(r2,r3))
			RotMultiplication[0][1] = -1*RotMultiplication[0][1]
			RotMultiplication[1][0] = -1*RotMultiplication[1][0]
			RotMultiplication[1][2] = -1*RotMultiplication[1][2]
			RotMultiplication[2][1] = -1*RotMultiplication[2][1]
			#print "RotMultiplication ", RotMultiplication		
			TempMat2 = Matrix4f(RotMultiplication[0][0],RotMultiplication[0][1],RotMultiplication[0][2],0,RotMultiplication[1][0],RotMultiplication[1][1],RotMultiplication[1][2],0,RotMultiplication[2][0],RotMultiplication[2][1],RotMultiplication[2][2],g_Transform[2][3],g_Transform[3][0],g_Transform[3][1],g_Transform[3][2],g_Transform[3][3])
			
			r3temp[0][1] = -1*r3temp[0][1]
			r3temp[1][0] = -1*r3temp[1][0]
			r3temp[1][2] = -1*r3temp[1][2]
			r3temp[2][1] = -1*r3temp[2][1]
			
			RotPartOfMatR3 = Matrix4f(r3temp[0][0],r3temp[0][1],r3temp[0][2],0,r3temp[1][0],r3temp[1][1],r3temp[1][2],0,r3temp[2][0],r3temp[2][1],r3temp[2][2],g_Transform[2][3],g_Transform[3][0],g_Transform[3][1],g_Transform[3][2],g_Transform[3][3])
			
			r2temp[0][1] = -1*r2temp[0][1]
			r2temp[1][0] = -1*r2temp[1][0]
			r2temp[1][2] = -1*r2temp[1][2]
			r2temp[2][1] = -1*r2temp[2][1]
			
			RotPartOfMatR2 = Matrix4f(r2temp[0][0],r2temp[0][1],r2temp[0][2],0,r2temp[1][0],r2temp[1][1],r2temp[1][2],0,r2temp[2][0],r2temp[2][1],r2temp[2][2],g_Transform[2][3],g_Transform[3][0],g_Transform[3][1],g_Transform[3][2],g_Transform[3][3])
			
			ROT = Rotation(TempMat2.getRotationPart())
			
			ROT_orbital = Rotation(RotPartOfMatR2.getRotationPart())
			ROT_orbital.z = ROT_orbital.y
			ROT_orbital.y = 0
			ROT_orbital.angle = -ROT_orbital.angle
			# sitting component z of the vector to 0 just in case
			# ROT.z = 0
			ROT_angular = Rotation(RotPartOfMatR3.getRotationPart())
			ROT_angular.z = ROT_angular.x
			ROT_angular.x = 0
			ROT_angular.angle = -ROT_angular.angle
			carmRot1.getField("rotation").setValue(ROT_orbital)
			carmRot2.getField("rotation").setValue(ROT_angular)
			
		elif not leftButtonStatus:
			dragging = False
			
		return True
			
ArcTesting = ArcBallComputationClass()

ArcTesting.route(eventSink)


