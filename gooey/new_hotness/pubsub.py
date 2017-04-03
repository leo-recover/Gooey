from collections import defaultdict

class PubSub:
    def __init__(self):
        self.state = {}

    def dispatch(self, event, action):
        for handler in self.state.get(event, []):
            handler(action)

    def subscribe(self, event, handler):
        self.state[event].append(handler)

    def notify(self):
        pass


pub = PubSub()

pub.subscribe('bark', lambda action: print('b1', action))
pub.subscribe('bark', lambda action: print('b2', action))
pub.subscribe('bark', lambda action: print('b3', action))
pub.subscribe('bark', lambda action: print('b4', action))

pub.dispatch('bark', {'type': 'RUFF'})

