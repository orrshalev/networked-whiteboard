import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout
import MySQLdb
from dotenv import load_dotenv
load_dotenv()

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Login Window')

        self.username_label = QLabel('Username:', self)
        self.username_input = QLineEdit(self)

        self.password_label = QLabel('Password:', self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton('Login', self)
        self.login_button.clicked.connect(self.login)

        self.signup_button = QPushButton('Sign Up', self)
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
        # debug purposes
        username = self.username_input.text()
        password = self.password_input.text()
        print(f'Username: {username}, Password: {password}')
        

    def signup(self):
        print('Sign up clicked')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
