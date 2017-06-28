from gooey.new_hotness.components.widgets.dropdown import Dropdown
from gooey.new_hotness import formatters

class Counter(Dropdown):

    def formatOutput(self, metadata, value):
        return formatters.counter(metadata, value)
