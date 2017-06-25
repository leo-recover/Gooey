from PyQt5.QtWidgets import QLabel, QHBoxLayout, QFrame
from PyQt5.QtWidgets import QScrollArea
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget

from new_hotness.components.general import line
from new_hotness.util import chunk


class ConfigPanel(QScrollArea):
    def __init__(self, store, required, optional, *args, **kwargs):
        super(ConfigPanel, self).__init__(*args, **kwargs)
        self.setFrameShape(QFrame.NoFrame)
        self.layoutComponent(required, optional)

    def layoutComponent(self, required, optional):
        layout = QVBoxLayout()

        if required:
            self.buildSection(layout, 'Required Arguments', 10, required)

        if optional:
            self.buildSection(layout, 'Optional Arguments', 15, optional)
 
        w = QWidget(self)
        w.setContentsMargins(0, 0, 0, 0)
        w.setLayout(layout)
        self.setWidget(w)
        self.setWidgetResizable(True)

    def buildSection(self, layout, sectionName, padding, widgets):
        layout.addSpacing(padding)
        layout.addWidget(QLabel('<h2>{}</h2>'.format(sectionName)))
        layout.addWidget(line(self, QFrame.HLine))
        layout.addSpacing(10)

        for widgetchunks in chunk(widgets, 1):
            sublayout = QHBoxLayout()
            for widget in widgetchunks:
                if widget:
                    sublayout.addLayout(widget.layout, 1)
                else:
                    sublayout.addStretch(1)

            layout.addLayout(sublayout)


