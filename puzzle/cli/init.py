import codecs
import os

import logging
import click
import yaml

from . import (base, root, phenomizer)

from puzzle.plugins import SqlStore
from puzzle.constants import PUZZLE_CONFIG_PATH

logger = logging.getLogger(__name__)

@base.command()
@click.option('--reset', 
    is_flag=True,
    help="Wipe the database and initialize a new one"
)
@root
@phenomizer
@click.pass_context
def init(ctx, reset, root, phenomizer):
    """Initialize a database that store metadata

        Check if "root" dir exists, otherwise create the directory and
        build the database. If a database already exists, do nothing.

    """
    configs = {}
    if root is None:
        root = ctx.obj.get('root') or os.path.expanduser("~/.puzzle")
    configs['root'] = root
    
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
    
    if phenomizer:
        phenomizer = [str(term) for term in phenomizer]
        configs['phenomizer_auth'] = phenomizer
    
    if not ctx.obj.get('config_path'):
        logger.info("Creating puzzle config file in {0}".format(PUZZLE_CONFIG_PATH))
        with codecs.open(PUZZLE_CONFIG_PATH, 'w', encoding='utf-8') as f:
            f.write(yaml.dump(configs))
        logger.debug("Config created")
            

