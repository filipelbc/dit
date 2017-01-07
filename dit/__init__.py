# -*- coding: utf-8 -*-

import sys


def completion():
    argv = sys.argv
    argv.pop(0)

    from dit.completion import interpret

    comp_options = interpret(argv)

    sys.stdout.write(comp_options)


def main():
    argv = sys.argv
    argv.pop(0)

    from dit.dit import interpret

    interpret(argv)
