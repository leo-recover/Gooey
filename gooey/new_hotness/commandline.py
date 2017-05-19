from itertools import chain


def buildCommandLineString():
    optionalArgs = [arg.value for arg in self.optional_args]
    requiredArgs = [c.value for c in self.required_args if c.commands]
    positionArgs = [c.value for c in self.required_args if not c.commands]
    if positionArgs:
        positionArgs.insert(0, "--")
    cmdString = ' '.join(filter(None, chain(requiredArgs, optionalArgs, positionArgs)))
    if self.layout_type == 'column':
        cmd_string = u'{} {}'.format(self.argument_groups[self.active_group].command, cmd_string)
    return u'{} --ignore-gooey {}'.format(self.build_spec['target'], cmd_string)