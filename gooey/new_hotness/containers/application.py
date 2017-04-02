import json
import sys
from itertools import groupby

from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, \
    QStackedWidget, QTextEdit, QProgressBar, QButtonGroup
from PyQt5.QtWidgets import QFrame, QDialog
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QScrollArea
from PyQt5.QtWidgets import QWidget, QMainWindow

from copy import deepcopy
from functools import reduce, partial
from gooey.new_hotness.components.config_panel import ConfigPanel
from gooey.new_hotness.components.console_panel import ConsolePanel
from gooey.new_hotness.components.footer import Footer
from gooey.new_hotness.components.general import hline
from gooey.new_hotness.functional import assign
from gooey.new_hotness.components.header import Header
from operator import itemgetter
from pydux import create_store, combine_reducers
from pydux.thunk_middleware import thunk_middleware
from pydux.apply_middleware import apply_middleware
from pydux.log_middleware import log_middleware



class MainWindow(QMainWindow):

    def __init__(self, store, parent=None):
        super(MainWindow, self).__init__(parent)
        self._store = store
        self._store.subscribe(self.listener)

        self.props = store.get_state()['main']
        self.setWindowTitle(self.props['program_name'])
        self.resize(
            self.props['default_size'][0],
            self.props['default_size'][1]
        )

        self.header = Header(store)
        self.footer = Footer(store)
        self.configPanel = ConfigPanel(
            self._store,
            self.filterRequiredArgs(),
            self.filterOptionalArgs()
        )

        self.bodyStack = QStackedWidget()
        self.bodyStack.addWidget(self.configPanel)
        self.bodyStack.addWidget(ConsolePanel(self._store))
        # self.bodyStack.setCurrentIndex(1)

        self.setCentralWidget(self.createCentralWiget())

    def createCentralWiget(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.header, alignment=Qt.AlignTop, stretch=0)
        layout.setSpacing(0)

        layout.addWidget(self.bodyStack, stretch=1)
        layout.setSpacing(0)

        layout.addWidget(self.footer)

        qwidget = QFrame()
        qwidget.setLayout(layout)
        qwidget.setFrameShape(QFrame.NoFrame)
        return qwidget

    def constructWidget(self, widget):
        import gooey.new_hotness.components.widgets as gooey_widgets
        if widget['type'] == 'MultiDirChooser':
            print('Ignoring MultiDirChooser')
            return None
        if widget['type'] == 'RadioGroup':
            print('Ignoring MultiDirChooser')
            return None
        return getattr(gooey_widgets, widget['type'])(
            self._store,
            widget['id'],
            widget['data']['display_name'],
            widget['data']['help'],
        )

    def filterRequiredArgs(self):
        # todo Required for _which_ subsection
        widgets = self._store.get_state()['widgets'].values()
        required = filter(lambda x: x['required'], widgets)
        components = map(self.constructWidget, required)
        return filter(None, components)

    def filterOptionalArgs(self):
        # todo Required for _which_ subsection
        widgets = self._store.get_state()['widgets'].values()
        required = filter(lambda x: not x['required'], widgets)
        components = map(self.constructWidget, required)
        return filter(None, components)

    def handleWidgetUpdate(self, action):
        self._state.widgets[action['id']].value = action['value']

    def listener(self):
        pass

    def handleStart(self):
        pass

    def handleStop(self):
        pass

    def handleClose(self):
        pass

    def handleRestart(self):
        pass





