# -*- coding: utf-8 -*-
"""
puzzle
~~~~~~~~~~~~~~~~~~~

A new secret project :P

:copyright: (c) 2015 by Robin Andeer
:licence: MIT, see LICENCE for more details
"""
from __future__ import absolute_import, unicode_literals
import logging

# Generate your own AsciiArt at:
# patorjk.com/software/taag/#f=Calvin%20S&t=Puzzle
__banner__ = r"""
╦  ╦┌─┐┌┐┌┌─┐┬ ┬┌─┐┬─┐┌┬┐
╚╗╔╝├─┤││││ ┬│ │├─┤├┬┘ ││  by Robin Andeer
 ╚╝ ┴ ┴┘└┘└─┘└─┘┴ ┴┴└──┴┘
"""

__title__ = 'puzzle'
__summary__ = 'A new secret project :P'
__uri__ = 'https://github.com/robinandeer/puzzle'

__version__ = '0.0.1'

__author__ = 'Robin Andeer'
__email__ = 'robin.andeer@gmail.com'

__license__ = 'MIT'
__copyright__ = 'Copyright 2015 Robin Andeer'

# the user should dictate what happens when a logging event occurs
logging.getLogger(__name__).addHandler(logging.NullHandler())
