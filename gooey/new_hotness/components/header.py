import os
from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout


class Header(QFrame):

    def __init__(self, store, *args, **kwargs):
        super(Header, self).__init__(*args, **kwargs)
        self._store = store
        self._store.subscribe(self.renderNextState)

        self.title = QLabel('<b>Settings</b>')
        self.subtitle = QLabel()
        self.icon = QPixmap()
        self.icon.load(os.path.join(os.getcwd(), '../images/config_icon.png'))
        self.icon = self.icon.scaled(131, 79, QtCore.Qt.KeepAspectRatio)

        self.layoutComponent()

    def layoutComponent(self):
        layout = QHBoxLayout()
        layout.addLayout(
            self.format_header(self.title, self.subtitle), stretch=1
        )

        label = QLabel()
        label.setPixmap(self.icon)
        layout.addWidget(label)

        self.setLayout(layout)
        self.setObjectName('headerSection')
        self.setMaximumHeight(80)
        self.setMinimumWidth(130)
        self.setFrameShape(QFrame.NoFrame)
        self.setLineWidth(0)
        # TODO fix styles
        self.setStyleSheet('''
            QFrame#headerSection {
                background: white; margin: 0;
                padding: 0;
                border-top: 1px solid #cacaca;
            }
        ''')

    def format_header(self, title, subtitle):
        layout = QVBoxLayout()
        layout.addStretch(1)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch(1)
        return layout

    def renderNextState(self):
        nextState = self._store.get_state().get('main')
        print(nextState)
        self.title.setText('<b>{}</b>'.format(nextState['title']))
        self.subtitle.setText(nextState['subtitle'])