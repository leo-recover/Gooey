from PyQt5.QtWidgets import QFileDialog

from gooey.new_hotness.components.widgets.chooser import Chooser
from gooey.new_hotness import formatters

class MultiFileChooser(Chooser):
    launchDialog = QFileDialog.getOpenFileNames

    def processResult(self, result):
        return ', '.join(result[0])

    def formatOutput(self, metatdata, value):
        return formatters.multiFileChooser(metatdata, value)
