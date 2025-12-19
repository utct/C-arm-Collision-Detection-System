from H3DInterface import*
import math

# imports for taking screenshots. This method works only on windows if the pywin and Pillow libraries are installed
screenshot_enabled = True
try:
	import win32ui
	import win32con
	import win32gui
except ImportError:
	screenshot_enabled = False

from PIL import Image

# imports to save the drrs to the right folder
import os
import inspect
from math import cos, sin, sqrt, atan2


toplist, winlist = [], []

sceneRef = None

# method to get list of opened windows
def enum_cb(hwnd, results):
	winlist.append((hwnd, win32gui.GetWindowText(hwnd)))


def calculatePosition(beta, alpha, transform1, transform2):	
	
	beta = beta * 3.1415926536/180
	alpha = alpha * 3.1415926536/180
	
	r2 = [  [cos(beta)   , 0.0, sin(beta)], 
		 [0.0          , 1.0,        0.0], 
		 [-1*sin(beta), 0.0, cos(beta)] ]
					
	r3 = [  [1.0, 0.0           ,         0.0], 
		 [0.0, cos(alpha)   , sin(alpha)], 
		 [0.0, -1*sin(alpha), cos(alpha)] ]
	
	r2[0][1] = -1*r2[0][1]
	r2[1][0] = -1*r2[1][0]
	r2[1][2] = -1*r2[1][2]
	r2[2][1] = -1*r2[2][1]
	
	r3[0][1] = -1*r3[0][1]
	r3[1][0] = -1*r3[1][0]
	r3[1][2] = -1*r3[1][2]
	r3[2][1] = -1*r3[2][1]
	
	MatR2 = Matrix4f(r2[0][0],r2[0][1],r2[0][2],0,r2[1][0],r2[1][1],r2[1][2],0,r2[2][0],r2[2][1],r2[2][2],0,0,0,0,1)
	
	ROT_orbital = Rotation(MatR2.getRotationPart())
	ROT_orbital.z = ROT_orbital.y
	ROT_orbital.y = 0
	
	MatR3 = Matrix4f(r3[0][0],r3[0][1],r3[0][2],0,r3[1][0],r3[1][1],r3[1][2],0,r3[2][0],r3[2][1],r3[2][2],0,0,0,0,1)
	
	ROT_angular = Rotation(MatR3.getRotationPart())
	ROT_angular.z = ROT_angular.x
	ROT_angular.x = 0
	
	transform1.getField("rotation").setValue(ROT_orbital)
	transform2.getField("rotation").setValue(ROT_angular)
	 

	
#
# takes screenshot of current H3F window and saves to bitmap
#
# @param number: suffix of bitmap
# @return: path to currently taken screenshot
#
def takeScreenshot(number):
	if not screenshot_enabled:
		print("Screenshot not enabled - works only on windows platforms for now ...")
		return ""
		
	win32gui.EnumWindows(enum_cb, toplist)
	h3dwindow = [(hwnd, title) for hwnd, title in winlist if 'h3dviewer' in title.lower()]
	# just grab the hwnd for first window matching h3dviewer
	h3dwindow = h3dwindow[0]
	hwnd = h3dwindow[0]
	# this is based on http://stackoverflow.com/questions/12590942/is-there-any-better-way-to-capture-the-screen-than-pil-imagegrab-grab
	bbox = win32gui.GetWindowRect(hwnd)
	hwin = win32gui.GetDesktopWindow()
	hwindc = win32gui.GetWindowDC(hwin)
	srcdc = win32ui.CreateDCFromHandle(hwindc)
	memdc = srcdc.CreateCompatibleDC()
	bmp = win32ui.CreateBitmap()
	bmp.CreateCompatibleBitmap(srcdc, bbox[2]-bbox[0], bbox[3]-bbox[1])
	memdc.SelectObject(bmp)
	memdc.BitBlt((0, 0), (bbox[2]-bbox[0], bbox[3]-bbox[1]), srcdc, (bbox[0], bbox[1]), win32con.SRCCOPY)
	filename = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + "\\drrs\\img{}.bmp".format(number)
	bmp.SaveBitmapFile(memdc, filename)
	return filename


