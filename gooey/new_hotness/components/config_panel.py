from PyQt5.QtWidgets import QLabel, QFrame
from PyQt5.QtWidgets import QScrollArea
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget
 
from gooey.new_hotness.components.general import hline
 
 
class ConfigPanel(QScrollArea):
    def __init__(self, store, required, optional, *args, **kwargs):
        super(ConfigPanel, self).__init__(*args, **kwargs)
        self.layoutComponent(required, optional)
 
    def layoutComponent(self, required, optional):
        layout = QVBoxLayout()

        if required:
            self.buildSection(layout, 'Required Arguments', 10, required)

        if optional:
            self.buildSection(layout, 'Optional Arguments', 15, optional)
 
        w = QWidget()
        w.setContentsMargins(0, 0, 0, 0)
        w.setLayout(layout)
        self.setWidget(w)
        self.setWidgetResizable(True)

    def buildSection(self, layout, sectionName, padding, widgets):
        layout.addSpacing(padding)
        layout.addWidget(QLabel('<h2>{}</h2>'.format(sectionName)))
        layout.addWidget(hline())
        layout.addSpacing(10)

        for widget in widgets:
            layout.addLayout(widget.layout)

