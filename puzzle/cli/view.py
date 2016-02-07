import os

import click
import logging

from . import (cli, family_file, family_type, version, verbose, root, mode,
               get_home_dir, variant_type)

from puzzle.plugins import SqlStore, VcfPlugin
try:
    from puzzle.plugins import GeminiPlugin
except ImportError:
    pass

from sqlite3 import DatabaseError

from puzzle.settings import BaseConfig
from puzzle.factory import create_app

logger = logging.getLogger(__name__)

@cli.command()
@click.argument('variant-source', 
    type=click.Path(exists=True),
    required=False
)
@click.option('--host',
    default='0.0.0.0',
    show_default=True,
)
@click.option('--port',
    default=5000,
    show_default=True,
)
@click.option('--debug',
    is_flag=True
)
@click.option('-p', '--pattern',
    default='*.vcf',
    show_default=True,
)
@family_file
@family_type
@version
@root
@mode
@variant_type
@click.pass_context
def view(ctx, host, port, debug, pattern, family_file, family_type,
         variant_source, variant_type, root, mode):
    """Visualize DNA variant resources.

    1. Look for variant source(s) to visualize and inst. the right plugin
    2.
    """

    root = root or ctx.obj['root']

    if root is None:
        root = get_home_dir()

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

        plugin = SqlStore(db_path)
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

    app = create_app(config_obj=BaseConfig)

    app.run(host=host, port=port, debug=debug)
