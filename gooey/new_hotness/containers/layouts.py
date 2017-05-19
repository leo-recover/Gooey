from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QWidget, QHBoxLayout, QListWidget
from PyQt5.QtWidgets import QVBoxLayout


# class StandardFrame(QFrame):
#     def __init__(self, header, body, footer):
#         super(StandardFrame, self).__init__()
#         layout = QVBoxLayout()
#         layout.setContentsMargins(0, 0, 0, 0)
#         layout.addWidget(header, alignment=Qt.AlignTop, stretch=0)
#         layout.setSpacing(0)
#
#         layout.addWidget(body, stretch=1)
#         layout.setSpacing(0)
#
#         layout.addWidget(footer)
#
#         self.setLayout(layout)
#         self.setFrameShape(QFrame.NoFrame)



class StandardFrame(QFrame):
    def __init__(self, header, body, footer):
        super(StandardFrame, self).__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(header, alignment=Qt.AlignTop, stretch=0)
        layout.setSpacing(0)



        layout.addWidget(body, stretch=1)
        layout.setSpacing(0)

        layout.addWidget(footer)

        self.setLayout(layout)
        self.setFrameShape(QFrame.NoFrame)


class MultiFrame(QFrame):
    def __init__(self, header, body, footer):
        super(MultiFrame, self).__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(header, alignment=Qt.AlignTop, stretch=0)
        layout.setSpacing(0)

        layout.addWidget(SplitLayout(), stretch=1)
        layout.setSpacing(0)

        layout.addWidget(footer)

        self.setLayout(layout)
        self.setFrameShape(QFrame.NoFrame)


class ActionsPanel(QWidget):

    def __init__(self, *args, **kwargs):
        super(ActionsPanel, self).__init__(*args, **kwargs)



class SplitLayout(QWidget):

    def __init__(self, *args, **kwargs):
        super(SplitLayout, self).__init__(*args, **kwargs)

        self.list = QListWidget()
        self.list.addItem('Poop')
        self.list.addItem('Schoop')
        self.list.addItem('McDoop')

        layout = QHBoxLayout()
        layout.addWidget(self.list)

        self.setLayout(layout)

