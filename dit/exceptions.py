# -*- coding: utf-8 -*-


class DitError(Exception):
    pass


class ArgumentError(DitError):
    pass


class NoTaskSpecifiedError(DitError):
    pass


class SubprocessError(Exception):
    pass


def maybe_raise_unrecognized_argument(argv):
    if len(argv) > 0:
        raise ArgumentError("Unrecognized argument: %s" % argv[0])
