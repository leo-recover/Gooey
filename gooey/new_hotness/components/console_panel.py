from PyQt5.QtWidgets import QVBoxLayout, QTextEdit
from PyQt5.QtWidgets import QWidget


class ConsolePanel(QWidget):

    def __init__(self, store, *args, **kwargs):
        super(ConsolePanel, self).__init__(*args, **kwargs)
        self._store = store
        # self._store.subscribe(self.receiveChanges)
        self.widget = QTextEdit()
        self.widget.setReadOnly(True)
        self.layoutComponent()

    def layoutComponent(self):
        layout = QVBoxLayout()
        layout.addWidget(self.widget, stretch=1)
        self.setLayout(layout)

    def receiveChanges(self):
        pass

    def dispatchChanges(self):
        pass
