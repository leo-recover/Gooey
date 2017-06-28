from operator import itemgetter

from PyQt5.QtWidgets import QMainWindow, QMessageBox, QPushButton
from PyQt5.QtWidgets import QStackedWidget

import gooey.new_hotness.components.widgets as gooey_widgets
from gooey.new_hotness.components.config_panel import ConfigPanel
from gooey.new_hotness.components.console_panel import ConsolePanel
from gooey.new_hotness.components.footer import Footer
from gooey.new_hotness.components.header import Header
from gooey.new_hotness.containers.layouts import StockLayout, SplitLayout
from new_hotness.commandline import build_cmd_str
from new_hotness.components.sidebar import Sidebar
from new_hotness.util import isRequired, isOptional, belongsTo, flatten, forEvent

from gooey.gui.processor import ProcessController

class MainWindow(QMainWindow):

    def __init__(self, state, parent=None):
        super(MainWindow, self).__init__(parent)

        self.clientRunner = ProcessController('', '')

        self._state = state

        self.setWindowTitle(self._state['program_name'])
        self.resize(*self._state['default_size'])

        self.header = Header(self)
        self.footer = Footer(self)

        self.sidebar = Sidebar(self, state['groups'].keys())
        self.qwidgets = self.constructWidgets(state)
        self.configPanels = self.buildConfigStack(state, self.qwidgets)
        self.configPanels.setCurrentIndex(0)

        self.configScreen = SplitLayout(
            self,
            self.sidebar,
            self.configPanels
        )

        self.console = ConsolePanel(self)

        self.bodyStack = QStackedWidget(self)
        self.bodyStack.addWidget(self.configScreen)
        self.bodyStack.addWidget(self.console)

        self.container = StockLayout(self.header, self.bodyStack, self.footer)
        self.setCentralWidget(self.container)

        self._state.map(itemgetter('title')).subscribe(self.header.setTitle)
        self._state.map(itemgetter('subtitle')).subscribe(self.header.setSubtitle)
        self._state.map(itemgetter('icon')).subscribe(self.header.setIcon)
        self.footer.buttons.filter(forEvent('START')).subscribe(self.handleStart)
        self.footer.buttons.filter(forEvent('CLOSE')).subscribe(self.handleStop)
        self.footer.buttons.filter(forEvent('STOP')).subscribe(self.handleClose)
        self.footer.buttons.filter(forEvent('RESTART')).subscribe(self.handleRestart)
        self.sidebar.value.subscribe(self.handleSidebarChange)
        for widget in flatten(self.qwidgets):
            widget.value.subscribe(self.handleWidgetUpdate)

        # Hide the sidebar if we're not in a sub-parser mode
        if len(state['groups']) == 1:
            self.configScreen.left.setVisible(False)


    def constructWidgets(self, state):
        output = []
        groups, widgets = state['groups'].keys(), state['widgets']
        for group in groups:
            groupedWidgets = list(filter(belongsTo(group), widgets.values()))
            required = list(filter(isRequired, groupedWidgets))
            optional = list(filter(isOptional, groupedWidgets))

            rout = []
            oout = []
            for widget in required:
                widget_class = getattr(gooey_widgets, widget['type'])
                rout.append(widget_class(self, widget))
            for widget in optional:

                widget_class = getattr(gooey_widgets, widget['type'])
                oout.append(widget_class(self, widget))

            output.append((rout, oout))
        return output


    def buildConfigStack(self, state, qwidgets):
        stack = QStackedWidget(self)
        for required, optional in qwidgets:
            stack.addWidget(ConfigPanel(state, required, optional))
        return stack


    def handleSidebarChange(self, action):
        self._state['activeGroup'] = action['group']
        self.configPanels.setCurrentIndex(action['value'])


    def handleWidgetUpdate(self, action):
        print("Yo", action)
        self._state['widgets'][action['id']]['cmd'] = action['cmd']


    def handleStart(self, action):
        activeGroup = self._state['activeGroup']
        activeWidgets = list(filter(belongsTo(activeGroup), self._state['widgets'].values()))
        if not self.hasRequiredArgs(activeWidgets):
            self.launchDialog(
                "Required Arguments",
                "Please supply values for all required arguments "
            )

        command = build_cmd_str(
            self._state,
            list(filter(belongsTo(activeGroup),
            self._state['widgets'].values()))
        )

        self.clientRunner.run(command)
        self.clientRunner.subject.subscribe(self.doThing)

        # console statuses from the other thread
        # pub.subscribe(self.on_new_message, 'console_update')
        # pub.subscribe(self.on_progress_change, 'progress_update')
        # pub.subscribe(self.on_client_done, 'execution_complete')
        self.bodyStack.setCurrentIndex(1)

        # self.client_runner.run(command)


    def doThing(self, event):
        print(event)
        try:
            self.console.widget.append(event.get('console_update').decode('utf-8'))
            c = self.console.widget.textCursor()
            c.movePosition(c.End)
            self.console.widget.setTextCursor(c)
        except Exception as e:
            print(e)

    def hasRequiredArgs(self, widgets):
        # todo: basic type validation (e.g. 'must be number')
        required = list(filter(isRequired, widgets))
        for i in required:
            print(i['type'], i.get('cmd'))
        return all(x.get('cmd') for x in required)
        # allGood = all(x.get('value') for x in required)
        # if not allGood:
        #     print("Oh FUCK no, son!")
        #     print([(x['data']['display_name'], x.get('value'))
        #            for x in required
        #            if not x['value']])




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


    def launchDialog(self, title, body):
        # QWidget, p_str, p_str_1, buttons, QMessageBox_StandardButtons=None, QMessageBox_StandardButton=None,
        QMessageBox.warning(self,
                            title, body, QMessageBox.Ok, QMessageBox.NoButton)

