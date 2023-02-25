import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsItem
from PyQt5.QtGui import QPen, QColor
from PyQt5.QtCore import Qt, QRectF, QPointF

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle("Whiteboard")

        self.graphicsView = GraphicsView(self)
        self.setCentralWidget(self.graphicsView)

        self.whiteboard = Whiteboard()
        self.graphicsView.scene().addItem(self.whiteboard)


class GraphicsView(QGraphicsView):
    def __init__(self, parent):
        super().__init__(parent)
        self.setScene(QGraphicsScene(self))
        self.setSceneRect(0, 0, 800, 600)


class Whiteboard(QGraphicsItem):
    def __init__(self):
        super().__init__()
        self.pen = QPen(QColor("black"), 2, Qt.SolidLine)
        self.lastPoint = None

    def boundingRect(self):
        return QRectF()

    def paint(self, painter, option, widget=None):
        pass

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.lastPoint = event.scenePos()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self.lastPoint is not None:
            newPoint = event.scenePos()
            line = QGraphicsItem(self)
            line.setPen(self.pen)
            line.setLine(self.lastPoint.x(), self.lastPoint.y(), newPoint.x(), newPoint.y())
            self.lastPoint = newPoint

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.lastPoint = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
