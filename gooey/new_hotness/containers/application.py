from operator import itemgetter

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QStackedWidget

import gooey.new_hotness.components.widgets as gooey_widgets
from gooey.new_hotness.components.config_panel import ConfigPanel
from gooey.new_hotness.components.console_panel import ConsolePanel
from gooey.new_hotness.components.footer import Footer
from gooey.new_hotness.components.header import Header
from gooey.new_hotness.containers.layouts import StockLayout, SplitLayout
from new_hotness.components.sidebar import Sidebar
from new_hotness.util import isRequired, isOptional, belongsTo, flatten, forEvent



class MainWindow(QMainWindow):

    def __init__(self, state, parent=None):
        super(MainWindow, self).__init__(parent)
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

        self.bodyStack = QStackedWidget(self)
        self.bodyStack.addWidget(self.configScreen)
        self.bodyStack.addWidget(ConsolePanel(self))

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
        self._state['widgets'][action['id']]['value'] = action['value']


    def handleStart(self, action):
        group = self._state['activeGroup']
        widgets = filter(belongsTo(group), self._state['widgets'].values())
        required = list(filter(lambda x: x['required'], widgets))
        print(len(required))
        allGood = all(x.get('value') for x in required)
        if not allGood:
            print("Oh FUCK no, son!")
            print([(x['data']['display_name'], x.get('value')) for x in required])

        # command = self.model.build_command_line_string()
        # self.client_runner.run(command)
        # # console statuses from the other thread
        # pub.subscribe(self.on_new_message, 'console_update')
        # pub.subscribe(self.on_progress_change, 'progress_update')
        # pub.subscribe(self.on_client_done, 'execution_complete')
        # self.bodyStack.setCurrentIndex(1)
        #
        # self.client_runner.run(command)


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