#
# crops image so that only x-ray circle is visible and saves to png
# 
# @param path: path to screenshot to be cropped
# @param number: suffix of png
# @return: path to cropped screenshot
#
def cropImage(path, number):	
	img = Image.open(path)
	if img.size[0] == sceneRef.window.getValue()[0].getField('width').getValue() and img.size[1] == sceneRef.window.getValue()[0].getField('height').getValue():
		# Fullscreen mode - zoomed in tighter to exclude all HUD elements
		box = (int(0.12*img.size[0]), int(0.18*img.size[1]), int(0.38*img.size[0]), int(0.68*img.size[1]))
		region = img.crop(box)
		filename = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + "\\drrs\\img{}.png".format(number)
		region.save(filename)
		return filename
	else:
		# Windowed mode - zoomed in tighter to exclude all HUD elements  
		box = (int(0.13*img.size[0]), int(0.22*img.size[1]), int(0.37*img.size[0]), int(0.65*img.size[1]))
		region = img.crop(box)
		filename = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + "\\drrs\\img{}.png".format(number)
		region.save(filename)
		return filename

button0InUse = False
button1InUse = False
button2InUse = False
button3InUse = False
button4InUse = False
button5InUse = False
button6InUse = False
button7InUse = False
button8InUse = False
button9InUse = False


pos0_rotation1Slider = 0
pos0_rotation2Slider = 0
pos0_rotation3Slider = 0 
pos0_translation1Slider = 0
pos0_translation2Slider = 0
pos0_translation3Slider = 0

pos1_rotation1Slider = 0
pos1_rotation2Slider = 0
pos1_rotation3Slider = 0 
pos1_translation1Slider = 0
pos1_translation2Slider = 0
pos1_translation3Slider = 0

pos2_rotation1Slider = 0
pos2_rotation2Slider = 0
pos2_rotation3Slider = 0 
pos2_translation1Slider = 0
pos2_translation2Slider = 0
pos2_translation3Slider = 0

pos3_rotation1Slider = 0
pos3_rotation2Slider = 0
pos3_rotation3Slider = 0 
pos3_translation1Slider = 0
pos3_translation2Slider = 0
pos3_translation3Slider = 0

pos4_rotation1Slider = 0
pos4_rotation2Slider = 0
pos4_rotation3Slider = 0 
pos4_translation1Slider = 0
pos4_translation2Slider = 0
pos4_translation3Slider = 0

pos5_rotation1Slider = 0
pos5_rotation2Slider = 0
pos5_rotation3Slider = 0 
pos5_translation1Slider = 0
pos5_translation2Slider = 0
pos5_translation3Slider = 0

pos6_rotation1Slider = 0
pos6_rotation2Slider = 0
pos6_rotation3Slider = 0 
pos6_translation1Slider = 0
pos6_translation2Slider = 0
pos6_translation3Slider = 0

pos7_rotation1Slider = 0
pos7_rotation2Slider = 0
pos7_rotation3Slider = 0 
pos7_translation1Slider = 0
pos7_translation2Slider = 0
pos7_translation3Slider = 0

pos8_rotation1Slider = 0
pos8_rotation2Slider = 0
pos8_rotation3Slider = 0 
pos8_translation1Slider = 0
pos8_translation2Slider = 0
pos8_translation3Slider = 0

pos9_rotation1Slider = 0
pos9_rotation2Slider = 0
pos9_rotation3Slider = 0 
pos9_translation1Slider = 0
pos9_translation2Slider = 0
pos9_translation3Slider = 0

def initialize():
	global sceneRef
	sceneRef = getCurrentScenes()[0]
	
	texture0 = references.getValue()[13]
	texture1 = references.getValue()[14]
	texture2 = references.getValue()[15]
	texture3 = references.getValue()[16]
	texture4 = references.getValue()[17]
	texture5 = references.getValue()[18]
	texture6 = references.getValue()[19]
	texture7 = references.getValue()[28]
	texture8 = references.getValue()[31]
	texture9 = references.getValue()[34]
	

