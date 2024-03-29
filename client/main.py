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

""" check if the correct number of arguments are passed in. """
if len(sys.argv) != 2:
    raise Exception("Usage: python3 main <SERVER_HOST>")

CLIENT_HOST = socket.gethostbyname(socket.gethostname())
CLIENT_PORT = 1000
SERVER_HOST = sys.argv[1]
SERVER_PORT = 1500


class LoginWindow(QWidget):
    """ Create a login window for the client to log in. """
    # client: SSLSocket

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
            b"LOGIN--"
            + username.encode("ascii")
            + b"--"
            + password.encode("ascii")
            + b"\r\n"
        )

        # check if data is available to be received without blocking
        data = self.client.recv(1024)
        if data[:-2] == b"OK":
            self.l_window.show()
            # self.wb_window = WhiteboardWindow(self.client)
            # self.wb_window.show()
            self.hide()

        elif data[:-2] == b"ERROR":
            # TODO: handle error case
            self.error_window = ErrorWindow("Incorrect username/password")
            self.error_window.show()

    def signup(self):
        username = self.username_input.text()
        password = self.password_input.text()
        self.l_window = landingWindow(self.client)
        self.l_window.hide()

        self.client.send(
            b"SIGNUP--"
            + username.encode("ascii")
            + b"--"
            + password.encode("ascii")
            + b"\r\n"
        )

        # wait for response from server
        data = self.client.recv(1024)
        if data[:-2] == b"OK":
            self.l_window.show()
            self.hide()
        elif data[:-2] == b"ERROR":
            self.error_window = ErrorWindow(
                "Maximum number of Users Reached, cannot log in"
            )
            self.error_window.show()


class ErrorWindow(QWidget):
    """ Create a window that pops up when there is an error. """
    def __init__(self, message):
        super().__init__()

        self.setWindowTitle("Error")
        self.setGeometry(100, 100, 400, 150)
        self.error_label = QLabel(message, self)
        self.error_label.move(50, 50)
        self.ok_button = QPushButton("OK", self)
        self.ok_button.move(150, 100)
        self.ok_button.clicked.connect(self.close)

        # self.move(
        #     self.login_window.pos().x() + (self.login_window.width() - self.width()) / 2,
        #     self.login_window.pos().y() + (self.login_window.height() - self.height()) / 2
        # )


