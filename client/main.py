import select
import sys
import os
import socket
import ssl
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from ssl import SSLSocket
from QTWorkers import Worker

if len(sys.argv) != 2:
    raise Exception("Usage: python3 testLoadingScreen <SERVER_HOST>")

if len(sys.argv) != 2:
    raise Exception("Usage: python3 testLoadingScreen <SERVER_HOST>")


CLIENT_HOST = socket.gethostbyname(socket.gethostname())
CLIENT_PORT = 1100  # see: https://stackoverflow.com/questions/20396820/socket-programing-permission-denied
SERVER_HOST = sys.argv[1]
SERVER_PORT = 1500

CLIENT_HOST = socket.gethostbyname(socket.gethostname())
CLIENT_PORT = 1100  # see: https://stackoverflow.com/questions/20396820/socket-programing-permission-denied
SERVER_HOST = sys.argv[1]
SERVER_PORT = 1500

class LoginWindow(QWidget):

    #client: SSLSocket

    def __init__(self):
        # connection related
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self.client = ssl.wrap_socket(
        #     self.client, keyfile="./tls/host.key", certfile="./tls/host.cert"
        # )
        self.client.bind((CLIENT_HOST, CLIENT_PORT))
        self.client.connect((SERVER_HOST, SERVER_PORT))

        # UI related
        super().__init__()
        self.setWindowTitle("Login Window")

        self.username_label = QLabel("Username:", self)
        self.username_input = QLineEdit(self)

        self.password_label = QLabel("Password:", self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Login", self)
        self.login_button.clicked.connect(self.login)

        self.signup_button = QPushButton("Sign Up", self)
        self.signup_button.clicked.connect(self.signup)

        vbox = QVBoxLayout()
        vbox.addWidget(self.username_label)
        vbox.addWidget(self.username_input)
        vbox.addWidget(self.password_label)
        vbox.addWidget(self.password_input)
        vbox.addWidget(self.login_button)
        vbox.addWidget(self.signup_button)

        self.setLayout(vbox)

        self.setGeometry(300, 300, 400, 200)
    def login(self):
        self.l_window = landingWindow(self.client)
        self.l_window.hide()
        # self.wb_window.submitClicked.connect(self.on_sub_window_confirm)
	
        # NOTE: Cannot include "-" in username or password
        username = self.username_input.text()
        password = self.password_input.text()
        self.client.send(
            b"LOGIN-" + username.encode("ascii") + b"-" + password.encode("ascii")
        )

        # check if data is available to be received without blocking
        data = self.client.recv(1024)
        if data == b"OK-": 
            self.l_window.run_threads()
            self.l_window.show()
            # self.wb_window = WhiteboardWindow(self.client)
            # self.wb_window.show()
            self.hide()
    
        elif data == b"ERROR":
            # TODO: handle error case
            self.error_window = ErrorWindow("Incorrect username/password")
            self.error_window.show()


    def signup(self):
	    
        username = self.username_input.text()
        password = self.password_input.text()
        self.l_window = landingWindow(self.client)
        self.l_window.hide()
	
        print("gets here in signup")
        self.client.send(
            b"SIGNUP-" + username.encode("ascii") + b"-" + password.encode("ascii")
        )

        #wait for response from server
        while True:
            # check if data is available to be received without blocking
            rlist, wlist, xlist = select.select([self.client], [], [], 0.1)
            if rlist:
                print("got here")
                data = self.client.recv(1024)
                print("after recv")
                if data == b"OK-":
                    self.l_window.show()
                    # self.close()
                    self.hide()
                elif data == b"ERROR":
                    print("Maximum number of Users Reached, cannot log in")
                break

class ErrorWindow(QWidget):
    def __init__(self, message):
        super().__init__()

        #self.main_window = LoginWindow()
        # self.login_window = login_window

        self.setWindowTitle("Error")
        self.setGeometry(100,100,400,150)
        self.error_label = QLabel(message, self)
        self.error_label.move(50, 50)
        self.ok_button = QPushButton("OK", self)
        self.ok_button.move(150,100)
        self.ok_button.clicked.connect(self.close)

        # self.move(
        #     self.login_window.pos().x() + (self.login_window.width() - self.width()) / 2,
        #     self.login_window.pos().y() + (self.login_window.height() - self.height()) / 2
        # )


class landingWindow(QWidget):
	"""
        Create a landing window that the clients go to after loggin in.
		The window contains a list of active whiteboards.
		The window also shows the user's name at the top.
        The user can click on a whiteboard to join it.
        Has a button at the bottom that allows the user to create a new whiteboard.
	"""
	def __init__(self, client):
		super().__init__()
		self.client = client
		self.setWindowTitle("Whiteboard Demo")
		self.setGeometry(100, 100, 800, 600)
		self.layout = QVBoxLayout()
		self.layout.setContentsMargins(0,0,0,0)
		self.layout.setSpacing(0)
		self.setLayout(self.layout)
		self.layout.addWidget(QLabel("Welcome to the Whiteboard Demo!"))
		self.layout.addWidget(QLabel("Please select a whiteboard to join:"))
		self.whiteboard_list = QListWidget()
		self.layout.addWidget(self.whiteboard_list)
		self.whiteboard_list.itemDoubleClicked.connect(self.join_whiteboard)
		self.create_whiteboard_button = QPushButton("Create New Whiteboard")
		self.create_whiteboard_button.clicked.connect(self.create_whiteboard)
		self.layout.addWidget(self.create_whiteboard_button)
		self.worker = Worker(self.client)
		self.worker.signals.whiteboard.connect(self.add_whiteboard)
		self.threadpool = QThreadPool()
		self.threadpool.start(self.worker)

	def add_whiteboard(self, whiteboard_name):
		self.whiteboard_list.addItem(whiteboard_name)

	def join_whiteboard(self, whiteboard):
		self.wb_window = WhiteboardWindow(self.client, whiteboard.text())
		self.wb_window.hide()
		self.wb_window.submitClicked.connect(self.on_sub_window_confirm)
		self.wb_window.show()
		self.close()

	def create_whiteboard(self):
		self.wb_window = WhiteboardWindow(self.client)
		self.wb_window.hide()
		self.wb_window.submitClicked.connect(self.on_sub_window_confirm)
		self.wb_window.show()
		self.close()

	def on_sub_window_confirm(self):
		self.show()
	
		
        
# window class
class WhiteboardWindow(QMainWindow):
	global textboxList 
	textboxList = []
	# submitClicked = qtc.pyqtSignal()
	def __init__(self, client):
		super().__init__()
		self.client = client

		# setting title
		self.setWindowTitle("Whiteboard Demo")

		# setting geometry to main window
		self.setGeometry(100, 100, 800, 600)

		# creating image object
		self.image = QImage(self.size(), QImage.Format_RGB32)

		self.worker = Worker(self.client)
		self.worker.signals.pixel.connect(self.server_paint)
		self.threadpool = QThreadPool()

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

	def run_threads(self):
		self.threadpool.start(self.worker)

	def server_paint(self, message: bytes): 
		x = int.from_bytes(message[:2], byteorder="big") 
		y = int.from_bytes(message[2:4], byteorder="big") 
		T = message[4]
		painter = QPainter(self.image)
		if T == 1:
			painter.setPen(QPen(Qt.black, 4,
							Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
		elif T == 2:
			painter.setPen(QPen(Qt.yellow, 12,
							Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
			painter.setOpacity(0.1)
		elif T == 3:
			painter.setPen(QPen(Qt.white, 20,
							Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
		elif T == 4:
			self.image.fill(Qt.white)
			for self.textbox in textboxList:
				self.textbox.setParent(None)
			self.update()
			return
		painter.drawPoint(x, y)
		self.update()

	def handle_data_received(self, data):
			if data == b"OK-":
				print("The pixels work")
			elif data == b"ERROR":
				self.error_window = ErrorWindow("Error with pixel sending")
				self.error_window.show()
				
	# method for checking mouse clicks
	def mousePressEvent(self, event):
		#x,y

		if event.button() == Qt.LeftButton and self.text == True:
			x = event.x()
			y = event.y()
			# turns the x and y values into 2 bytes to send to server
			xbytes = x.to_bytes(2, byteorder='big')
			ybytes = y.to_bytes(2, byteorder='big')
			if self.brushColor == Qt.black:
				T = 1
				T_bytes = T.to_bytes(1, byteorder='big')
			elif self.brushColor == Qt.yellow:
				T = 2
				T_bytes = T.to_bytes(1, byteorder='big')
			elif self.brushColor == Qt.white:
				T = 3
				T_bytes = T.to_bytes(1, byteorder='big')
	
			message = xbytes + ybytes + T_bytes
			roomname = "test"
			self.client.send(
				b"PAINT-" + message + b"-" + roomname.encode("ascii")
		    )
			print("sent to server")
            # # wait for response from server
		
			# self.client.send()
			# if the selected action is textbox 
			self.textbox = QLineEdit(self)
			self.textbox.move(event.pos())
			self.textbox.show()
				# add self.textbox to a list
			textboxList.append(self.textbox)
			print(f"Mouse clicked at ({x}, {y})")

		# if left mouse button is pressed
		elif event.button() == Qt.LeftButton:
			print("gets here click")
			x = event.x()
			y = event.y()
			# make drawing flag true
			self.drawing = True
			# make last point to the point of cursor
			self.lastPoint = event.pos()
			xbytes = x.to_bytes(2, byteorder='big')
			ybytes = y.to_bytes(2, byteorder='big')
			if self.brushColor == Qt.black:
				T = 1
				T_bytes = T.to_bytes(1, byteorder='big')
			elif self.brushColor == Qt.yellow:
				T = 2
				T_bytes = T.to_bytes(1, byteorder='big')
			elif self.brushColor == Qt.white:
				T = 3
				T_bytes = T.to_bytes(1, byteorder='big')
	
			message = xbytes + ybytes + T_bytes
			roomname = "test"
			self.client.send(
				b"PAINT-" + message + b"-" + roomname.encode("ascii")
		    )
			# self.worker = Worker(self.client)
			# # self.worker.client = self.client
			# self.worker.data_received.connect(self.handle_data_received)
			# self.worker.start()
            # wait for response from server

	# method for tracking mouse activity
	def mouseMoveEvent(self, event):
		#checking if left button is pressed and drawing flag is true
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
			x = event.x()
			y = event.y()
			print(f"Mouse moved at ({x}, {y})")
			xbytes = x.to_bytes(2, byteorder='big')
			ybytes = y.to_bytes(2, byteorder='big')
			if self.brushColor == Qt.black:
				T = 1
				T_bytes = T.to_bytes(1, byteorder='big')
			elif self.brushColor == Qt.yellow:
				T = 2
				T_bytes = T.to_bytes(1, byteorder='big')
			elif self.brushColor == Qt.white:
				T = 3
				T_bytes = T.to_bytes(1, byteorder='big')
	
			message = xbytes + ybytes + T_bytes
			roomname = "test"
			self.client.send(
				b"PAINT-" + message + b"-" + roomname.encode("ascii")
		    )
	
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
if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
