from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QHBoxLayout

from gooey.new_hotness.components.widgets.bases import TextContainer


class Dropdown(TextContainer):
    widget_class = QComboBox

    def __init__(self, parent, widgetInfo, *args, **kwargs):
        super(Dropdown, self).__init__(parent, widgetInfo, *args, **kwargs)

        # initialize dropdown values
        for choice in widgetInfo['data']['choices']:
            self.widget.addItem(choice)

        if widgetInfo['data']['default']:
            self.setValue(widgetInfo['data']['default'])

    def getSublayout(self, *args, **kwargs):
        layout = QHBoxLayout()
        layout.addWidget(self.widget)
        return layout

    def connectSignal(self):
        self.widget.currentIndexChanged.connect(self.dispatchChange)

    def setValue(self, value):
        self.widget.setCurrentIndex(value)

    def dispatchChange(self, value, **kwargs):
        self.value.on_next({'value': value, 'id': self._id})
        # QTimer.singleShot(0, lambda: self._store.dispatch({})