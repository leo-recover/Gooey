from functools import reduce

import rx
from rx import Observable, Observer
from rx.subjects import BehaviorSubject
from rx.subjects import Subject


class StateContainer(Subject):
    def __init__(self, initialState=None):
        super(StateContainer, self).__init__()
        self._state = initialState or {}

    def __getitem__(self, item):
        return self._state[item]

    def __setitem__(self, key, value):
        self._state[key] = value
        self.on_next(self._state)


s = StateContainer({'one': {'two': 'qwer'}})

s.subscribe(print)

s['foo'] = 'bar'

s['one']['two'] = 'bar'
