import json
import sys
from uuid import uuid4

from PyQt5.QtWidgets import QFileDialog, QCalendarWidget, QDialogButtonBox, \
    QComboBox, QCheckBox

from PyQt5 import QtGui

from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QFrame, QDialog
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit, QTextEdit, QPlainTextEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QScrollArea
from PyQt5.QtWidgets import QWidget, QMainWindow

from copy import deepcopy
from functools import reduce
from gooey.new_hotness.date_dialog import DateDialog
from pydux import create_store, combine_reducers

from rx.subjects import Subject

class TextContainer(QWidget):
    '''
    Primary Base component for all Text Input components
    '''

    widget_class = None

    def __init__(self, store, _id, label, help_text, *args, **kwargs):
        super(TextContainer, self).__init__(*args, **kwargs)
        self._store = store
        self._store.subscribe(self.receiveChange)

        self._id = _id
        self.label = QLabel('<b>{}</b>'.format(label))
        self.help_text = QLabel(help_text)
        self._widget = self.getWidget()
        self.layout = self.arrange(self.label, self.help_text)
        self.widget = Subject()
        self.connectSignal()

    def getWidget(self):
        return self.widget_class()

    def arrange(self, label, text):
        layout = QVBoxLayout()
        layout.addWidget(label, alignment=Qt.AlignTop)
        if text:
            layout.addWidget(text)
        else:
            layout.addStretch(1)
        layout.addLayout(self.getSublayout())
        return layout

    def connectSignal(self):
        self._widget.textChanged.connect(self.dispatchChange)

    def getSublayout(self, *args, **kwargs):
        raise NotImplementedError

    def receiveChange(self, *args, **kwargs):
        raise NotImplementedError

    def dispatchChange(self, value, **kwargs):
        raise NotImplementedError


class TextField(TextContainer):
    widget_class = QLineEdit

    def getSublayout(self, *args, **kwargs):
        layout = QHBoxLayout()
        layout.addWidget(self._widget)
        return layout

    def receiveChange(self):
        pass
        # print('self._id:::', self._id)
        # currentValue = self._store.get_state()['widgets'][self._id]['value']
        # self._widget.setText(str(currentValue))

    def dispatchChange(self, value, **kwargs):
        print('dispatching change for component with ID:', self._id)
        self.widget.on_next({
            'type': 'UPDATE_WIDGET',
            'value': value,
            'id': self._id
        })


class PasswordField(TextField):
    def __init__(self, *args, **kwargs):
        super(PasswordField, self).__init__(*args, **kwargs)
        self._widget.setEchoMode(QLineEdit.Password)


class Textarea(TextField):
    widget_class = QTextEdit

    def receiveChange(self):
        currentState = self._store.get_state()['widgets'][self._id]['value']
        print('received_change! current state = ', currentState)
        if self._widget.toPlainText() != currentState:
            self._widget.document().setPlainText(currentState)

    def dispatchChange(self, *args, **kwargs):
        print('dispatching change for component with ID:', self._id)
        self.widget.on_next({
            'type': 'UPDATE_WIDGET',
            'value':  self._widget.toPlainText(),
            'id': self._id
        })


class Chooser(TextField):
    widget_class = QLineEdit
    launchDialog = None

    def getSublayout(self, *args, **kwargs):
        self.button = QPushButton('Browse')
        self.button.clicked.connect(self.spawnDialog)

        layout = QHBoxLayout()
        layout.addWidget(self._widget, stretch=1)
        layout.addWidget(self.button)
        return layout

    def spawnDialog(self, *args, **kwargs):
        if not callable(self.launchDialog):
            raise AssertionError(
                'Chooser subclasses must provide QFileDialog callable '
                'to launchDialog property (.e.g '
                '`launchDialog = QFileDialog.getOpenFileName`'
            )
        result = self.launchDialog(parent=self)
        if result:
            self.dispatchChange(self.processResult(result))

    def processResult(self, result):
        return result[0]


# TODO: unify all of the return types Qt throws out
# TODO: of the various Dialogs
class DateChooser(Chooser):
    launchDialog = DateDialog.getUserSelectedDate


class FileSaver(Chooser):
    launchDialog = QFileDialog.getSaveFileName


class FileChooser(Chooser):
    launchDialog = QFileDialog.getOpenFileName


class MultiFileChooser(Chooser):
    launchDialog = QFileDialog.getOpenFileNames

    def processResult(self, result):
        return ', '.join(result[0])


class DirectoryChooser(Chooser):
    launchDialog = QFileDialog.getExistingDirectory

    def processResult(self, result):
        return result


class Dropdown(TextContainer):
    widget_class = QComboBox

    def getSublayout(self, *args, **kwargs):
        layout = QHBoxLayout()
        layout.addWidget(self._widget)
        return layout

    def connectSignal(self):
        self._widget.currentIndexChanged.connect(self.dispatchChange)

    def receiveChange(self, *args, **kwargs):
        widget_details = self._store.get_state()['widgets'][self._id]['data']

        if len(widget_details['choices']) != self._widget.count():
            for _ in range(self._widget.count()):
                self._widget.removeItem(0)
            for choice in widget_details['choices']:
                self._widget.addItem(choice)

        currentIndex = self._store.get_state()['widgets'][self._id]['value']
        if currentIndex and currentIndex != self._widget.currentIndex():
            self._widget.setCurrentIndex(currentIndex or 0)

    def dispatchChange(self, value, **kwargs):
        QTimer.singleShot(0, lambda: self._store.dispatch({
            'type': 'UPDATE_WIDGET',
            'value': value,
            'id': self._id,
            'updateId': uuid4()
        }))


class Counter(Dropdown):
    pass


class CheckBox(QWidget):

    def __init__(self, store, _id, label, help_text, *args, **kwargs):
        super(CheckBox, self).__init__(*args, **kwargs)
        self._store = store
        self._store.subscribe(self.receiveChange)

        print(label, help_text, args, kwargs)

        self._id = _id
        self.label = QLabel('<b>{}</b>'.format(label))
        self._widget = QCheckBox(help_text or '')

        self.layout = self.arrange()

        self.connectSignal()

    def arrange(self):
        layout = QVBoxLayout()
        layout.addWidget(self.label, alignment=Qt.AlignTop)
        layout.addWidget(self._widget)
        return layout


    def connectSignal(self):
        self._widget.stateChanged.connect(self.dispatchChange)

    def receiveChange(self, *args, **kwargs):
        print('TODO: CheckBox receiveChange')

    def dispatchChange(self, value, **kwargs):
        print('TODO: CheckBox dispatchChange')