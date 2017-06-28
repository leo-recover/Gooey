from gooey.new_hotness.components.widgets.textfield import TextField
from gooey.new_hotness import formatters

class Counter(TextField):

    def formatOutput(self, metadata, value):
        return formatters.commandField(metadata, value)