# 
# save current C-arm position to button which is pressed if button is not
# already used or moves C-arm to defined position of already in use
#
# Return value is irrelevant but is needed as this is AutoUpdate
#
# @route0 value of button0
# @route1 value of button1
# @route2 value of button2
# @route3 value of button3
# @route4 value of button4
# @route5 value of button5
# @route6 value of button6
# @return true if successful
# 
class positionButtons( AutoUpdate(TypedField( SFBool, (SFBool, SFBool, SFBool, SFBool, SFBool, SFBool, SFBool, SFBool, SFBool, SFBool) ) ) ):
	def update(self, event):
		try:
			routes_in = self.getRoutesIn()
			button0Press = routes_in[0].getValue()
			button1Press = routes_in[1].getValue()
			button2Press = routes_in[2].getValue()
			button3Press = routes_in[3].getValue()
			button4Press = routes_in[4].getValue()
			button5Press = routes_in[5].getValue()
			button6Press = routes_in[6].getValue()
			button7Press = routes_in[7].getValue()
			button8Press = routes_in[8].getValue()
			button9Press = routes_in[9].getValue()

			rotation1Slider		= references.getValue()[0]
			rotation2Slider		= references.getValue()[1]
			rotation3Slider		= references.getValue()[2]
			translation1Slider	= references.getValue()[3]
			translation2Slider	= references.getValue()[4]
			translation3Slider	= references.getValue()[5]
			
			label0 = references.getValue()[6]
			label1 = references.getValue()[7]
			label2 = references.getValue()[8]
			label3 = references.getValue()[9]
			label4 = references.getValue()[10]
			label5 = references.getValue()[11]
			label6 = references.getValue()[12]
			label7 = references.getValue()[27]
			label8 = references.getValue()[30]
			label9 = references.getValue()[33]
			
			texture0 = references.getValue()[13]
			texture1 = references.getValue()[14]
			texture2 = references.getValue()[15]
			texture3 = references.getValue()[16]
			texture4 = references.getValue()[17]
			texture5 = references.getValue()[18]
			texture6 = references.getValue()[19]
			texture7 = references.getValue()[28]
			texture8 = references.getValue()[31]
			texture9 = references.getValue()[34]
			
			touch0 = references.getValue()[20]
			touch1 = references.getValue()[21]
			touch2 = references.getValue()[22]
			touch3 = references.getValue()[23]
			touch4 = references.getValue()[24]
			touch5 = references.getValue()[25]
			touch6 = references.getValue()[26]
			touch7 = references.getValue()[29]
			touch8 = references.getValue()[32]
			touch9 = references.getValue()[35]
			
			
			CarmOrbital = references.getValue()[36]
			CarmAngular = references.getValue()[37]
			
			global button0InUse
			global button1InUse
			global button2InUse
			global button3InUse
			global button4InUse
			global button5InUse
			global button6InUse
			global button7InUse
			global button8InUse
			global button9InUse
			
			
			global pos0_rotation1Slider 
			global pos0_rotation2Slider 
			global pos0_rotation3Slider 
			global pos0_translation1Slider
			global pos0_translation2Slider
			global pos0_translation3Slider

			global pos1_rotation1Slider 
			global pos1_rotation2Slider 
			global pos1_rotation3Slider 
			global pos1_translation1Slider
			global pos1_translation2Slider
			global pos1_translation3Slider

			global pos2_rotation1Slider 
			global pos2_rotation2Slider 
			global pos2_rotation3Slider 
			global pos2_translation1Slider
			global pos2_translation2Slider
			global pos2_translation3Slider

			global pos3_rotation1Slider 
			global pos3_rotation2Slider 
			global pos3_rotation3Slider 
			global pos3_translation1Slider
			global pos3_translation2Slider
			global pos3_translation3Slider

			global pos4_rotation1Slider 
			global pos4_rotation2Slider 
			global pos4_rotation3Slider 
			global pos4_translation1Slider
			global pos4_translation2Slider
			global pos4_translation3Slider

			global pos5_rotation1Slider
			global pos5_rotation2Slider 
			global pos5_rotation3Slider 
			global pos5_translation1Slider
			global pos5_translation2Slider
			global pos5_translation3Slider

			global pos6_rotation1Slider 
			global pos6_rotation2Slider
			global pos6_rotation3Slider 
			global pos6_translation1Slider
			global pos6_translation2Slider
			global pos6_translation3Slider

			global pos7_rotation1Slider 
			global pos7_rotation2Slider
			global pos7_rotation3Slider 
			global pos7_translation1Slider
			global pos7_translation2Slider
			global pos7_translation3Slider

			global pos8_rotation1Slider 
			global pos8_rotation2Slider
			global pos8_rotation3Slider 
			global pos8_translation1Slider
			global pos8_translation2Slider
			global pos8_translation3Slider

			global pos9_rotation1Slider 
			global pos9_rotation2Slider
			global pos9_rotation3Slider 
			global pos9_translation1Slider
			global pos9_translation2Slider
			global pos9_translation3Slider

			if button0Press:
				if button0InUse:
					rotation1Slider.getField("value").setValue(pos0_rotation1Slider)
					rotation2Slider.getField("value").setValue(pos0_rotation2Slider)
					rotation3Slider.getField("value").setValue(pos0_rotation3Slider)
					translation1Slider.getField("value").setValue(pos0_translation1Slider)
					translation2Slider.getField("value").setValue(pos0_translation2Slider)
					translation3Slider.getField("value").setValue(pos0_translation3Slider)
					calculatePosition(pos0_rotation1Slider, pos0_rotation2Slider, CarmOrbital, CarmAngular)
				else:
					button0InUse = True
					pos0_rotation1Slider = rotation1Slider.getField("value").getValue()
					pos0_rotation2Slider = rotation2Slider.getField("value").getValue()
					pos0_rotation3Slider = rotation3Slider.getField("value").getValue()
					pos0_translation1Slider = translation1Slider.getField("value").getValue()
					pos0_translation2Slider = translation2Slider.getField("value").getValue()
					pos0_translation3Slider = translation3Slider.getField("value").getValue()
					label0.getField("text").setValue(carmSliders2StringList(pos0_rotation1Slider, pos0_rotation2Slider, pos0_rotation3Slider, pos0_translation1Slider, pos0_translation2Slider, pos0_translation3Slider))
					imgFile = takeScreenshot(0)
					tex = cropImage(imgFile, 0)
					texture0.getField("url").setValue([tex])
					touch0.getField("text").setValue([""])
			if button1Press:
				if button1InUse:
					rotation1Slider.getField("value").setValue(pos1_rotation1Slider)
					rotation2Slider.getField("value").setValue(pos1_rotation2Slider)
					rotation3Slider.getField("value").setValue(pos1_rotation3Slider)
					translation1Slider.getField("value").setValue(pos1_translation1Slider)
					translation2Slider.getField("value").setValue(pos1_translation2Slider)
					translation3Slider.getField("value").setValue(pos1_translation3Slider)
					calculatePosition(pos1_rotation1Slider, pos1_rotation2Slider, CarmOrbital, CarmAngular)
				else:
					button1InUse = True
					pos1_rotation1Slider = rotation1Slider.getField("value").getValue()
					pos1_rotation2Slider = rotation2Slider.getField("value").getValue()
					pos1_rotation3Slider = rotation3Slider.getField("value").getValue()
					pos1_translation1Slider = translation1Slider.getField("value").getValue()
					pos1_translation2Slider = translation2Slider.getField("value").getValue()
					pos1_translation3Slider = translation3Slider.getField("value").getValue()
					label1.getField("text").setValue(carmSliders2StringList(pos1_rotation1Slider, pos1_rotation2Slider, pos1_rotation3Slider, pos1_translation1Slider, pos1_translation2Slider, pos1_translation3Slider))
					imgFile = takeScreenshot(1)
					tex = cropImage(imgFile, 1)
					texture1.getField("url").setValue([tex])
					touch1.getField("text").setValue([""])
			if button2Press:
				if button2InUse:
					rotation1Slider.getField("value").setValue(pos2_rotation1Slider)
					rotation2Slider.getField("value").setValue(pos2_rotation2Slider)
					rotation3Slider.getField("value").setValue(pos2_rotation3Slider)
					translation1Slider.getField("value").setValue(pos2_translation1Slider)
					translation2Slider.getField("value").setValue(pos2_translation2Slider)
					translation3Slider.getField("value").setValue(pos2_translation3Slider)
					calculatePosition(pos2_rotation1Slider, pos2_rotation2Slider, CarmOrbital, CarmAngular)
				else:
					button2InUse = True
					pos2_rotation1Slider = rotation1Slider.getField("value").getValue()
					pos2_rotation2Slider = rotation2Slider.getField("value").getValue()
					pos2_rotation3Slider = rotation3Slider.getField("value").getValue()
					pos2_translation1Slider = translation1Slider.getField("value").getValue()
					pos2_translation2Slider = translation2Slider.getField("value").getValue()
					pos2_translation3Slider = translation3Slider.getField("value").getValue()
					label2.getField("text").setValue(carmSliders2StringList(pos2_rotation1Slider, pos2_rotation2Slider, pos2_rotation3Slider, pos2_translation1Slider, pos2_translation2Slider, pos2_translation3Slider))
					imgFile = takeScreenshot(2)
					tex = cropImage(imgFile, 2)
					texture2.getField("url").setValue([tex])
					touch2.getField("text").setValue([""])
			if button3Press:
				if button3InUse:
					rotation1Slider.getField("value").setValue(pos3_rotation1Slider)
					rotation2Slider.getField("value").setValue(pos3_rotation2Slider)
					rotation3Slider.getField("value").setValue(pos3_rotation3Slider)
					translation1Slider.getField("value").setValue(pos3_translation1Slider)
					translation2Slider.getField("value").setValue(pos3_translation2Slider)
					translation3Slider.getField("value").setValue(pos3_translation3Slider)
					calculatePosition(pos3_rotation1Slider, pos3_rotation2Slider, CarmOrbital, CarmAngular)
				else:
					button3InUse = True
					pos3_rotation1Slider = rotation1Slider.getField("value").getValue()
					pos3_rotation2Slider = rotation2Slider.getField("value").getValue()
					pos3_rotation3Slider = rotation3Slider.getField("value").getValue()
					pos3_translation1Slider = translation1Slider.getField("value").getValue()
					pos3_translation2Slider = translation2Slider.getField("value").getValue()
					pos3_translation3Slider = translation3Slider.getField("value").getValue()
					label3.getField("text").setValue(carmSliders2StringList(pos3_rotation1Slider, pos3_rotation2Slider, pos3_rotation3Slider, pos3_translation1Slider, pos3_translation2Slider, pos3_translation3Slider))
					imgFile = takeScreenshot(3)
					tex = cropImage(imgFile, 3)
					texture3.getField("url").setValue([tex])
					touch3.getField("text").setValue([""])
			if button4Press:
				if button4InUse:
					rotation1Slider.getField("value").setValue(pos4_rotation1Slider)
					rotation2Slider.getField("value").setValue(pos4_rotation2Slider)
					rotation3Slider.getField("value").setValue(pos4_rotation3Slider)
					translation1Slider.getField("value").setValue(pos4_translation1Slider)
					translation2Slider.getField("value").setValue(pos4_translation2Slider)
					translation3Slider.getField("value").setValue(pos4_translation3Slider)
					calculatePosition(pos4_rotation1Slider, pos4_rotation2Slider, CarmOrbital, CarmAngular)
				else:
					button4InUse = True
					pos4_rotation1Slider = rotation1Slider.getField("value").getValue()
					pos4_rotation2Slider = rotation2Slider.getField("value").getValue()
					pos4_rotation3Slider = rotation3Slider.getField("value").getValue()
					pos4_translation1Slider = translation1Slider.getField("value").getValue()
					pos4_translation2Slider = translation2Slider.getField("value").getValue()
					pos4_translation3Slider = translation3Slider.getField("value").getValue()
					label4.getField("text").setValue(carmSliders2StringList(pos4_rotation1Slider, pos4_rotation2Slider, pos4_rotation3Slider, pos4_translation1Slider, pos4_translation2Slider, pos4_translation3Slider))
					imgFile = takeScreenshot(4)
					tex = cropImage(imgFile, 4)
					texture4.getField("url").setValue([tex])
					touch4.getField("text").setValue([""])
			if button5Press:
				if button5InUse:
					rotation1Slider.getField("value").setValue(pos5_rotation1Slider)
					rotation2Slider.getField("value").setValue(pos5_rotation2Slider)
					rotation3Slider.getField("value").setValue(pos5_rotation3Slider)
					translation1Slider.getField("value").setValue(pos5_translation1Slider)
					translation2Slider.getField("value").setValue(pos5_translation2Slider)
					translation3Slider.getField("value").setValue(pos5_translation3Slider)
					calculatePosition(pos5_rotation1Slider, pos5_rotation2Slider, CarmOrbital, CarmAngular)
				else:
					button5InUse = True
					pos5_rotation1Slider = rotation1Slider.getField("value").getValue()
					pos5_rotation2Slider = rotation2Slider.getField("value").getValue()
					pos5_rotation3Slider = rotation3Slider.getField("value").getValue()
					pos5_translation1Slider = translation1Slider.getField("value").getValue()
					pos5_translation2Slider = translation2Slider.getField("value").getValue()
					pos5_translation3Slider = translation3Slider.getField("value").getValue()
					label5.getField("text").setValue(carmSliders2StringList(pos5_rotation1Slider, pos5_rotation2Slider, pos5_rotation3Slider, pos5_translation1Slider, pos5_translation2Slider, pos5_translation3Slider))
					imgFile = takeScreenshot(5)
					tex = cropImage(imgFile, 5)
					texture5.getField("url").setValue([tex])
					touch5.getField("text").setValue([""])
			if button6Press:
				if button6InUse:
					rotation1Slider.getField("value").setValue(pos6_rotation1Slider)
					rotation2Slider.getField("value").setValue(pos6_rotation2Slider)
					rotation3Slider.getField("value").setValue(pos6_rotation3Slider)
					translation1Slider.getField("value").setValue(pos6_translation1Slider)
					translation2Slider.getField("value").setValue(pos6_translation2Slider)
					translation3Slider.getField("value").setValue(pos6_translation3Slider)
					calculatePosition(pos6_rotation1Slider, pos6_rotation2Slider, CarmOrbital, CarmAngular)
				else:
					button6InUse = True
					pos6_rotation1Slider = rotation1Slider.getField("value").getValue()
					pos6_rotation2Slider = rotation2Slider.getField("value").getValue()
					pos6_rotation3Slider = rotation3Slider.getField("value").getValue()
					pos6_translation1Slider = translation1Slider.getField("value").getValue()
					pos6_translation2Slider = translation2Slider.getField("value").getValue()
					pos6_translation3Slider = translation3Slider.getField("value").getValue()
					label6.getField("text").setValue(carmSliders2StringList(pos6_rotation1Slider, pos6_rotation2Slider, pos6_rotation3Slider, pos6_translation1Slider, pos6_translation2Slider, pos6_translation3Slider))
					imgFile = takeScreenshot(6)
					tex = cropImage(imgFile, 6)
					texture6.getField("url").setValue([tex])
					touch6.getField("text").setValue([""])
			if button7Press:
				if button7InUse:
					rotation1Slider.getField("value").setValue(pos7_rotation1Slider)
					rotation2Slider.getField("value").setValue(pos7_rotation2Slider)
					rotation3Slider.getField("value").setValue(pos7_rotation3Slider)
					translation1Slider.getField("value").setValue(pos7_translation1Slider)
					translation2Slider.getField("value").setValue(pos7_translation2Slider)
					translation3Slider.getField("value").setValue(pos7_translation3Slider)
					calculatePosition(pos7_rotation1Slider, pos7_rotation2Slider, CarmOrbital, CarmAngular)
				else:
					button7InUse = True
					pos7_rotation1Slider = rotation1Slider.getField("value").getValue()
					pos7_rotation2Slider = rotation2Slider.getField("value").getValue()
					pos7_rotation3Slider = rotation3Slider.getField("value").getValue()
					pos7_translation1Slider = translation1Slider.getField("value").getValue()
					pos7_translation2Slider = translation2Slider.getField("value").getValue()
					pos7_translation3Slider = translation3Slider.getField("value").getValue()
					label7.getField("text").setValue(carmSliders2StringList(pos7_rotation1Slider, pos7_rotation2Slider, pos7_rotation3Slider, pos7_translation1Slider, pos7_translation2Slider, pos7_translation3Slider))
					imgFile = takeScreenshot(7)
					tex = cropImage(imgFile, 7)
					texture7.getField("url").setValue([tex])
					touch7.getField("text").setValue([""])
			if button8Press:
				if button8InUse:
					rotation1Slider.getField("value").setValue(pos8_rotation1Slider)
					rotation2Slider.getField("value").setValue(pos8_rotation2Slider)
					rotation3Slider.getField("value").setValue(pos8_rotation3Slider)
					translation1Slider.getField("value").setValue(pos8_translation1Slider)
					translation2Slider.getField("value").setValue(pos8_translation2Slider)
					translation3Slider.getField("value").setValue(pos8_translation3Slider)
					calculatePosition(pos8_rotation1Slider, pos8_rotation2Slider, CarmOrbital, CarmAngular)
				else:
					button8InUse = True
					pos8_rotation1Slider = rotation1Slider.getField("value").getValue()
					pos8_rotation2Slider = rotation2Slider.getField("value").getValue()
					pos8_rotation3Slider = rotation3Slider.getField("value").getValue()
					pos8_translation1Slider = translation1Slider.getField("value").getValue()
					pos8_translation2Slider = translation2Slider.getField("value").getValue()
					pos8_translation3Slider = translation3Slider.getField("value").getValue()
					label8.getField("text").setValue(carmSliders2StringList(pos8_rotation1Slider, pos8_rotation2Slider, pos8_rotation3Slider, pos8_translation1Slider, pos8_translation2Slider, pos8_translation3Slider))
					imgFile = takeScreenshot(8)
					tex = cropImage(imgFile, 8)
					texture8.getField("url").setValue([tex])
					touch8.getField("text").setValue([""])
			if button9Press:
				if button9InUse:
					rotation1Slider.getField("value").setValue(pos9_rotation1Slider)
					rotation2Slider.getField("value").setValue(pos9_rotation2Slider)
					rotation3Slider.getField("value").setValue(pos9_rotation3Slider)
					translation1Slider.getField("value").setValue(pos9_translation1Slider)
					translation2Slider.getField("value").setValue(pos9_translation2Slider)
					translation3Slider.getField("value").setValue(pos9_translation3Slider)
					calculatePosition(pos9_rotation1Slider, pos9_rotation2Slider, CarmOrbital, CarmAngular)
				else:
					button9InUse = True
					pos9_rotation1Slider = rotation1Slider.getField("value").getValue()
					pos9_rotation2Slider = rotation2Slider.getField("value").getValue()
					pos9_rotation3Slider = rotation3Slider.getField("value").getValue()
					pos9_translation1Slider = translation1Slider.getField("value").getValue()
					pos9_translation2Slider = translation2Slider.getField("value").getValue()
					pos9_translation3Slider = translation3Slider.getField("value").getValue()
					label9.getField("text").setValue(carmSliders2StringList(pos9_rotation1Slider, pos9_rotation2Slider, pos9_rotation3Slider, pos9_translation1Slider, pos9_translation2Slider, pos9_translation3Slider))
					imgFile = takeScreenshot(9)
					tex = cropImage(imgFile, 9)
					texture9.getField("url").setValue([tex])
					touch9.getField("text").setValue([""])


		except IndexError:
			pass

		return True	
#
# converts current c-arm position to textual representation
#
# @route0 rotation1 of carm
# @route1 rotation2 of carm
# @route2 rotation3 of carm
# @route3 translation1 of carm
# @route4 translation2 of carm
# @route5 translation3 of carm
# @return textual decription of carm position
#	
def carmSliders2StringList(rot1, rot2, rot3, trans1, trans2, trans3):
	string0 = None
	string1 = None
	if rot1 >= 0:
		string0 = "RAO {}".format(int(math.fabs(rot1)))
	else:
		string0 = "LAO {}".format(int(math.fabs(rot1)))
	if rot2 <= 0:
		string1 = ", caudal {}".format(int(math.fabs(rot2)))
	else:
		string1 = ", cranial {}".format(int(math.fabs(rot2)))
	return [str(string0) + str(string1)]

positionButtons = positionButtons()
