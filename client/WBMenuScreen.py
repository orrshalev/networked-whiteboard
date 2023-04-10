import sys
import socket
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Set up the window
        self.setWindowTitle('User Menu')
        self.setGeometry(100, 100, 800, 600)

        # Set up the layout
        layout = QVBoxLayout()

        # Add a label to display the list of active users
        self.label = QLabel()
        layout.addWidget(self.label)

        # Set the layout for the window
        self.setLayout(layout)

        # Get the list of active users from the server
        #users = self.get_active_users()

        # Update the label with the list of active users
        #self.label.setText('Active Users:\n' + '\n'.join(users))
        self.label.setText('Active Users:')

    # def get_active_users(self):
    #     # Connect to the server and get the list of active users
    #     try:
    #         s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #         #s.connect(('server_address', 1234))
    #         s.connect(('172.18.0.2', 1500))
    #         s.sendall(b'get_active_users')
    #         data = s.recv(1024)
    #         s.close()
    #         users = data.decode('utf-8').split('\n')
    #         users = [u.strip() for u in users if u.strip()]
    #         return users
    #     except Exception as e:
    #         print('Error:', e)
    #         return []


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
