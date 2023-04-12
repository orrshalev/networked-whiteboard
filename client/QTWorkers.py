from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import socket
import time
import traceback, sys


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.
    '''
    pixel = pyqtSignal(bytes)
    exit = pyqtSignal()


class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function
    '''

    def _receive_pixel(self):
        while True:
            data = self.client.recv(1024)
            if not data:
                print(f"Dtaa not received correctly from server")
                break
            print(data)
            data = data.split(b'-')
            if data[0].decode('ascii') == 'PAINT':
                print(data[1])
                self.signals.pixel.emit(data[1])
            

    def __init__(self, client: socket.socket):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.client = client
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''
        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self._receive_pixel()
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            pass
