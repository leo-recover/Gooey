from PyQt5.QtWidgets import QFrame


def hline():
    frame = QFrame()
    frame.setFrameShape(QFrame.HLine)
    frame.setFrameShadow(QFrame.Sunken)
    frame.setLineWidth(2)
    return frame