from PyQt5.QtWidgets import QLabel, QFrame
from PyQt5.QtWidgets import QScrollArea
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget

from gooey.new_hotness.components.general import hline


class ConfigPanel(QScrollArea):
    def __init__(self, store, required, optional, *args, **kwargs):
        super(ConfigPanel, self).__init__(*args, **kwargs)
        self._store = store
        self._store.subscribe(self.state_to_props)
        self.layoutComponent(required, optional)

    def layoutComponent(self, required, optional):
        layout = QVBoxLayout()

        layout.addSpacing(10)
        layout.addWidget(QLabel('<h2>Required Arguments</h2>'))
        layout.addWidget(hline())
        layout.addSpacing(10)

        for widget in required:
            layout.addLayout(widget.layout)

        layout.addSpacing(15)
        layout.addWidget(QLabel('<h2>Optional Arguments</h2>'))
        layout.addWidget(hline())
        layout.addSpacing(15)
        for widget in optional:
            layout.addLayout(widget.layout)

        w = QWidget()
        w.setContentsMargins(0, 0, 0, 0)
        w.setLayout(layout)
        self.setWidget(w)
        self.setWidgetResizable(True)

    def state_to_props(self):
        pass