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
from gooey.new_hotness.containers.layouts import StandardFrame
from gooey.new_hotness.functional import assign
from gooey.new_hotness.components.header import Header
from operator import itemgetter
from pydux import create_store, combine_reducers
from pydux.thunk_middleware import thunk_middleware
from pydux.apply_middleware import apply_middleware
from pydux.log_middleware import log_middleware

from rx import Observable, Observer


class MainWindow(QMainWindow):

    def __init__(self, state, parent=None):
        super(MainWindow, self).__init__(parent)
        self._state = state

        self.setWindowTitle(self._state['program_name'])
        self.resize(*self._state['default_size'])

        self.header = Header(self)
        self.footer = Footer(self)

        self.configPanel = ConfigPanel(
            self._state,
            self.filterRequiredArgs(),
            self.filterOptionalArgs()
        )

        self.bodyStack = QStackedWidget()
        self.bodyStack.addWidget(self.configPanel)
        self.bodyStack.addWidget(ConsolePanel(self._state))
        # self.bodyStack.setCurrentIndex(1)

        self.container = StandardFrame(self.header, self.bodyStack, self.footer)
        self.setCentralWidget(self.container)

        # wire all the things
        self._state.map(itemgetter('title')).subscribe(self.header.setTitle)
        self._state.map(itemgetter('subtitle')).subscribe(self.header.setSubtitle)
        self._state.map(itemgetter('icon')).subscribe(self.header.setIcon)


    def createWidgetComponents(self, state):
        return map(self.constructWidget, state['widgets'])

    def constructWidget(self, widget):
        import gooey.new_hotness.components.widgets as gooey_widgets
        if widget['type'] == 'MultiDirChooser':
            print('Ignoring MultiDirChooser')
            return None
        if widget['type'] == 'RadioGroup':
            print('Ignoring MultiDirChooser')
            return None
        w = getattr(gooey_widgets, widget['type'])(
            self,
            widget['id'],
            widget['data']['display_name'],
            widget['data']['help'],
        )
        w.value.subscribe(self.handleWidgetUpdate)
        return w

    def filterRequiredArgs(self):
        # todo Required for _which_ subsection
        widgets = self._state['widgets'].values()
        required = filter(lambda x: x['required'], widgets)
        components = map(self.constructWidget, required)
        return filter(None, components)

    def filterOptionalArgs(self):
        # todo Required for _which_ subsection
        widgets = self._state['widgets'].values()
        required = filter(lambda x: not x['required'], widgets)
        components = map(self.constructWidget, required)
        return filter(None, components)

    def handleWidgetUpdate(self, action):
        self._state['widgets'][action['id']]['value'] = action['value']

    def handleStart(self):
        pass

    def handleStop(self):
        pass

    def handleClose(self):
        pass

    def handleRestart(self):
        pass





