from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtWidgets import QStackedWidget

import gooey.new_hotness.components.widgets as gooey_widgets
from gooey.gui.processor import ProcessController
from gooey.new_hotness.components.config_panel import ConfigPanel
from gooey.new_hotness.components.console_panel import ConsolePanel
from gooey.new_hotness.components.footer import Footer
from gooey.new_hotness.components.header import Header
from gooey.new_hotness.containers.layouts import StockLayout, SplitLayout
from gui import image_repository
from new_hotness.commandline import build_cmd_str
from new_hotness.components.sidebar import Sidebar
from new_hotness.util import isRequired, isOptional, belongsTo, flatten, forEvent
from new_hotness.util import nestedget


class MainWindow(QMainWindow):
    # todo: proper controller

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

        self._state.map(nestedget(['gooey_state', 'title'])).subscribe(self.header.setTitle)
        self._state.map(nestedget(['gooey_state', 'subtitle'])).subscribe(self.header.setSubtitle)
        self._state.map(nestedget(['gooey_state', 'icon'])).subscribe(self.header.setIcon)
        self._state.map(nestedget(['gooey_state', 'window'])).subscribe(self.setActiveBody)
        self._state.map(nestedget(['gooey_state', 'buttonGroup'])).subscribe(self.footer.setVisibleGroup)
        self.footer.buttons.filter(forEvent('START')).subscribe(self.handleStart)
        self.footer.buttons.filter(forEvent('STOP')).subscribe(self.handleStop)
        self.footer.buttons.filter(forEvent('CLOSE')).subscribe(self.handleClose)
        self.footer.buttons.filter(forEvent('RESTART')).subscribe(self.handleStart)
        self.footer.buttons.filter(forEvent('QUIT')).subscribe(self.handleClose)
        self.footer.buttons.filter(forEvent('EDIT')).subscribe(self.handleEdit)
        self.sidebar.value.subscribe(self.handleSidebarChange)
        for widget in flatten(self.qwidgets):
            widget.value.subscribe(self.handleWidgetUpdate)

        # Hide the sidebar if we're not in a sub-parser mode
        if len(state['groups']) == 1:
            self.configScreen.hideLeft()


    def setActiveBody(self, index):
        self.bodyStack.setCurrentIndex(index)


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
        self._state['widgets'][action['id']]['cmd'] = action['cmd']


    def handleStart(self, action):
        activeGroup = self._state['activeGroup']
        activeWidgets = list(filter(belongsTo(activeGroup), self._state['widgets'].values()))
        # if not self.hasRequiredArgs(activeWidgets):
        #     self.launchDialog(
        #         "Required Arguments",
        #         "Please supply values for all required arguments "
        #     )
        #     return

        command = build_cmd_str(
            self._state,
            list(filter(belongsTo(activeGroup),
            self._state['widgets'].values()))
        )

        self.do2()

        self.clientRunner.run(command)
        self.clientRunner.subject.subscribe(
            on_next=self.doThing,
            on_error=lambda *args, **kwargs: print('ERROR!', args, kwargs)
        )



    def doThing(self, event):
        if event.get('completed'):
            self.doOtherThing()
            return
        try:
            self.console.widget.append(event.get('console_update').decode('utf-8'))
            c = self.console.widget.textCursor()
            c.movePosition(c.End)
            self.console.widget.setTextCursor(c)
        except Exception as e:
            print(e)


    def doOtherThing(self):
        if self.clientRunner.was_success():
            self.do3()
        else:
            self.do4()


    def hasRequiredArgs(self, widgets):
        # todo: basic type validation (e.g. 'must be number')
        required = list(filter(isRequired, widgets))
        for i in required:
            print(i['type'], i.get('cmd'))
        return all(x.get('cmd') for x in required)



    def handleStop(self, action):
        if self.confirmStop():
            self.clientRunner.stop()


    def handleClose(self, action):
        self.close()


    def handleRestart(self, action):
        print('Handling restart')
        self.handleStart(action)


    def handleEdit(self, action):
        self.do1()

    def launchDialog(self, title, body):
        QMessageBox.warning(
            self, title, body, QMessageBox.Ok, QMessageBox.NoButton
        )


    def launchConfirmDialog(self, title, body):
        result = QMessageBox.question(
            self, title, body, QMessageBox.Ok, QMessageBox.Cancel
        )
        return result == QMessageBox.Ok


    def confirmStop(self):
        return self.launchConfirmDialog(
            'Are you sure you want to stop?',
            'Do it?'
        )


    def do1(self):
        self._state['gooey_state'] = {
            'icon': image_repository.config_icon,
            'title': 'Settings',
            'subtitle': 'Example program demonstrating things',
            'window': 0,
            'buttonGroup': 0
        }

    def do2(self):
        self._state['gooey_state'] = {
            'icon': image_repository.running_icon,
            'title': 'Running',
            'subtitle': 'Please wait',
            'window': 1,
            'buttonGroup': 1
        }

    def do3(self):
        self._state['gooey_state'] = {
            'icon': image_repository.success_icon,
            'title': 'Success',
            'subtitle': 'Program is now complete',
            'window': 1,
            'buttonGroup': 2
        }

    def do4(self):
        self._state['gooey_state'] = {
            'icon': image_repository.error_icon,
            'title': 'Error',
            'subtitle': 'An error occurred while running',
            'window': 1,
            'buttonGroup': 2
        }

