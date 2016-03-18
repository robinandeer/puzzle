# -*- coding: utf-8 -*-
from flask_bootstrap import Bootstrap
from flask.ext.markdown import Markdown

bootstrap = Bootstrap()
markdown = lambda app: Markdown(app)
