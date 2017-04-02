import pytest

from gooey.gui.model import MyModel, MyWidget
from gooey.python_bindings.argparse_to_json import convert


@pytest.fixture
def choice_dict():
  return {
    "data": {
      "commands": [
        "-r",
        "--recursive"
      ],
      "display_name": "recursive",
      "help": "Recurse into subfolders",
      "default": None,
      "nargs": "",
      "choices": [
        "yes",
        "no"
      ]
    },
    "required": False,
    "type": "Dropdown"
  }


def test_widget_value_conversion(choice_dict):
  '''
  Choice boxes should follow a few rules:
    1. Not return place holder text (e.g. 'Select Option')
    2. Return a value if present, otherwise None
  '''
  choice_option = MyWidget.from_dict(choice_dict)
  assert choice_option.title == choice_dict['data']['display_name']
  assert choice_option.help == choice_dict['data']['help']
  assert choice_option.default == choice_dict['data']['default']
  assert choice_option.nargs == choice_dict['data']['nargs']
  assert choice_option.choices == choice_dict['data']['choices']
  assert choice_option.commands == choice_dict['data']['commands']
  assert choice_option.type == choice_dict['type']

  # UI's placeholder text should be ignored
  choice_option.value = 'Select Option'
  print choice_option._value
  assert choice_option.value == None



def _get_dropdown(widget_list):
  for widget in widget_list:
    if widget['type'] == 'Dropdown':
      return widget
  raise Exception("yo! You fed me a bad fixture, Homie")
