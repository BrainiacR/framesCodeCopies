#View Port
from luma.core.interface.serial import spi
from luma.core.virtual import viewport
import luma.oled.device
from luma.oled.device import ssd1351
from PIL import Image, ImageDraw
import time
import RPi.GPIO as GPIO
import datetime

#TrackBall
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
Trackball = [5,6,13,19]
SW = 23
GPIO.setup(Trackball, GPIO.IN)
GPIO.setup(SW, GPIO.IN)
Trackballindex = 1
TOPINDEX = 0
Array = []

framesize = (128,128)
Serial = spi(device = 0, port = 0)
device = ssd1351(Serial,128,128,1,'diff_to_previous',0,0,True)
actWindowsize = viewport(device, width = 320, height = 726)
#ObjectImage = ["Sources", (SizeX,SizeY),(LocationX,LocationY), (SelLoc1X, SelLoc1Y, SelLoc2X, SelLoc2Y), ContextSensitive menu array] If Possible to be selected
#Splash Screen Resources
FramesLogo = ["framesResources/FramesLogo01.png", (70,27), (30,90)]
Logo = ["framesResources/CELogo01.jpg",(128,128),(0,0),(0,0,0,0)]
#Fillers
Filler = ("framesResources/CELogo01.jpg", (1,1),(0,0),(0,0,0,0))
OptionFiller = ()
#Dev Bar Resources
Power = ("framesResources/PowerIcon01.jpg", (10,10), (114,6),(113,5,124,16))
Wifi = ("framesResources/WifiIcon01.jpg", (12,12), (97,5),(96,3,110,18))
Battery = ["framesResources/BatteryIcon01.jpg", (20,20), (2,2)]
Bluetooth = ("framesResources/BluetoothIcon01.jpg", (14,14) , (82,4),(81,3,93,17))
#Trackball arrays
SplashScrnSel = (Bluetooth, Wifi, Power, Filler)
#Resource Draws
DevBar = [Power, Wifi, Battery, Bluetooth]
SplashScrn = (Logo, FramesLogo)
#Screen Context
Context = "Splash"
ScreenContext = SplashScrn
ScreenSelectContext = SplashScrnSel
#Button Context
ButtonSel = False
BContext = Filler
#Option Context
OpContext = OptionFiller
OpSel = False
#Click
ClickState = True
#Context Sensitive Menus
#Class for CSM
class ContextMenu(object):
	def __init__(Self, Title, Size, Location, BackgroundColor, Options, Canvas, Screen, Arr):
		Self.Size = Size
		Self.Location = Location
		Self.BackgroundColor = BackgroundColor
		Self.Options = Options
		Self.Canvas = Canvas
		Self.Screen = Screen
		Self.Arr = Arr
		Self.Title = Title

	def Draw(Self):
		#Draw Rectangle at Location
		draw = ImageDraw.Draw(Self.Canvas)
		draw.rectangle((Self.Location, Self.Location[0] + Self.Size[0], Self.Location[1] + Self.Size[1]), fill = Self.BackgroundColor)
		OptionInteger = 10
		draw.text((Self.Location[0], Self.Location[1]), Self.Title, fill = "black")
		for Option in Self.Options:
			draw.text((Self.Location[0], Self.Location[1] + OptionInteger), Option[0], fill = "black")
			OptionInteger += 10
		del draw
		device.display(Self.Canvas)

RunOnce = 1
def Persist():
	x = 1
CSM = ContextMenu("UN", (0,0), (0,0), (0,0,0) , [("nothing")], 1, SplashScrn, Array)
#Draw Init Canvas
Canvas = Image.new("RGB", framesize, (255,255,255))

def DrawScreen(Canvas, Screen, Arr, TOPindex):
	global Array
	global TOPINDEX
	global ScreenContext
	ScreenContext = Screen
	ScreenSelectContext = Arr
	TOPINDEX = TOPindex
	Array = Arr
	#Draw Image 'Canvas'
	for imageObject in Screen:
		#create temp image and open the file 
		tmpimg = Image.open(imageObject[0])
		#resize image
		tmpimg = tmpimg.resize(imageObject[1])
		#convert image to RGBA if it wasnt already
		tmpimg = tmpimg.convert("RGBA")
		#paste the image on the splash with mask of the image
		Canvas.paste(tmpimg, imageObject[2], tmpimg)

