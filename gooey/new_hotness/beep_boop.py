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
    return new_buildspec


def load_initial_state():
    with open('gooey_config.json', 'r') as f:
        data = json.loads(f.read())
        return gooey1to2(data)



def gooey_reducer(state, action):
    if state is None:
        return {}
    elif action['type'] == 'RECEIVED_STATE':
        return assign({}, state, action['state'])
    elif action['type'] == 'UPDATE_HEADER_TITLE':
        return assign({}, state, {'title': action['title']})
    elif action['type'] == 'UPDATE_HEADER_SUBTITLE':
        return assign({}, state, {'subtitle': action['subtitle']})
    else:
        return state


def widget_reducer(state, action):
    if state == None:
        return {}
    elif action['type'] == 'RECEIVED_WIDGET':
        return assign({}, state, action['widgets'])
    elif action['type'] == 'UPDATE_WIDGET':
        print('state:', state)
        return assign({}, state, {
            action['id']: assign({}, state[action['id']], {
                'value': action['value']
            })
        })
    else:
        return state



# need to put buildspec defaults in here before passing down to Form object
store = create_store(combine_reducers({
    'main': gooey_reducer,
    'widgets': widget_reducer
}), enhancer=apply_middleware(thunk_middleware, log_middleware))


state = load_initial_state()
widgets = state.pop('widgets')


store.dispatch({
    'type': 'RECEIVED_STATE',
    'state': state
})

store.dispatch({
    'type': 'RECEIVED_WIDGET',
    'widgets': widgets
})


# store.dispatch({
#     'type': 'UPDATE_HEADER_TITLE',
#     'title': 'Yo dawg'
# })


sys._excepthook = sys.excepthook

def my_exception_hook(exctype, value, traceback):
    # Print the error and traceback
    print(exctype, value, traceback)
    # Call the normal Exception hook after
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)

# Set the exception hook to our wrapping function
sys.excepthook = my_exception_hook


# ----------------------------
# Qt ordering
# 1. Create QApp
app = QApplication(sys.argv)
# 2. initialize all our forum junk
form = MainWindow(store)
# 3. Now that the form objects actually exist, dispatch any initial junk that's
# required

# store.dispatch({
#     'type': '@@INIT',
#     'widgets': widgets
# })

# show
form.show()

app.exec_()
