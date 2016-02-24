# -*- coding: utf-8 -*-
import os
import webbrowser

import click
import logging

from . import (base, family_file, family_type, version, root, mode, 
               variant_type, phenomizer)

from puzzle.plugins import SqlStore, VcfPlugin
try:
    from puzzle.plugins import GeminiPlugin
except ImportError:
    pass

from sqlite3 import DatabaseError

from puzzle.server import create_app
from puzzle.server.settings import BaseConfig

logger = logging.getLogger(__name__)


@base.command()
@click.argument('variant-source', type=click.Path(exists=True), required=False)
@click.option('--host', default='0.0.0.0', show_default=True)
@click.option('--port', default=5000, show_default=True)
@click.option('--debug', is_flag=True)
@click.option('-p', '--pattern', default='*.vcf', show_default=True)
@click.option('--no-browser', is_flag=True, help='Prevent auto-opening browser')
@phenomizer
@family_file
@family_type
@version
@root
@mode
@variant_type
@click.pass_context
def view(ctx, host, port, debug, pattern, family_file, family_type,
         variant_source, variant_type, root, mode, no_browser, phenomizer):
    """Visualize DNA variant resources.

    1. Look for variant source(s) to visualize and inst. the right plugin
    """
    root = root or ctx.obj.get('root') or os.path.expanduser("~/.puzzle")

    if os.path.isfile(root):
        logger.error("'root' can't be a file")
        ctx.abort()

    logger.info("Root directory is: {}".format(root))

    db_path = os.path.join(root, 'puzzle_db.sqlite3')
    logger.info("db path is: {}".format(db_path))

    if variant_source is None:
        if not os.path.exists(db_path):
            logger.warn("database not initialized, run 'puzzle init'")
            ctx.abort()
        phenomizer_auth = phenomizer or ctx.obj.get('phenomizer_auth')
        plugin = SqlStore(db_path, phenomizer_auth=phenomizer_auth)
        BaseConfig.STORE_ENABLED = True

    elif mode == 'vcf':
        logger.info("Initialzing VCF plugin")
        try:
            plugin = VcfPlugin(
                root_path=variant_source,
                case_lines=family_file,
                case_type=family_type,
                pattern=pattern,
                vtype=variant_type
            )
        except SyntaxError as e:
            logger.error(e.message)
            ctx.abort()

    elif mode == 'gemini':
        logger.info("Initialzing GEMINI plugin")
        try:
            plugin = GeminiPlugin(db=variant_source, vtype=variant_type)
        except NameError:
            logger.error("Need to have gemini installed to use gemini plugin")
            ctx.abort()
        except DatabaseError as e:
            logger.error("{0} is not a valid gemini db".format(variant_source))
            logger.info("variant-source has to point to a gemini databse")
            ctx.abort()

    logger.debug("Plugin setup was succesfull")

    BaseConfig.PUZZLE_BACKEND = plugin
    BaseConfig.UPLOAD_DIR = os.path.join(root, 'resources')

    app = create_app(config_obj=BaseConfig)

    if not (no_browser or debug):
        webbrowser.open_new_tab("http://{}:{}".format(host, port))

    app.run(host=host, port=port, debug=debug)
