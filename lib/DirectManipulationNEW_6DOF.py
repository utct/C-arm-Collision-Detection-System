from H3DInterface import*
import time
import threading

oldPosition = None
sceneRef = None

# NEW: Mode tracking (0=Rotation, 1=Translation1, 2=Translation2/Wigwag)
currentMode = 0

def initialize():
	global sceneRef
	sceneRef = getCurrentScenes()[0]
	

def traverseSG():
	rotation1Slider 	= references.getValue()[0]  # Orbital (LAO/RAO)
	rotation2Slider 	= references.getValue()[1]  # Tilt (CRAN/CAUD)
	rotation3Slider 	= references.getValue()[2]  # Wigwag (NEW)
	translation1Slider	= references.getValue()[3]  # Lateral (X)
	translation2Slider	= references.getValue()[4]  # Horizontal (depth, NEW)
	translation3Slider	= references.getValue()[5]  # Vertical (Z)
	mouseSensor 		= references.getValue()[6]
	RotTransSwitch 		= references.getValue()[7]

	
	if mouseSensor.getField("leftButton").getValue():
		# restrict area to touchable area
		height = sceneRef.window.getValue()[0].getField('height').getValue()
		width = sceneRef.window.getValue()[0].getField('width').getValue()
		
		# these values simply stem from measurements from the view area in which the volume is shown
		allowedTouchAreaStart = (width * 0.086085, height * 0.077568)
		allowedTouchAreaEnd = (width * 0.457547, height * 0.738994)
		currentPosition = mouseSensor.getField("position").getValue()
		if currentPosition.x >= allowedTouchAreaStart[0] and currentPosition.y >= allowedTouchAreaStart[1] and currentPosition.x <= allowedTouchAreaEnd[0] and currentPosition.y <= allowedTouchAreaEnd[1]:
			global oldPosition
		
			if oldPosition != currentPosition:
				# only change something if position has changed
				oldPosition = currentPosition
				
				# NEW: Multi-mode control
				mode = getMode(RotTransSwitch)
				
				if mode == 0:  # Rotation mode (Orbital + Tilt)
					rotation1Slider.getField("value").setValue(
						rotation1Slider.getField("value").getValue() - mouseSensor.getField("motion").getValue().x
					)
					rotation2Slider.getField("value").setValue(
						rotation2Slider.getField("value").getValue() + mouseSensor.getField("motion").getValue().y
					)
					
				elif mode == 1:  # Translation mode 1 (Lateral + Vertical)
					translation1Slider.getField("value").setValue(
						translation1Slider.getField("value").getValue() - mouseSensor.getField("motion").getValue().x / 17.5
					)
					translation3Slider.getField("value").setValue(
						translation3Slider.getField("value").getValue() - mouseSensor.getField("motion").getValue().y / 17.5
					)
					
				elif mode == 2:  # Translation mode 2 (Wigwag + Horizontal depth) - NEW!
					# Horizontal drag = Wigwag rotation
					rotation3Slider.getField("value").setValue(
						rotation3Slider.getField("value").getValue() - mouseSensor.getField("motion").getValue().x
					)
					# Vertical drag = Horizontal (depth) translation
					translation2Slider.getField("value").setValue(
						translation2Slider.getField("value").getValue() - mouseSensor.getField("motion").getValue().y / 17.5
					)
	
	# Restrict c-arm movement to safe ranges
	# Rotations: -70 to 70 degrees
	if rotation1Slider.getField("value").getValue() < -70:
		rotation1Slider.getField("value").setValue(-70)
	if rotation1Slider.getField("value").getValue() > 70:
		rotation1Slider.getField("value").setValue(70)
		
	if rotation2Slider.getField("value").getValue() < -70:
		rotation2Slider.getField("value").setValue(-70)
	if rotation2Slider.getField("value").getValue() > 70:
		rotation2Slider.getField("value").setValue(70)
		
	# NEW: Wigwag limits
	if rotation3Slider.getField("value").getValue() < -70:
		rotation3Slider.getField("value").setValue(-70)
	if rotation3Slider.getField("value").getValue() > 70:
		rotation3Slider.getField("value").setValue(70)


# NEW: Get current mode based on RotTransSwitch or global mode
def getMode(RotTransSwitch):
	"""
	Mode 0: Rotation (Orbital + Tilt)
	Mode 1: Translation 1 (Lateral + Vertical)
	Mode 2: Translation 2 (Wigwag + Horizontal)
	
	The original RotTransSwitch handles mode 0 vs mode 1.
	We use global currentMode to add mode 2.
	"""
	global currentMode
	return currentMode


# NEW: Set mode explicitly
def setMode(mode):
	global currentMode
	if mode >= 0 and mode <= 2:
		currentMode = mode
		print("[Mode] Switched to mode %d: %s" % (mode, getModeName(mode)))


def getModeName(mode):
	if mode == 0:
		return "Rotation (Orbital + Tilt)"
	elif mode == 1:
		return "Translation (Lateral + Vertical)"
	else:
		return "Advanced (Wigwag + Horizontal)"


# Threading for long press implementation
threadLongPress = None
threadLongPress_stop = threading.Event()

