# -*- coding: utf-8 -*-
import os
import tempfile
import webbrowser

import click
import logging

from path import path

from . import (base, family_file, family_type, version, root, phenomizer)

from puzzle.plugins import SqlStore, VcfPlugin
try:
    from puzzle.plugins import GeminiPlugin
    GEMINI = True
except ImportError:
    GEMINI = False

from sqlite3 import DatabaseError

from puzzle.server import create_app
from puzzle.server.settings import BaseConfig
from puzzle.utils import (get_file_type, get_variant_type, get_cases)

logger = logging.getLogger(__name__)


@base.command()
@click.argument('variant-source', type=click.Path(exists=True), required=False)
@click.option('--host', default='0.0.0.0', show_default=True)
@click.option('--port', default=5000, show_default=True)
@click.option('--debug', is_flag=True)
@click.option('-p', '--pattern', default='*', show_default=True)
@click.option('--no-browser', is_flag=True, help='Prevent auto-opening browser')
@phenomizer
@family_file
@family_type
@version
@root
@click.pass_context
def view(ctx, host, port, debug, pattern, family_file, family_type,
         variant_source, root, no_browser, phenomizer):
    """Visualize DNA variant resources.

    1. Look for variant source(s) to visualize and inst. the right plugin
    """
    main_loop = (not debug) or (os.environ.get('WERKZEUG_RUN_MAIN') == 'true')
    root = root or ctx.obj.get('root') or os.path.expanduser("~/.puzzle")
    phenomizer_auth = phenomizer or ctx.obj.get('phenomizer_auth')
    BaseConfig.PHENOMIZER_AUTH = True if ctx.obj.get('phenomizer_auth') else False
    BaseConfig.STORE_ENABLED = True

    if variant_source is None:
        logger.info("Root directory is: {}".format(root))

        db_path = os.path.join(root, 'puzzle_db.sqlite3')
        logger.info("db path is: {}".format(db_path))
        if not os.path.exists(db_path):
            logger.warn("database not initialized, run 'puzzle init'")
            ctx.abort()

        if os.path.isfile(root):
            logger.error("'root' can't be a file")
            ctx.abort()

        store = SqlStore(db_path, phenomizer_auth=phenomizer_auth)
        for case_obj in store.cases():
            if case_obj.variant_mode == 'gemini':
                if not GEMINI:
                    logger.error("Need to have gemini instaled to view gemini database")
                    ctx.abort()

    else:
        logger.info("Using in memory database")
        tmpdir = tempfile.mkdtemp()
        tmpdb = os.path.join(tmpdir, 'puzzle.sqlite3')
        logger.info("building database: {}".format(tmpdb))
        store = SqlStore("sqlite:///{}".format(tmpdb),
                         phenomizer_auth=phenomizer_auth)
        if main_loop:
            store.set_up()
            cases = []
            if os.path.isfile(variant_source):
                file_type = get_file_type(variant_source)
                #Test if gemini is installed
                if file_type == 'unknown':
                    logger.error("File has to be vcf or gemini db")
                    ctx.abort()
                elif file_type == 'gemini':
                    #Check if gemini is installed
                    if not GEMINI:
                        logger.error("Need to have gemini installed to use gemini plugin")
                        ctx.abort()
                variant_type = get_variant_type(variant_source)
                cases = get_cases(
                    variant_source=variant_source,
                    case_lines=family_file,
                    case_type=family_type,
                    variant_type=variant_type,
                    variant_mode=file_type
                )
            else:
                for file in path(variant_source).walkfiles(pattern):
                    file_type = get_file_type(file)
                    if file_type != 'unknown':
                        variant_type = get_variant_type(file)
                        #Test if gemini is installed
                        if file_type == 'gemini':
                            if not GEMINI:
                                logger.error("Need to have gemini installed to use gemini plugin")
                                ctx.abort()

                        for case in get_cases(
                            variant_source=file,
                            case_type=family_type,
                            variant_type=variant_type,
                            variant_mode=file_type):

                            cases.append(case)

            for case_obj in cases:
                if store.case(case_obj.case_id) is not None:
                    logger.warn("{} already exists in the database"
                                .format(case_obj.case_id))
                    continue

                # extract case information
                logger.debug("adding case: {}".format(case_obj.case_id))
                store.add_case(case_obj, vtype=case_obj.variant_type, mode=case_obj.variant_mode)

    logger.debug("Plugin setup was succesfull")
    BaseConfig.PUZZLE_BACKEND = store
    BaseConfig.UPLOAD_DIR = os.path.join(root, 'resources')

    app = create_app(config_obj=BaseConfig)

    if no_browser is False:
        webbrowser.open_new_tab("http://{}:{}".format(host, port))

    app.run(host=host, port=port, debug=debug)
