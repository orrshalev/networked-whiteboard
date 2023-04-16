from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import socket
import time
import traceback, sys


def splitlines_clrf(data: bytes) -> list[bytes]:
    """
    More guranteed safety that lines will split based on \r\n ONLY than build in splitlines
    """
    lines = []
    start = 0
    while True:
        end = data.find(b"\r\n", start)
        if end == -1:
            last_line = data[start:]
            if last_line:
                lines.append(last_line)
            break
        lines.append(data[start : end + 2])
        start = end + 2
    return lines


class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.
    """

    pixel = pyqtSignal(bytes)
    text = pyqtSignal(bytes)
    exit = pyqtSignal()


class Worker(QRunnable):
    """
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function
    """

    def _handle_pixel_message(self, line: bytes):
        line = line.split(b"--")
        # print(line)
        if line[0].decode("ascii") == "PAINT":
            # print(line[1])
            self.signals.pixel.emit(line[1])
        elif line[0].decode("ascii") == "TEXT":
            self.signals.text.emit(line[1] + line[2])
        elif line[0].decode("ascii") == "EXIT":
            self.signals.exit.emit()
            exit()

    def _receive_pixel(self):
        data = b""
        while True:
            try:
                data += self.client.recv(1024)
            except Exception:
                print("Error receiving data from server")
                break
            lines = splitlines_clrf(data)
            if len(lines) == 0:
                print("Error receiving data from server")
                break
            full_lines, last_line = lines[:-1], lines[-1]
            for line in full_lines:
                # TODO: Maybe do error handeling
                self._handle_pixel_message(line[:-2])
            if last_line.endswith(b"\r\n"):
                self._handle_pixel_message(last_line[:-2])
                data = b""
            else:
                data = last_line

    def __init__(self, client: socket.socket):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.client = client
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """
        # Retrieve args/kwargs here; and fire processing using them
        result = self._receive_pixel()
