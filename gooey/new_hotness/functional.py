from functools import reduce


def assign(*args):
    return reduce(lambda acc, x: acc.update(x) or acc, args, {})

