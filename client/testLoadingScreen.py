import select
import sys
import os
import socket
import ssl
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

if len(sys.argv) != 2:
    raise Exception("Usage: python3 testLoadingScreen <SERVER_HOST>")


CLIENT_HOST = socket.gethostbyname(socket.gethostname())
CLIENT_PORT = 1100  # see: https://stackoverflow.com/questions/20396820/socket-programing-permission-denied
SERVER_HOST = sys.argv[1]
SERVER_PORT = 1500


class LoginWindow(QWidget):
    def __init__(self):
        # connection related
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.client = ssl.wrap_socket(
            self.client, keyfile="./tls/host.key", certfile="./tls/host.cert"
        )
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

        self.main_window = MainWindow()
        self.main_window.hide()

    def login(self):
        # NOTE: Cannot include "-" in username or password
        username = self.username_input.text()
        password = self.password_input.text()
        print("gets here")
        self.client.send(
            b"LOGIN-" + username.encode("ascii") + b"-" + password.encode("ascii")
        )

         # wait for response from server
        while True:
            # check if data is available to be received without blocking
            rlist, wlist, xlist = select.select([self.client], [], [], 0.1)
            if rlist:
                data = self.client.recv(1024)
                if data == b"OK-":
                    self.main_window.show()
                    self.close()
                elif data == b"ERROR":
                    # TODO: handle error case
                    self.error_window = ErrorWindow("Incorrect username/password")
                    self.error_window.show()
                break


    def signup(self):
        username = self.username_input.text()
        password = self.password_input.text()
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
                    self.main_window.show()
                    self.close()
                elif data == b"ERROR":
                    print("Maximum number of Users Reached, cannot log in")
                break

class ErrorWindow(QWidget):
    def __init__(self, message, login_window):
        super().__init__()

        #self.main_window = LoginWindow()
        self.login_window = login_window

        self.setWindowTitle("Error")
        self.setGeometry(100,100,400,150)
        self.error_label = QLabel(message, self)
        self.error_label.move(50, 50)
        self.ok_button = QPushButton("OK", self)
        self.ok_button.move(150,100)
        self.ok_button.clicked.connect(self.close)

        self.move(
            self.login_window.pos().x() + (self.login_window.width() - self.width()) / 2,
            self.login_window.pos().y() + (self.login_window.height() - self.height()) / 2
        )

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Main Window")
        self.setGeometry(100,100,800,600)
        self.main_window_label = QLabel("Welcome to the main window!", self)
        self.main_window_label.move(100,100)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())