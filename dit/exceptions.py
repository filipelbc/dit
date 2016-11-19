

class DitException(Exception):
    pass


class ArgumentException(DitException):
    pass


class NoTaskSpecifiedCondition(DitException):
    pass


class SubprocessException(Exception):
    pass