class landingWindow(QWidget):
    """
    Create a landing window that the clients go to after loggin in.
            The window contains a list of active users.
            The window contains a list of active whiteboards.
            The window contains a refresh button.
            The window contains a section for the user to recovery their whiteboard.
            The window also shows the user's name at the top.
    The user can click on a whiteboard to join it.
    Has a button at the bottom that allows the user to create a new whiteboard if they do have a whiteboard saved.
    """

    def __init__(self, client):
        super().__init__()
        self.client = client
        self.setWindowTitle("Whiteboard Demo")
        self.setGeometry(100, 100, 800, 600)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
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
        self.layout.addWidget(QLabel("Active Users:"))
        self.user_list = QListWidget()
        self.layout.addWidget(self.user_list)
        # self.user_list.itemDoubleClicked.connect(self.join_user)
        self.layout.addWidget(QLabel("Registered Users:"))
        self.inactive_list = QListWidget()
        self.layout.addWidget(self.inactive_list)

        self.layout.addWidget(
            QLabel("Please enter the name of a whiteboard to recover:")
        )
        self.recovery_input = QLineEdit()
        self.recovery_input.setPlaceholderText("Whiteboard Name...")
        self.layout.addWidget(self.recovery_input)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password... (if applicable)")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.password_input)
        self.recovery_button = QPushButton("Recover")
        self.recovery_button.clicked.connect(self.recover)
        self.layout.addWidget(self.recovery_button)
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh)
        self.layout.addWidget(self.refresh_button)
        self.refresh()

    def refresh(self):
        self.user_list.clear()
        self.whiteboard_list.clear()
        self.inactive_list.clear()

        self.client.send(b"GETUSERS\r\n")
        users = self.client.recv(1024)
        users = users.split(b"--")
        for user in users:
            self.user_list.addItem(user.decode("ascii"))

        self.client.send(b"GETINACTIVEUSERS\r\n")
        inactiveusers = self.client.recv(1024)
        inactiveusers = inactiveusers.split(b"--")
        for user in inactiveusers:
            self.inactive_list.addItem(user.decode("ascii"))

        self.client.send(b"GETROOMS\r\n")
        rooms = self.client.recv(1024)
        rooms = rooms.split(b"--")
        for room in rooms:
            self.whiteboard_list.addItem(room.decode("ascii"))

    def add_whiteboard(self, whiteboard_name):
        self.whiteboard_list.addItem(whiteboard_name)

    def add_user(self, user_name):
        self.user_list.addItem(user_name)

    def join_whiteboard(self, whiteboard: QListWidgetItem):
        password, ok = QInputDialog.getText(
            self, "Whiteboard Password", "Enter Password:", QLineEdit.Password
        )
        if ok:
            message = (
                b"JOINROOM--"
                + whiteboard.text().encode("ascii")[:-2]
                + b"--"
                + password.encode("ascii")
                + b"\r\n"
            )
            self.client.send(message)
            data = self.client.recv(1024)
            if data[:-2] == b"OK":
                self.wb_window = WhiteboardWindow(self.client, self)
                self.wb_window.hide()
                self.wb_window.show()
                self.hide()
            elif data[:-2] == b"ERROR":
                
                self.error_window = ErrorWindow("Incorrect username/password")
                self.error_window.show()
        
    # TODO : get user input for name
    def create_whiteboard(self):
        room_name, ok = QInputDialog.getText(
            self, "Create Whiteboard", "Enter Whiteboard Name:"
        )
        if ok:
            password, ok = QInputDialog.getText(
                self, "Create Whiteboard", "Enter Password (optional):"
            )
            if ok:
                command = b"CREATEROOM--" + room_name.encode("ascii")
                if password:
                    command += b"--" + password.encode("ascii")
                command += b"\r\n"
                self.client.send(command)

                data = self.client.recv(1024)
                if data[:-2] == b"OK":
                    self.wb_window = WhiteboardWindow(self.client, self)
                    self.wb_window.hide()
                    self.wb_window.show()
                    self.hide()
                elif data[:-2] == b"ERROR":
                    self.error_window = ErrorWindow("Incorrect username/password")
                    self.error_window.show()
        else:
            return

    def on_sub_window_confirm(self):
        self.show()

    def recover(self):
        """ Recover a whiteboard """
        roomname = self.recovery_input.text()
        password = self.password_input.text()
        self.client.send(
            b"RECOVER"
            + b"--"
            + roomname.encode("ascii")
            + b"--"
            + password.encode("ascii")
            + b"\r\n"
        )
        data = self.client.recv(1024)
        if data[:-2] == b"OK":
            self.wb_window = WhiteboardWindow(self.client, roomname)
            self.wb_window.hide()
            self.wb_window.show()
            self.hide()
        elif data[:-2] == b"ERROR":
            self.error_window = ErrorWindow("Incorrect roomname/password")
            self.error_window.show()



