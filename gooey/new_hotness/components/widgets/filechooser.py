from PyQt5.QtWidgets import QFileDialog

from gooey.new_hotness.components.widgets.chooser import Chooser


class FileChooser(Chooser):
    launchDialog = QFileDialog.getOpenFileName


