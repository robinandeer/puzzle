# -*- coding: utf-8 -*-
import os.path
from .blueprints import public_bp, variants_bp

PROJECT_NAME = __name__.split('.')[0]


class BaseConfig:
    PROJECT = PROJECT_NAME
    DEBUG = False
    TESTING = False

    # http://flask.pocoo.org/docs/quickstart/#sessions
    SECRET_KEY = 'secret key'

    # default blueprints
    BLUEPRINTS = [public_bp, variants_bp]

    PUZZLE_ROOT = os.path.abspath('tests/fixtures')


class DevConfig(BaseConfig):
    DEBUG = True


class TestConfig(DevConfig):
    TESTING = True
