#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
puzzle.__main__
~~~~~~~~~~~~~~~~~~~~~

The main entry point for the command line interface.

Invoke as ``puzzle`` (if installed)
or ``python -m puzzle`` (no install required).
"""
import sys

from puzzle.cli import base as cli


if __name__ == '__main__':
    # exit using whatever exit code the CLI returned
    sys.exit(cli())
