# -*- coding: utf-8 -*-
import logging

from flask import Flask

from .ext import bootstrap, markdown
from .settings import BaseConfig

logger = logging.getLogger(__name__)


def create_app(config=None, config_obj=None):
    """Flask app factory function.

    Args:
        config (Optional[path]): path to a Python module config file
        config_obj (Optional[class]): Python config object
    """
    app = Flask(__name__)
    # configure application from external configs
    configure_app(app, config=config, config_obj=config_obj)
    # register different parts of the application
    register_blueprints(app)
    # setup extensions
    bind_extensions(app)
    return app


def configure_app(app, config=None, config_obj=None):
    """Configure application instance.

    Args:
        app (Flask): initialized Flask app instance
        config (Optional[path]): path to a Python module config file
        config_obj (Optional[class]): Python config object
    """
    app.config.from_object(config_obj or BaseConfig)
    if config is not None:
        app.config.from_pyfile(config)


def register_blueprints(app):
    """Configure blueprints.

    Args:
        app (Flask): initialized Flask app instance
    """
    for blueprint in app.config.get('BLUEPRINTS', []):
        app.register_blueprint(blueprint)


def bind_extensions(app):
    """Configure extensions.

    Args:
        app (Flask): initialized Flask app instance
    """
    # bind plugin to app object
    app.db = app.config['PUZZLE_BACKEND']
    app.db.init_app(app)

    # bind bootstrap blueprints
    bootstrap.init_app(app)
    markdown(app)

    @app.template_filter('islist')
    def islist(object):
        return isinstance(object, (tuple, list))
