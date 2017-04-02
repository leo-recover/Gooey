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

'''
function navigateTo(item) {

    var mainTab = item.toLowerCase();
    var main_navbar = $('ul[data-qa="main-navbar"]');
    var mainTabToClick;

    switch (mainTab) {
        case 'search':
            mainTabToClick = main_navbar.$$('li').get(0);
            break;
        case 'upload':
            mainTabToClick = main_navbar.$$('li').get(1);
            break;
        case 'feeds':
            mainTabToClick = main_navbar.$$('li').get(2);
            break;
        case 'trust':
            mainTabToClick = main_navbar.$$('li').get(3);
            break;
        case 'admin':
            mainTabToClick = main_navbar.$$('li').get(4);
            break;
        case 'getting started':
            mainTabToClick = main_navbar.$$('li').get(5);
            break;
    }

    mainTabToClick.click();
}
'''