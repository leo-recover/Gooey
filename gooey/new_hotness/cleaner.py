import os

from gooey.gui.util.quoting import quote


def formatCheckbox(widget):
    return widget._meta['commands'][0] if widget['value'] else None


def RadioGroup(widget):
    try:
        return self.commands[self._value.index(True)][0]
    except ValueError:
        return None


def MultiFileChooser(widget):
    value = ' '.join(quote(x) for x in widget['value'].split(os.pathsep) if x)
    if widget['commands'] and value:
        return u'{} {}'.format(widget['commands'][0], value)
    return value or None


def TextArea(widget):
    if widget['commands'] and widget['value']:
        return '{} {}'.format(widget['commands'][0], quote(widget['value'].encode('unicode_escape')))
    else:
        return quote(widget['value'].encode('unicode_escape')) if widget['value'] else ''


def CommandField(widget):
    if widget['commands'] and widget['value']:
        return u'{} {}'.format(widget['commands'][0], widget['value'])
    else:
        return widget['value'] or None


def Counter(widget):
    '''
    Returns
      str(option_string * DropDown Value)
      e.g.
      -vvvvv
    '''
    if not str(widget['value']).isdigit():
        return None
    arg = str(widget['commands'][0]).replace('-', '')
    repeated_args = arg * int(widget['value'])
    return '-' + repeated_args


def Dropdown(widget):
    if widget['value'] == 'Select Option':
        return None
    elif widget['commands'] and widget['value']:
        return u'{} {}'.format(widget['commands'][0], quote(widget['value']))
    else:
        return quote(widget['value']) if widget['value'] else ''


def General(widget):
    if widget['commands'] and widget['value']:
        if not widget['data']['nargs']:
            v = quote(widget['value'])
        else:
            v = widget['value']
        return u'{0} {1}'.format(widget['commands'][0], v)
    else:
        if not widget['value']:
            return None
        elif not widget['data']['nargs']:
            return quote(widget['value'])
        else:
            return widget['value']



