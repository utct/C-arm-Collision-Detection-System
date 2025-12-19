from H3DInterface import*

import math

#
# Field class that changes an SFFloat into a MFString.
#
# @route0 value of Rotation1 slider
# @return value of Rotation1 slider as string
#
class Rotation1SFFloat2MFString( TypedField( MFString, SFFloat ) ):
	def update(self, event):
		return ["%.02f" % self.getRoutesIn()[0].getValue()]
		
#
# Field class that changes an SFFloat into a MFString.
#
# @route0 value of Rotation2 slider
# @return value of Rotation2 slider as string
#
class Rotation2SFFloat2MFString( TypedField( MFString, SFFloat ) ):
	def update(self, event):
		return ["%.02f" % self.getRoutesIn()[0].getValue()]

#
# Field class that changes an SFFloat into a MFString.
#
# @route0 value of Rotation3 slider
# @return value of Rotation3 slider as string
#
class Rotation3SFFloat2MFString( TypedField( MFString, SFFloat ) ):
	def update(self, event):
		return ["%.02f" % self.getRoutesIn()[0].getValue()]
		
#
# Field class that changes an SFFloat into a MFString.
#
# @route0 value of translation slider
# @return value of translation slider as string
#
class Translation1SFFloat2MFString( TypedField( MFString, SFFloat ) ):
	def update(self, event):
		return ["%.02f" % self.getRoutesIn()[0].getValue()]

#
# Field class that changes an SFFloat into a MFString.
#
# @route0 value of translation slider
# @return value of translation slider as string
#
class Translation2SFFloat2MFString( TypedField( MFString, SFFloat ) ):
	def update(self, event):
		return ["%.02f" % self.getRoutesIn()[0].getValue()]

#
# Field class that changes an SFFloat into a MFString.
#
# @route0 value of translation slider
# @return value of translation slider as string
#
class Translation3SFFloat2MFString( TypedField( MFString, SFFloat ) ):
	def update(self, event):
		return ["%.02f" % self.getRoutesIn()[0].getValue()]

#
# Field class that changes buttonState to textual description
#
# @route0 value of button state
# @return textual description of button function
#
class buttonState2ButtonText( TypedField( MFString, SFBool ) ):
	def update(self, event):
		if self.getRoutesIn()[0].getValue():
			return ["Switch Mode", "(current Mode:", "Rotation)"]
		else:
			return ["Switch Mode", "(current Mode:", "Translation)"]

#
# Field class that transforms C-Arm position to description
#
# @route0 rotation1 of carm
# @route1 rotation2 of carm
# @route2 rotation3 of carm
# @route3 translation1 of carm
# @route4 translation2 of carm
# @route5 translation3 of carm
# @return textual decription of carm position
#
class carm2MFString( TypedField( MFString, (SFFloat, SFFloat, SFFloat, SFFloat, SFFloat, SFFloat)) ):
	def update(self, event):
		# Rotation 1 (Orbital)
		if self.getRoutesIn()[0].getValue() >= 0:
			string0 = "RAO %.1f" % math.fabs( self.getRoutesIn()[0].getValue() )
		else:
			string0 = "LAO %.1f" % math.fabs( self.getRoutesIn()[0].getValue() )
		
		# Rotation 2 (Tilt)
		if self.getRoutesIn()[1].getValue() <= 0:
			string1 = "CAU %.1f" % math.fabs( self.getRoutesIn()[1].getValue() )
		else:
			string1 = "CRA %.1f" % math.fabs( self.getRoutesIn()[1].getValue() )
		
		# Only return RAO/LAO and CAU/CRA values
		return [str(string0), str(string1)]


#
# Field classes for Table sliders
#
class TableVerticalSFFloat2MFString( TypedField( MFString, SFFloat ) ):
	def update(self, event):
		return ["%.02f cm" % self.getRoutesIn()[0].getValue()]

class TableLongitudinalSFFloat2MFString( TypedField( MFString, SFFloat ) ):
	def update(self, event):
		return ["%.02f cm" % self.getRoutesIn()[0].getValue()]

class TableTransverseSFFloat2MFString( TypedField( MFString, SFFloat ) ):
	def update(self, event):
		return ["%.02f cm" % self.getRoutesIn()[0].getValue()]


# Instantiate all field converters
Rotation1SFFloat2MFString = Rotation1SFFloat2MFString()
Rotation2SFFloat2MFString = Rotation2SFFloat2MFString()
Rotation3SFFloat2MFString = Rotation3SFFloat2MFString()
Translation1SFFloat2MFString = Translation1SFFloat2MFString()
Translation2SFFloat2MFString = Translation2SFFloat2MFString()
Translation3SFFloat2MFString = Translation3SFFloat2MFString()
TableVerticalSFFloat2MFString = TableVerticalSFFloat2MFString()
TableLongitudinalSFFloat2MFString = TableLongitudinalSFFloat2MFString()
TableTransverseSFFloat2MFString = TableTransverseSFFloat2MFString()
buttonState2ButtonText = buttonState2ButtonText()
carm2MFString = carm2MFString()
