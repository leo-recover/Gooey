from PyQt5.QtWidgets import QFileDialog

from gooey.new_hotness.components.widgets.chooser import Chooser


class MultiFileChooser(Chooser):
    launchDialog = QFileDialog.getOpenFileNames

    def processResult(self, result):
        return ', '.join(result[0])