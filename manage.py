#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask.ext.script import Manager

from puzzle.factory import create_app
from puzzle.settings import DevConfig

app = create_app(config_obj=DevConfig)
manager = Manager(app)


if __name__ == '__main__':
    manager.run()
