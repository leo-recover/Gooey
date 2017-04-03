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
from gooey.gui.util.quoting import quote
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


def forType(target):
    return lambda action: action['type'] == target


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
        self.bodyStack.addWidget(ConsolePanel(self))
        # self.bodyStack.setCurrentIndex(1)

        self.container = StandardFrame(self.header, self.bodyStack, self.footer)
        self.setCentralWidget(self.container)

        # wire all the things
        self._state.map(itemgetter('title')).subscribe(self.header.setTitle)
        self._state.map(itemgetter('subtitle')).subscribe(self.header.setSubtitle)
        self._state.map(itemgetter('icon')).subscribe(self.header.setIcon)

        self.footer.buttons.filter(forType('START')).subscribe(self.handleStart)
        self.footer.buttons.filter(forType('CLOSE')).subscribe(self.handleStop)
        self.footer.buttons.filter(forType('STOP')).subscribe(self.handleClose)
        self.footer.buttons.filter(forType('RESTART')).subscribe(self.handleRestart)


    def createWidgetComponents(self, state):
        return map(self.constructWidget, state['widgets'])

    def constructWidget(self, widget):
        import gooey.new_hotness.components.widgets as gooey_widgets
        if widget['type'] == 'MultiDirChooser':
            print('Ignoring MultiDirChooser')
            return None
        if widget['type'] == 'RadioGroup':
            print('Ignoring RadioGroup')
            return None
        w = getattr(gooey_widgets, widget['type'])(self, widget)
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

    def handleStart(self, action):
        widgets = self._state['widgets'].values()
        required = list(filter(lambda x: x['required'], widgets))
        print(len(required))
        allGood = all(x.get('value') for x in required)
        if not allGood:
            print("Oh FUCK no, son!")
            print([(x['data']['display_name'], x.get('value')) for x in required])

        command = self.model.build_command_line_string()
        self.client_runner.run(command)
        # console statuses from the other thread
        pub.subscribe(self.on_new_message, 'console_update')
        pub.subscribe(self.on_progress_change, 'progress_update')
        pub.subscribe(self.on_client_done, 'execution_complete')
        # self.bodyStack.setCurrentIndex(1)

        self.client_runner.run(command)

    def build_command_line_string(self):
        optional_args = [arg.value for arg in self.optional_args]
        required_args = [c.value for c in self.required_args if c.commands]
        position_args = [c.value for c in self.required_args if not c.commands]
        if position_args:
            position_args.insert(0, "--")
        cmd_string = ' '.join(filter(None, chain(required_args, optional_args, position_args)))
        if self.layout_type == 'column':
            cmd_string = u'{} {}'.format(self.argument_groups[self.active_group].command, cmd_string)
        return u'{} --ignore-gooey {}'.format(self.build_spec['target'], cmd_string)


    def handleStop(self, action):
        self.close()

    def handleClose(self):
        pass

    def handleRestart(self):
        pass

    def getCleanValue(self, widget):

        if widget['type'] == 'CheckBox':
            return widget['commands'][0] if widget['value'] else None

        # if self.type == 'RadioGroup':
        #     try:
        #         return self.commands[self._value.index(True)][0]
        #     except ValueError:
        #         return None
        #
        # if self.type == 'MultiFileChooser':
        #     value = ' '.join(quote(x) for x in self._value.split(os.pathsep) if x)
        #     if self.commands and value:
        #         return u'{} {}'.format(self.commands[0], value)
        #     return value or None

        if widget['type'] == 'Textarea':
            if widget['commands'] and widget['value']:
                return '{} {}'.format(widget['commands'][0], quote(widget['value'].encode('unicode_escape')))
            else:
                return quote(widget['value'].encode('unicode_escape')) if widget['value'] else ''
        if widget['type'] == 'CommandField':
            if widget['commands'] and widget['value']:
                return u'{} {}'.format(widget['commands'][0], widget['value'])
            else:
                return widget['value'] or None

        if widget['type'] == 'Counter':
            '''
            Returns
              str(option_string * DropDown Value)
              e.g.
              -vvvvv
            '''
            if not str(widget['value']).isdigit():
                return None
            arg = str(widget['commands'][0]).replace('-', '')
            repeated_args = arg * int(widget['value'])
            return '-' + repeated_args

        if widget['type'] == 'Dropdown':
            if widget['value'] == 'Select Option':
                return None
            elif widget['commands'] and widget['value']:
                return u'{} {}'.format(widget['commands'][0], quote(widget['value']))
            else:
                return quote(widget['value']) if widget['value'] else ''
        else:
            if widget['commands'] and widget['value']:
                if not widget['data']['nargs']:
                    v = quote(widget['value'])
                else:
                    v = widget['value']
                return u'{0} {1}'.format(widget['commands'][0], v)
            else:
                if not widget['value']:
                    return None
                elif not widget['data']['nargs']:
                    return quote(widget['value'])
                else:
                    return widget['value']