class WhiteboardWindow(QMainWindow):
    """ Whiteboard Window Class
         this class is the main whiteboard window where the user can draw and type text
    """
    global textboxList
    textboxList = []

    def __init__(self, client, landing_window):
        super().__init__()
        self.client = client
        self.l_window = landing_window

        # setting title
        self.setWindowTitle("Whiteboard Demo")

        # setting geometry to main window
        self.setGeometry(100, 100, 800, 600)

        # creating image object
        self.image = QImage(self.size(), QImage.Format_RGB32)

        self.worker = Worker(self.client)
        self.worker.signals.pixel.connect(self.server_paint)
        self.worker.signals.text.connect(self.server_text)
        self.worker.signals.exit.connect(self.exit)
        self.worker.signals.pixel_rgb.connect(self.server_paint_rgb)
        self.threadpool = QThreadPool()
        self.threadpool.start(self.worker)

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
        saveAction = QAction("Save and Exit", self)
        # adding save to the file menu
        fileMenu.addAction(saveAction)
        # adding action to the save
        saveAction.triggered.connect(self.save)

        exitAction = QAction("Exit", self)

        fileMenu.addAction(exitAction)

        exitAction.triggered.connect(self.exit)

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

    def exit(self):
        """ Exit the whiteboard """
        self.hide()
        self.l_window.show()
        # TODO : Add going back to main menu
        image = self.image
        width = image.width()
        height = image.height()
        for x in range(width):
            for y in range(height):
                rgb = image.pixel(x, y)
                red = (rgb >> 16) & 0xFF
                green = (rgb >> 8) & 0xFF
                blue = rgb & 0xFF
                alpha = (rgb >> 24) & 0xFF
                message = (
                    x.to_bytes(2, byteorder="big")
                    + y.to_bytes(2, byteorder="big")
                    + red.to_bytes(1, byteorder="big")
                    + green.to_bytes(1, byteorder="big")
                    + blue.to_bytes(1, byteorder="big")
                    + alpha.to_bytes(1, byteorder="big")
                )
                if (red == 255 and green == 255 and blue == 255):
                    continue
                else:
                    self.client.send(b"SAVE" + b"--" + message + b"\r\n")
        self.client.send(b"EXIT\r\n")
        sys.exit()

    def save(self):
        """ Save and exit the whiteboard """
        self.hide()
        self.l_window.show()
        image = self.image
        width = image.width()
        height = image.height()
        for x in range(width):
            for y in range(height):
                rgb = image.pixel(x, y)
                red = (rgb >> 16) & 0xFF
                green = (rgb >> 8) & 0xFF
                blue = rgb & 0xFF
                alpha = (rgb >> 24) & 0xFF
                message = x.to_bytes(2, byteorder="big") + y.to_bytes(2, byteorder="big") + red.to_bytes(1, byteorder="big") + green.to_bytes(1, byteorder="big") + blue.to_bytes(1, byteorder="big") + alpha.to_bytes(1, byteorder="big")
                if (red == 255 and green == 255 and blue == 255):
                    continue
                else:
                    self.client.send(b"SAVE" + b"--" + message + b"\r\n")
        self.client.send(b"EXIT\r\n")
        sys.exit()

    def server_paint(self, message: bytes):
        """ Paint on the whiteboard """
        x = int.from_bytes(message[:2], byteorder="big")
        y = int.from_bytes(message[2:4], byteorder="big")
        T = message[4]
        painter = QPainter(self.image)
        if T == 1:
            painter.setPen(QPen(Qt.black, 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        elif T == 2:
            painter.setPen(QPen(Qt.yellow, 12, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.setOpacity(0.1)
        elif T == 3:
            painter.setPen(QPen(Qt.white, 20, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        elif T == 4:
            self.image.fill(Qt.white)
            for self.textbox in textboxList:
                self.textbox.setParent(None)
            self.update()
            return
        # text
        painter.drawPoint(x, y)
        self.update()

    def server_paint_rgb(self, message: bytes):
        """ Paint on the whiteboard """
        x = int.from_bytes(message[:2], byteorder="big")
        y = int.from_bytes(message[2:4], byteorder="big")
        red = int.from_bytes(message[4:5], byteorder="big")
        green = int.from_bytes(message[5:6], byteorder="big")
        blue = int.from_bytes(message[6:7], byteorder="big")
        alpha = int.from_bytes(message[7:8], byteorder="big")
        painter = QPainter(self.image)
        painter.setPen(QPen(QColor(red, green, blue, alpha), 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawPoint(x, y)
        self.update()

    def server_text(self, message: bytes):
        """ Place text on the whiteboard """
        x = int.from_bytes(message[:2], byteorder="big")
        y = int.from_bytes(message[2:4], byteorder="big")
        text = message[4:].decode("utf-8")
        painter = QPainter(self.image)
        painter.setPen(QPen(Qt.black, 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setFont(QFont("Arial", 16))
        # Draw the text at the mouse click position
        painter.drawText(x, y, text)
        painter.end()
        # Update the widget to display the modified image
        self.update()

    def handle_data_received(self, data):
        """ Handle data received from the server """
        if data[:-2] == b"OK":
            print("The pixels work")
        elif data[:-2] == b"ERROR":
            self.error_window = ErrorWindow("Error with pixel sending")
            self.error_window.show()

    # method for checking mouse clicks
    def mousePressEvent(self, event):
        """ Handle mouse press events """
        # x,y

        if event.button() == Qt.LeftButton and self.text == True:
            x = event.x()
            y = event.y()
            # turns the x and y values into 2 bytes to send to server
            xbytes = x.to_bytes(2, byteorder="big")
            ybytes = y.to_bytes(2, byteorder="big")

            message = xbytes + ybytes
            # # wait for response from server

            text, ok = QInputDialog.getText(
                self, "Text Input Dialog", "Enter your text:"
            )
            if ok:
                # Create a painter to draw on the image
                painter = QPainter(self.image)
                painter.setPen(
                    QPen(Qt.black, 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
                )
                painter.setFont(QFont("Arial", 16))
                # Draw the text at the mouse click position
                painter.drawText(event.pos(), text)
                painter.end()
                # Update the widget to display the modified image
                self.update()

            self.client.send(
                b"TEXT--" + message + b"--" + text.encode("utf-8") + b"\r\n"
            )

        # if left mouse button is pressed
        elif event.button() == Qt.LeftButton:
            # make drawing flag true
            self.drawing = True
            # make last point to the point of cursor

    # method for tracking mouse activity
    def mouseMoveEvent(self, event):
        """ Handle mouse move events """
        # checking if left button is pressed and drawing flag is true
        if (event.buttons() & Qt.LeftButton) & self.drawing:
            # creating painter object
            painter = QPainter(self.image)

            # set the pen of the painter
            painter.setPen(
                QPen(
                    self.brushColor,
                    self.brushSize,
                    Qt.SolidLine,
                    Qt.RoundCap,
                    Qt.RoundJoin,
                )
            )

            # create an if statement for checking if the selected color is yellow
            if self.brushColor == Qt.yellow:
                # if the color is yellow, set the opacity to 0.1
                painter.setOpacity(0.1)
            x = event.x()
            y = event.y()
            xbytes = x.to_bytes(2, byteorder="big")
            ybytes = y.to_bytes(2, byteorder="big")
            if self.brushColor == Qt.black:
                T = 1
                T_bytes = T.to_bytes(1, byteorder="big")
            elif self.brushColor == Qt.yellow:
                T = 2
                T_bytes = T.to_bytes(1, byteorder="big")
            elif self.brushColor == Qt.white:
                T = 3
                T_bytes = T.to_bytes(1, byteorder="big")

            message = xbytes + ybytes + T_bytes
    
            self.client.send(b"PAINT--" + message + b"\r\n")

            # draw line from the last point of cursor to the current point
            # this will draw only one step
            painter.drawPoint(x, y)

            # change the last point
            # update
            self.update()

    # method for mouse left button release
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            # make drawing flag false
            self.drawing = False

    # paint event
    def paintEvent(self, event):
        """ Paint the image to the canvas """
        # create a canvas
        canvasPainter = QPainter(self)

        # draw rectangle on the canvas
        canvasPainter.drawImage(self.rect(), self.image, self.image.rect())

    # method for clearing every thing on canvas
    def clear(self):
        """ Clear the whole canvas """
        # make the whole canvas white
        T = 4
        T_bytes = T.to_bytes(1, byteorder="big")
        self.image.fill(Qt.white)
        self.client.send(b"PAINT--xxxx" + T_bytes + b"\r\n")
        # update
        self.update()

    """ Methods for changing brush color"""
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
