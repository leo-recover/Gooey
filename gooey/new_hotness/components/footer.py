from itertools import groupby

from PyQt5.QtWidgets import QHBoxLayout, \
    QStackedWidget, QProgressBar
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QWidget

from functools import partial
from operator import itemgetter



class Footer(QWidget):
    button_details = [
        {'label': 'Cancel', 'type': 'CANCEL', 'group': 'config'},
        {'label': 'Start', 'type': 'START', 'group': 'config'},
        {'label': 'Stop', 'type': 'STOP', 'group': 'running'},
        {'label': 'Edit', 'type': 'EDIT', 'group': 'complete'},
        {'label': 'Restart', 'type': 'RESTART', 'group': 'complete'},
        {'label': 'Quit', 'type': 'QUIT', 'group': 'complete'},
    ]

    def __init__(self, store, *args, **kwargs):
        super(Footer, self).__init__(*args, **kwargs)
        self._store = store
        self._store.subscribe(self.receiveChanges)

        self.progressBar = QProgressBar()
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(0)

        self.spacer = QWidget()
        self.buttonStack = self.createButtonStack()
        self.layoutComponent()

    def createButtonStack(self):
        def dispatch(action, *args, **kwargs):
            self._store.dispatch({'type': action})

        buttonStack = QStackedWidget()
        groups = groupby(self.button_details, itemgetter('group'))
        for group, details in groups:
            q = QWidget()
            layout = QHBoxLayout()
            for item in details:
                appliedDispatch = partial(dispatch, item['type'])
                button = QPushButton(item['label'])
                button.clicked.connect(appliedDispatch)
                layout.addWidget(button)
            q.setLayout(layout)
            buttonStack.addWidget(q)
        return buttonStack

    def layoutComponent(self):
        layout = QHBoxLayout()
        layout.addWidget(self.progressBar, stretch=1)
        layout.addWidget(self.spacer, stretch=1)
        layout.addWidget(self.buttonStack)
        self.progressBar.setVisible(False)
        self.spacer.setVisible(True)

        self.setLayout(layout)
        self.setMinimumHeight(60)
        self.setMaximumHeight(60)

    def receiveChanges(self):
        # swap button stack depending on state
        # hide/show progressbar
        # other
        pass

