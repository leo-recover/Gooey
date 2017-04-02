

# import rx
# from rx import Observable, Observer
# from rx.testing import marbles
#
# class MyObserver(Observer):
#     def on_next(self, x):
#         print("Got: %s" % x)
#
#     def on_error(self, e):
#         print("Got error: %s" % e)
#
#     def on_completed(self):
#         print("Sequence completed")
#
# from rx.subjects import Subject
#
# stream = Subject()
# stream.on_next(41)
#
# d = stream.subscribe(lambda x: print("Got: %s" % x))
#
# stream.on_next(42)
#
# d.dispose()
# stream.on_next(43)



from rx.subjects import Subject
from rx.concurrency import QtScheduler
import sys

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QLabel


class Window(QWidget):

    def __init__(self):
        super(QWidget, self).__init__()
        self.setWindowTitle("Rx for Python rocks")
        self.resize(600, 600)
        self.setMouseTracking(True)

        # This Subject is used to transmit mouse moves to labels
        self.mousemove = Subject()

    def mouseMoveEvent(self, event):
        self.mousemove.on_next((event.x(), event.y()))


def main():
    app = QApplication(sys.argv)
    scheduler = QtScheduler(QtCore)

    window = Window()
    window.show()

    text = 'TIME FLIES LIKE AN ARROW'
    labels = [QLabel(char, window) for char in text]

    def handle_label(i, label):

        def on_next(pos):
            x, y = pos
            label.move(x + i*12 + 15, y)
            label.show()

        window.mousemove.delay(i*100, scheduler=scheduler).subscribe(on_next)

    for i, label in enumerate(labels):
        handle_label(i, label)

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()