def pressLong(buttonDirection, stop_event):
	rotation1Slider 	= references.getValue()[0]
	rotation2Slider 	= references.getValue()[1]
	rotation3Slider 	= references.getValue()[2]  # NEW
	translation1Slider	= references.getValue()[3]
	translation2Slider	= references.getValue()[4]  # NEW
	translation3Slider	= references.getValue()[5]
	RotTransSwitch 		= references.getValue()[7]

	while not stop_event.is_set():
		mode = getMode(RotTransSwitch)
		
		if mode == 0:  # Rotation mode
			if buttonDirection == 0:  # Up
				rotation2Slider.getField("value").setValue(rotation2Slider.getField("value").getValue() - 0.5)
			elif buttonDirection == 1:  # Down
				rotation2Slider.getField("value").setValue(rotation2Slider.getField("value").getValue() + 0.5)
			elif buttonDirection == 2:  # Left
				rotation1Slider.getField("value").setValue(rotation1Slider.getField("value").getValue() + 0.5)
			elif buttonDirection == 3:  # Right
				rotation1Slider.getField("value").setValue(rotation1Slider.getField("value").getValue() - 0.5)
				
		elif mode == 1:  # Translation mode 1
			if buttonDirection == 0:  # Up
				translation3Slider.getField("value").setValue(translation3Slider.getField("value").getValue() + 0.05)
			elif buttonDirection == 1:  # Down
				translation3Slider.getField("value").setValue(translation3Slider.getField("value").getValue() - 0.05)
			elif buttonDirection == 2:  # Left
				translation1Slider.getField("value").setValue(translation1Slider.getField("value").getValue() - 0.05)
			elif buttonDirection == 3:  # Right
				translation1Slider.getField("value").setValue(translation1Slider.getField("value").getValue() + 0.05)
				
		elif mode == 2:  # Translation mode 2 (NEW)
			if buttonDirection == 0:  # Up
				translation2Slider.getField("value").setValue(translation2Slider.getField("value").getValue() + 0.05)
			elif buttonDirection == 1:  # Down
				translation2Slider.getField("value").setValue(translation2Slider.getField("value").getValue() - 0.05)
			elif buttonDirection == 2:  # Left
				rotation3Slider.getField("value").setValue(rotation3Slider.getField("value").getValue() + 0.5)
			elif buttonDirection == 3:  # Right
				rotation3Slider.getField("value").setValue(rotation3Slider.getField("value").getValue() - 0.5)
		
		# Restrict movements
		if rotation1Slider.getField("value").getValue() < -70:
			rotation1Slider.getField("value").setValue(-70)
		if rotation1Slider.getField("value").getValue() > 70:
			rotation1Slider.getField("value").setValue(70)
		if rotation2Slider.getField("value").getValue() < -70:
			rotation2Slider.getField("value").setValue(-70)
		if rotation2Slider.getField("value").getValue() > 70:
			rotation2Slider.getField("value").setValue(70)
		# NEW: Wigwag limits
		if rotation3Slider.getField("value").getValue() < -70:
			rotation3Slider.getField("value").setValue(-70)
		if rotation3Slider.getField("value").getValue() > 70:
			rotation3Slider.getField("value").setValue(70)
		
		time.sleep(0.1)


class showLowRes( AutoUpdate( SFBool ) ):
	def update(self, event):
		return self.getValue()


class showHiRes( AutoUpdate( SFBool ) ):
	def update(self, event):
		return self.getValue()


class fineControlButtons2Sliders( AutoUpdate( TypedField( SFBool, ( SFBool, SFBool, SFBool, SFBool ) ) ) ):
	def update(self, event):
		rotation1Slider 	= references.getValue()[0]
		rotation2Slider 	= references.getValue()[1]
		rotation3Slider 	= references.getValue()[2]
		translation1Slider	= references.getValue()[3]
		translation2Slider	= references.getValue()[4]
		translation3Slider	= references.getValue()[5]
		mouseSensor 		= references.getValue()[6]
		RotTransSwitch 		= references.getValue()[7]

		if not event.getValue():
			threadLongPress_stop.set()
			return True
		
		threadLongPress_stop.clear()

		try:
			if self.getRoutesIn()[0].getValue():
				threadLongPress = threading.Thread(target=pressLong, args=(0, threadLongPress_stop))
				threadLongPress.start()
			if self.getRoutesIn()[1].getValue():
				threadLongPress = threading.Thread(target=pressLong, args=(1, threadLongPress_stop))
				threadLongPress.start()
			if self.getRoutesIn()[2].getValue():
				threadLongPress = threading.Thread(target=pressLong, args=(2, threadLongPress_stop))
				threadLongPress.start()
			if self.getRoutesIn()[3].getValue():
				threadLongPress = threading.Thread(target=pressLong, args=(3, threadLongPress_stop))
				threadLongPress.start()
	
		except IndexError:
			pass
		return True

		
showLowRes = showLowRes()
showHiRes = showHiRes()
showHiRes.setValue(True)
fineControlButtons2Sliders = fineControlButtons2Sliders()


# NEW: Keyboard handler for mode switching
class KeyboardHandler(AutoUpdate(SFString)):
	"""
	Press '1', '2', or '3' keys to switch modes
	"""
	def update(self, event):
		key = event.getValue()
		if key == "1":
			setMode(0)
		elif key == "2":
			setMode(1)
		elif key == "3":
			setMode(2)
		return key

keyboardHandler = KeyboardHandler()


