# -*- coding: utf-8 -*-
from flask import Flask

from .ext import db
from .settings import BaseConfig


def create_app(config=None, config_obj=None):
    """Flask app factory function."""
    app = Flask(__name__)
    configure_app(app, config=config, config_obj=config_obj)
    register_blueprints(app)
    bind_extensions(app)
    return app


def configure_app(app, config=None, config_obj=None):
    """Configure application instance."""
    app.config.from_object(config_obj or BaseConfig)
    if config is not None:
        app.config.from_pyfile(config)


def register_blueprints(app):
    """Configure blueprints."""
    for blueprint in app.config.get('BLUEPRINTS', []):
        app.register_blueprint(blueprint)


def bind_extensions(app):
    """Configure extensions."""
    db.init_app(app)
