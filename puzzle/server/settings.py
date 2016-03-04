# -*- coding: utf-8 -*-
from puzzle.plugins import VcfPlugin
from .blueprints import public_bp, variants_bp

PROJECT_NAME = __name__.split('.')[0]


class BaseConfig:
    PROJECT = PROJECT_NAME
    DEBUG = False
    TESTING = False

    # http://flask.pocoo.org/docs/quickstart/#sessions
    SECRET_KEY = 'secret key'
    PUZZLE_BACKEND = VcfPlugin()
    STORE_ENABLED = False

    # default blueprints
    BLUEPRINTS = [public_bp, variants_bp]

    #Phemonizer credentials
    PHENOMIZER_AUTH = False

class DevConfig(BaseConfig):
    DEBUG = True


class TestConfig(DevConfig):
    TESTING = True
