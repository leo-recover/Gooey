import json
import sys
from uuid import uuid4

from PyQt5.QtWidgets import QApplication

from copy import deepcopy
from gooey.new_hotness.containers.application import MainWindow
from gooey.new_hotness.functional import assign
from pydux import create_store, combine_reducers
from pydux.apply_middleware import apply_middleware
from pydux.log_middleware import log_middleware
from pydux.thunk_middleware import thunk_middleware
from rx.subjects import Subject


def app_reducer(state, action):
    if action['type'] == 'pass':
        pass

def gooey1to2(buildspec):
    '''
    Still figuring out exactly how I want everything arranged..
    '''
    root_commands = []
    widgets = []

    for parent_name, val in buildspec['widgets'].items():
        root_commands.append({'name': parent_name, 'command': val['command']})

        for widget in val['contents']:
            new_widget = deepcopy(widget)
            new_widget['parent'] = parent_name
            if not widget['type'] == 'RadioGroup':
                if new_widget['type'] == 'DirChooser':
                    new_widget['type'] = 'DirectoryChooser'
                new_widget['value'] = widget['data']['default']
            else:
                new_widget['value'] = None
            new_widget['id'] = str(uuid4())
            widgets.append(new_widget)

    widget_map = {widget['id']: widget for widget in widgets}
    new_buildspec = deepcopy(buildspec)
    new_buildspec['root_commands'] = root_commands
    new_buildspec['widgets'] = widget_map
    new_buildspec['title'] = 'Settings'
    new_buildspec['subtitle'] = new_buildspec['program_description']
    new_buildspec['icon'] = '../images/config_icon.png'
    return new_buildspec


def load_initial_state():
    with open('gooey_config.json', 'r') as f:
        data = json.loads(f.read())
        return gooey1to2(data)


class StateContainer(Subject):
    def __init__(self, initialState=None):
        super(StateContainer, self).__init__()
        self._state = initialState or {}

    def __getitem__(self, item):
        return self._state[item]

    def __setitem__(self, key, value):
        self._state[key] = value
        self.on_next(self._state)




sys._excepthook = sys.excepthook

def my_exception_hook(exctype, value, traceback):
    # Print the error and traceback
    print(exctype, value, traceback)
    # Call the normal Exception hook after
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)

# Set the exception hook to our wrapping function
sys.excepthook = my_exception_hook



state = StateContainer(load_initial_state())
# ----------------------------
# Qt ordering
# 1. Create QApp
app = QApplication(sys.argv)
# 2. initialize all our forum junk
form = MainWindow(state)
# 3. Now that the form objects actually exist, dispatch any initial junk that's
# required

state['title'] = 'Foobar'
state['title'] = 'Settings'
state['icon'] = '../images/config_icon.png'
# store.dispatch({
#     'type': '@@INIT',
#     'widgets': widgets
# })

# show
form.show()

app.exec_()
