# -*- coding: utf-8 -*-

from sys import stderr, stdout

_verbose = False

_warning_str = ('\033[0;101;37mWARNIG:\033[0m' if stderr.isatty()
                else "WARNING:")

_error_str = ('\033[0;41;37mERROR:\033[0m' if stderr.isatty()
              else "ERROR:")


def _flush_stdout():
    # This is needed before using stderr, since it is never buffered
    if not stdout.isatty():
        stdout.flush()


def turn_verbose_on():
    global _verbose
    _verbose = True


def normal(message=''):
    print(message)


def verbose(message=''):
    if _verbose:
        print(message)


def yn_question(question):
    return input("%s [Y/n] " % question) == "Y"


def warning(message):
    _flush_stdout()
    stderr.write("%s %s\n" % (_warning_str, message))


def error(message):
    _flush_stdout()
    stderr.write("%s %s\n" % (_error_str, message))