def DrawDevBar(Canvas):
	draw = ImageDraw.Draw(Canvas)
	draw.rectangle((0,22,128,23),(0,0,0))
	del draw
	for imageObject in DevBar:
		tmpimg = Image.open(imageObject[0])
		tmpimg = tmpimg.resize(imageObject[1])
		tmpimg = tmpimg.convert("RGBA")
		tmpimg.putalpha(255)
		Canvas.paste(tmpimg, imageObject[2], tmpimg)


def CheckBatt(Canvas):
	#Code for checking battery percentage
	BattX = 0
	BattMaxX = 17
	fillColor = "green"
	BattPercentage = 100
	#Just for testing because the code for checking bat percent and the calculation is not there
	BattX =15
	BattPercentage = (int)((BattX/BattMaxX) * 100)
	if(BattX < 5):
		fillColor = "red"
	elif(BattX <= 10):
		fillColor = "orange"
	else:
		fillColor = "green"

	draw = ImageDraw.Draw(Canvas)
	draw.rectangle((4,8,BattX,15), fill = fillColor)
	draw.text((24,8),str(BattPercentage) +"%",fill = "black")
	del draw

def upCallback(channel):
	global Trackballindex
	global Canvas
	global Array
	global TOPINDEX
	global BContext
	CurIndex = 0
	PrevIndex = 0
	Trackballindex += 1
	if(Trackballindex > TOPINDEX - 1):
		Trackballindex = 0
		CurIndex = Trackballindex
		PrevIndex = TOPINDEX - 1
	else:
		CurIndex = Trackballindex
		PrevIndex = Trackballindex - 1

	CurImage = Array[CurIndex]
	BContext = CurImage
	PrevImage = Array[PrevIndex]
	SelectionBox(Canvas, PrevImage, CurImage)
	print("Up Call Back Fired")

def downCallback(channel):
	global ClickState
	if(ClickState!= True):
		EnableClick()
	global Trackballindex
	global Canvas
	global Array
	global TOPINDEX
	global BContext
	global OpContext
	global OpSel
	CurIndex = 0
	PrevIndex = 0
	Trackballindex -=1
	if(Trackballindex < 0):
		Trackballindex = TOPINDEX - 1
		CurIndex = Trackballindex
		PrevIndex = 0
	else:
		CurIndex = Trackballindex
		PrevIndex = Trackballindex + 1

	if(ButtonSel == False):
		CurImage = Array[CurIndex]
		BContext = CurImage
		PrevImage = Array[PrevIndex]
		SelectionBox(Canvas, PrevImage, CurImage)
	else:
		CurOption = Array[CurIndex]
		OpContext = CurOption
		OpSel = True
		if(TOPINDEX != 1):
			PrevOption = Array[PrevIndex]
		else:
			PrevOption = Array[CurIndex]
		OptionSelBox(Canvas, PrevOption, CurOption, CurIndex, PrevIndex)
	print("Down Call Back Fired")

def clickCallback(channel):
	global BContext
	print("Click call back fired")
	if(ButtonSel == False):
		checkButton(BContext)
	elif(OpSel == True):
		OpContext[1]()

def OptionSelBox(Canvas, PrevOption, CurOption, CurIndex, PrevIndex):
	draw = ImageDraw.Draw(Canvas)
	#draw rectangle over Current option
	draw.rectangle((CSM.Location[0], CSM.Location[1] + CurIndex * 10 + 10, CSM.Location[0] + CSM.Size[0], CSM.Location[1] + (CurIndex * 10) + 20), fill = "purple")
	draw.text((CSM.Location[0], CSM.Location[1] + CurIndex * 10 + 10),Array[CurIndex][0], fill = "orange")
	if(len(Array) != 1):
		#Erase rectangle over last option and repaste text
		draw.rectangle((CSM.Location[0], CSM.Location[1] + PrevIndex * 10 + 10, CSM.Location[0] + CSM.Size[0], CSM.Location[1] + (PrevIndex * 10) + 20), fill = "white")
		draw.text((CSM.Location[0], CSM.Location[1] + PrevIndex * 10 + 10), Array[PrevIndex][0], fill = "black")
	device.display(Canvas)

