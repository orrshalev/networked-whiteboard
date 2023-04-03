# importing libraries
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys

# window class
class Window(QMainWindow):
	global textboxList 
	textboxList = []
	def __init__(self):
		super().__init__()

		# setting title
		self.setWindowTitle("Whiteboard Demo")

		# setting geometry to main window
		self.setGeometry(100, 100, 800, 600)

		# creating image object
		self.image = QImage(self.size(), QImage.Format_RGB32)

		# making image color to white
		self.image.fill(Qt.white)

		# default drawing flag
		self.drawing = False
		# default text flag
		self.text = False
		# default brush size
		self.brushSize = 4
		# default color
		self.brushColor = Qt.black

		# QPoint object to tract the point
		self.lastPoint = QPoint()

		# creating menu bar
		mainMenu = self.menuBar()

		# creating file menu for save and clear action
		fileMenu = mainMenu.addMenu("File")
        
		# adding brush color to main menu
		b_color = mainMenu.addMenu("Brush")
		
        # adding eraser to main menu
		eraser = mainMenu.addMenu("Eraser")

		# adding textbox to main menu
		textbox = mainMenu.addMenu("Textbox")

		# creating save action
		saveAction = QAction("Save", self)
		# adding save to the file menu
		fileMenu.addAction(saveAction)
		# adding action to the save
		saveAction.triggered.connect(self.save)

		# creating clear action
		clearAction = QAction("Clear", self)
		# adding clear to the file menu
		fileMenu.addAction(clearAction)
		# adding action to the clear
		clearAction.triggered.connect(self.clear)
		
		# creating options for brush color
		# creating action for black color
		black = QAction("Black", self)
		# adding this action to the brush colors
		b_color.addAction(black)
		# adding methods to the black
		black.triggered.connect(self.blackColor)

		# POTENTIAL CODE FOR ERASER
		# similarly repeating above steps for different color
		white = QAction("Eraser", self)
		eraser.addAction(white)
		white.triggered.connect(self.whiteColor)

		yellow = QAction("Highlighter", self)
		b_color.addAction(yellow)
		yellow.triggered.connect(self.yellowColor)

		# POTENTIAL CODE FOR TEXTBOX
		textboxAction = QAction("Textbox", self)
		# add action to the textbox
		textbox.addAction(textboxAction)
		# add method to the textbox
		textboxAction.triggered.connect(self.textboxPlace)


	# method for checking mouse clicks
	def mousePressEvent(self, event):

		if event.button() == Qt.LeftButton and self.text == True:
			# if the selected action is textbox
			self.textbox = QLineEdit(self)
			self.textbox.move(event.pos())
			self.textbox.show()
				# add self.textbox to a list
			textboxList.append(self.textbox)
		# if left mouse button is pressed
		elif event.button() == Qt.LeftButton:

			# make drawing flag true
			self.drawing = True
			# make last point to the point of cursor
			self.lastPoint = event.pos()

	# method for tracking mouse activity
	def mouseMoveEvent(self, event):
		
		# checking if left button is pressed and drawing flag is true
		if (event.buttons() & Qt.LeftButton) & self.drawing:
			
			# creating painter object
			painter = QPainter(self.image)
			
			# set the pen of the painter
			painter.setPen(QPen(self.brushColor, self.brushSize,
							Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
			
			# create an if statement for checking if the selected color is yellow
			if self.brushColor == Qt.yellow:
				# if the color is yellow, set the opacity to 0.1
				painter.setOpacity(0.1)
			
			# draw line from the last point of cursor to the current point
			# this will draw only one step
			painter.drawLine(self.lastPoint, event.pos())
			
			# change the last point
			self.lastPoint = event.pos()
			# update
			self.update()


	# method for mouse left button release
	def mouseReleaseEvent(self, event):

		if event.button() == Qt.LeftButton:
			# make drawing flag false
			self.drawing = False

	# paint event
	def paintEvent(self, event):
		# create a canvas
		canvasPainter = QPainter(self)
		
		# draw rectangle on the canvas
		canvasPainter.drawImage(self.rect(), self.image, self.image.rect())

	# method for saving canvas
	def save(self):
		filePath, _ = QFileDialog.getSaveFileName(self, "Save Image", "",
						"PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*) ")

		if filePath == "":
			return
		self.image.save(filePath)

	# method for clearing every thing on canvas
	def clear(self):
		# make the whole canvas white
		self.image.fill(Qt.white)
		# for every textbox in the list
		for self.textbox in textboxList:
			# remove the textbox
			self.textbox.setParent(None)
		# update
		self.update()

	# methods for changing brush color
	def blackColor(self):
		self.text = False
		self.brushColor = Qt.black
		self.brushSize = 4

	def whiteColor(self):
		self.text = False
		self.brushColor = Qt.white
		self.brushSize = 20

	def yellowColor(self):
		self.text = False
		self.brushSize = 12
		self.brushColor = Qt.yellow
    
	# method for textbox
	def textboxPlace(self):
		
		self.drawing = False
		self.text = True

# create pyqt5 app
App = QApplication(sys.argv)

# create the instance of our Window
window = Window()

# showing the window
window.show()

# start the app
sys.exit(App.exec())
