import os

import logging
import click

from . import (base, root)

from puzzle.plugins import SqlStore

logger = logging.getLogger(__name__)

@base.command()
@click.option('--reset', 
    is_flag=True,
    help="Wipe the database and initialize a new one"
)
@root
@click.pass_context
def init(ctx, reset, root):
    """Initialize a database that store metadata

        Check if "root" dir exists, otherwise create the directory and
        build the database. If a database already exists, do nothing.

        The behaviour will be different with different plugins. A config file
        in YAML format will be created in puzzle/configs with information about
        the database.

        VCF:
            A sqlite database will be built in the home directory of the user
        GEMINI:
            A sqlite database will be built in the home directory of the user
    """
    if root is None:
        root = os.path.expanduser("~/.puzzle")

    if os.path.isfile(root):
        logger.error("'root' can't be a file")
        ctx.abort()

    logger.info("Root directory is: {}".format(root))

    db_path = os.path.join(root, 'puzzle_db.sqlite3')
    logger.info("db path is: {}".format(db_path))

    resource_dir = os.path.join(root, 'resources')
    logger.info("resource dir is: {}".format(resource_dir))

    if os.path.exists(resource_dir):
        logger.debug("Found puzzle directory: {0}".format(root))
        if os.path.exists(resource_dir) and not reset:
            logger.warning("Puzzle db already in place")
            ctx.abort()
    else:
        logger.info("Create directory: {0}".format(resource_dir))
        os.makedirs(resource_dir)
        logger.debug('Directory created')

    logger.debug('Connect to database and create tables')
    store = SqlStore(db_path)
    store.set_up(reset=reset)

