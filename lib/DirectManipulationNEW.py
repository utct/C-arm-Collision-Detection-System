from H3DInterface import*
import time
import threading

oldPosition = None
sceneRef = None

def initialize():
	global sceneRef
	sceneRef = getCurrentScenes()[0]
	print("[DirectManipulation] Initialized - Rotation mode only")
	

def traverseSG():
	rotation1Slider 	= references.getValue()[0]
	rotation2Slider 	= references.getValue()[1]
	rotation3Slider 	= references.getValue()[2]
	translation1Slider	= references.getValue()[3]
	translation2Slider	= references.getValue()[4]
	translation3Slider	= references.getValue()[5]
	mouseSensor 		= references.getValue()[6]

	
	if mouseSensor.getField("leftButton").getValue():
		# restrict area to touchable area
		height = sceneRef.window.getValue()[0].getField('height').getValue()
		width = sceneRef.window.getValue()[0].getField('width').getValue()
		
		# these values simply stem from measurements from the view area in which the volume is shown
		allowedTouchAreaStart = (width * 0.086085, height * 0.077568)
		allowedTouchAreaEnd = (width * 0.457547, height * 0.738994)
		currentPosition = mouseSensor.getField("position").getValue()
		if currentPosition.x >= allowedTouchAreaStart[0] and currentPosition.y >= allowedTouchAreaStart[1] and currentPosition.x <= allowedTouchAreaEnd[0] and currentPosition.y <= allowedTouchAreaEnd[1]:
			#showLowRes.setValue(True)
			#showHiRes.setValue(False)
			#print mouseSensor.getField("motion").getValue()
			global oldPosition
		
			if oldPosition != currentPosition:
				# only change something if position has changed. This is necessary because 'motion' field sometimes has a non zero value, even if motion has already stopped.
				oldPosition = currentPosition
				
				# Rotation mode only (Orbital + Tilt)
				rotation1Slider.getField("value").setValue(rotation1Slider.getField("value").getValue() - mouseSensor.getField("motion").getValue().x)
				rotation2Slider.getField("value").setValue(rotation2Slider.getField("value").getValue() + mouseSensor.getField("motion").getValue().y)
	else:
		#showLowRes.setValue( False )	
		#showHiRes.setValue( True )
		pass
	
	# restrict c arm movement to values between -70 and +70 degrees
	if rotation1Slider.getField("value").getValue() < -100:
		rotation1Slider.getField("value").setValue(-100)
	if rotation1Slider.getField("value").getValue() > 100:
		rotation1Slider.getField("value").setValue(100)
	if rotation2Slider.getField("value").getValue() < -90:
		rotation2Slider.getField("value").setValue(-90)
	if rotation2Slider.getField("value").getValue() > 270:
		rotation2Slider.getField("value").setValue(270)
	# NEW: Wigwag limits
	if rotation3Slider.getField("value").getValue() < -70:
		rotation3Slider.getField("value").setValue(-70)
	if rotation3Slider.getField("value").getValue() > 70:
		rotation3Slider.getField("value").setValue(70)
	
	# Translation limits based on research paper (Table II)
	# Lateral (trans1): -5 to 5cm (adjusted for better X-ray view)
	if translation1Slider.getField("value").getValue() < -5:
		translation1Slider.getField("value").setValue(-5)
	if translation1Slider.getField("value").getValue() > 5:
		translation1Slider.getField("value").setValue(5)
	# Horizontal (trans2): -5 to 5cm (adjusted for better X-ray view)
	if translation2Slider.getField("value").getValue() < -5:
		translation2Slider.getField("value").setValue(-5)
	if translation2Slider.getField("value").getValue() > 5:
		translation2Slider.getField("value").setValue(5)
	# Vertical (trans3): 0-46cm (research: l₁ = 0.0 to 0.46m)
	if translation3Slider.getField("value").getValue() < 0:
		translation3Slider.getField("value").setValue(0)
	if translation3Slider.getField("value").getValue() > 46:
		translation3Slider.getField("value").setValue(46)		
	
# Threading for long press implementation
threadLongPress = None
threadLongPress_stop = threading.Event()