def SelectionBox(Canvas, PrevImage, CurImage):
	draw = ImageDraw.Draw(Canvas)
	#Erase the Selection Box around the old image
	draw.rectangle(PrevImage[3], fill = "white")
	#Repaste the old image
	tmpPrev = Image.open(PrevImage[0])
	tmpPrev = tmpPrev.resize(PrevImage[1])
	tmpPrev = tmpPrev.convert("RGBA")
	tmpPrev.putalpha(255)
	Canvas.paste(tmpPrev, PrevImage[2], tmpPrev)
	#Draw Box Around New Image
	draw.rectangle(CurImage[3], fill = "purple")
	#Paste new Image on top of selection box
	tmpCur = Image.open(CurImage[0])
	tmpCur = tmpCur.resize(CurImage[1])
	tmpCur = tmpCur.convert("RGBA")	
	tmpCur.putalpha(255)
	Canvas.paste(tmpCur, CurImage[2], tmpCur)
	device.display(Canvas)

def checkScreen(Context):
	if(Context == "Splash"):
		DrawScreen(Canvas, SplashScrn, SplashScrnSel, len(SplashScrnSel))

def DisableClick():
	GPIO.remove_event_detect(SW)
	global ClickState
	ClickState = False

def EnableClick():
	GPIO.add_event_detect(SW, GPIO.RISING)
	GPIO.add_event_callback(SW, clickCallback)
	global ClickState
	ClickState = True

def CloseContextMenu():
	print("Closed CSM")
	global ButtonSel
	global OpContext
	OpContext = ()
	ButtonSel = False
	DrawScreen(CSM.Canvas, CSM.Screen, CSM.Arr, len(CSM.Arr))
	DrawDevBar(Canvas)
	CheckBatt(Canvas)
	DisableClick()
	device.display(Canvas)

def CreateContextMenu(Title, Size, Location, Color, Options, Canvas, Screen, Arr):
	global ButtonSel
	global CSM
	global Array
	global TOPINDEX
	CSM = ContextMenu(Title, Size, Location, Color, Options, Canvas, Screen, Arr)
	CSM.Draw()
	ButtonSel = True
	Array = Options
	TOPINDEX = len(Options)
	print("Context Menu Created")

def checkButton(BContext):
	if(BContext == Power):
		CreateContextMenu("P O W E R", (80,40), (64,0), (255,255,255), [("Shutdown", Persist), ("Close", CloseContextMenu)], Canvas, ScreenContext, ScreenSelectContext),
	elif(BContext == Wifi):
		 CreateContextMenu("W I F I", (80,40), (50, 0), (255,255,255), [("Wifi Settings", Persist), ("Close", CloseContextMenu)], Canvas, ScreenContext, ScreenSelectContext) 
	global Trackballindex
	Trackballindex = 0

def Setup():
	checkScreen(Context)
	DrawDevBar(Canvas)
	CheckBatt(Canvas)
	device.display(Canvas)
	global Trackball
	GPIO.add_event_detect(Trackball[0],GPIO.FALLING)
	GPIO.add_event_detect(Trackball[1],GPIO.FALLING)
	GPIO.add_event_detect(Trackball[2],GPIO.FALLING)
	GPIO.add_event_detect(Trackball[3],GPIO.FALLING)
	GPIO.add_event_detect(SW,GPIO.RISING)
	GPIO.add_event_callback(SW, clickCallback)
	GPIO.add_event_callback(Trackball[0], downCallback)
	GPIO.add_event_callback(Trackball[2], downCallback)


Setup()
if __name__ == '__main__':
	try:
		while(True):
			Persist()
	except KeyboardInterrupt:
		device.hide()
		GPIO.cleanup()
