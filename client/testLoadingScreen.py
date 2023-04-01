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


HOST = "127.0.0.1"
PORT = 1100 # see: https://stackoverflow.com/questions/20396820/socket-programing-permission-denied

class LoginWindow(QWidget):

    def __init__(self):
        # connection related
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.client = ssl.wrap_socket(self.client, keyfile="./tls/host.key", certfile="./tls/host.cert")
        self.client.bind((HOST, PORT))
        self.client.connect(("127.0.0.1", 1500))

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
        # NOTE: Cannot include "-" in username or password
        username = self.username_input.text()
        password = self.password_input.text()
        self.client.send(username.encode("ascii") + b"-" + password.encode("ascii"))

    def signup(self):
        print("Sign up clicked")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