def pressLong(buttonDirection, stop_event):
	rotation1Slider 	= references.getValue()[0]
	rotation2Slider 	= references.getValue()[1]
	rotation3Slider 	= references.getValue()[2]
	translation1Slider	= references.getValue()[3]
	translation2Slider	= references.getValue()[4]
	translation3Slider	= references.getValue()[5]

	while not stop_event.is_set():
		# Rotation mode only (Orbital + Tilt)
		if buttonDirection == 0:  # Up
			rotation2Slider.getField("value").setValue(rotation2Slider.getField("value").getValue() - 0.5)
		elif buttonDirection == 1:  # Down
			rotation2Slider.getField("value").setValue(rotation2Slider.getField("value").getValue() + 0.5)
		elif buttonDirection == 2:  # Left
			rotation1Slider.getField("value").setValue(rotation1Slider.getField("value").getValue() + 0.5)
		elif buttonDirection == 3:  # Right
			rotation1Slider.getField("value").setValue(rotation1Slider.getField("value").getValue() - 0.5)
		
		# Restrict movements
		if rotation1Slider.getField("value").getValue() < -100:
			rotation1Slider.getField("value").setValue(-100)
		if rotation1Slider.getField("value").getValue() > 100:
			rotation1Slider.getField("value").setValue(100)
		if rotation2Slider.getField("value").getValue() < -90:
			rotation2Slider.getField("value").setValue(-90)
		if rotation2Slider.getField("value").getValue() > 270:
			rotation2Slider.getField("value").setValue(270)
		# Wigwag limits (research paper: θ₂ = -10° to 10°)
		if rotation3Slider.getField("value").getValue() < -10:
			rotation3Slider.getField("value").setValue(-10)
		if rotation3Slider.getField("value").getValue() > 10:
			rotation3Slider.getField("value").setValue(10)
		
		# Translation limits based on research paper (Table II)
		if translation1Slider.getField("value").getValue() < -50:
			translation1Slider.getField("value").setValue(-50)
		if translation1Slider.getField("value").getValue() > 50:
			translation1Slider.getField("value").setValue(50)
		# Horizontal: 0-15cm (research: l₃ = 0.0 to 0.15m)
		if translation2Slider.getField("value").getValue() < 0:
			translation2Slider.getField("value").setValue(0)
		if translation2Slider.getField("value").getValue() > 15:
			translation2Slider.getField("value").setValue(15)
		# Vertical: 0-46cm (research: l₁ = 0.0 to 0.46m)
		if translation3Slider.getField("value").getValue() < 0:
			translation3Slider.getField("value").setValue(0)
		if translation3Slider.getField("value").getValue() > 46:
			translation3Slider.getField("value").setValue(46)
		
		time.sleep(0.1)

#
# Field class that is accessible from x3d code: Boolean value that expresses if
# the low resolution volume is to be displayed or not. Need for this behavior
# for performance reasons.(During movement only low resolution volume is shown)
#
class showLowRes( AutoUpdate( SFBool ) ):
	def update(self, event):
		return self.getValue()

#
# Field class that is accessible from x3d code: Boolean value that expresses if
# the hi resolution volume is to be displayed or not. Need for this behavior
# for performance reasons.(During movement only low resolution volume is shown)
#
class showHiRes( AutoUpdate( SFBool ) ):
	def update(self, event):
		return self.getValue()

#
# Field class that converts button states c arm position
#
# Field class that accepts all button presses from the user interface. View is
# manipulated via reference thus return value is irrelevant
#
# @route0 value of button state Up
# @route1 value of button state Down
# @route2 value of button state Left
# @route3 value of button state Right
# @return true
#

class fineControlButtons2Sliders( AutoUpdate( TypedField( SFBool, ( SFBool, SFBool, SFBool, SFBool ) ) ) ):
	def update(self, event):
		rotation1Slider 	= references.getValue()[0]
		rotation2Slider 	= references.getValue()[1]
		rotation3Slider 	= references.getValue()[2]
		translation1Slider	= references.getValue()[3]
		translation2Slider	= references.getValue()[4]
		translation3Slider	= references.getValue()[5]
		mouseSensor 		= references.getValue()[6]

		#event is used to know if thread is already running or not
		if not event.getValue():
			threadLongPress_stop.set()
			return True;
		
		threadLongPress_stop.clear()

		try:
			if self.getRoutesIn()[0].getValue():
				# ButtonUp pressed
				threadLongPress = threading.Thread(target=pressLong, args=(0, threadLongPress_stop))
				threadLongPress.start()
			if self.getRoutesIn()[1].getValue():
				#ButtonDown pressed
				#print "ButtonDown pressed"
				threadLongPress = threading.Thread(target=pressLong, args=(1, threadLongPress_stop))
				threadLongPress.start()
			if self.getRoutesIn()[2].getValue():
				#ButtonLeft pressed
				#print "ButtonLeft pressed"
				threadLongPress = threading.Thread(target=pressLong, args=(2, threadLongPress_stop))
				threadLongPress.start()
			if self.getRoutesIn()[3].getValue():
				#ButtonRight pressed
				#print "ButtonRight pressed"
				threadLongPress = threading.Thread(target=pressLong, args=(3, threadLongPress_stop))
				threadLongPress.start()
	
		except IndexError:
			pass
		return True
		
showLowRes = showLowRes()
showHiRes = showHiRes()
showHiRes.setValue(True)
fineControlButtons2Sliders = fineControlButtons2Sliders()

# Initialize on module load
initialize()
