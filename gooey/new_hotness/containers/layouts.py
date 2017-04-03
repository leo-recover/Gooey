from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QVBoxLayout


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