import os

import logging
import click

from . import (base, root)

from puzzle.plugins import SqlStore

logger = logging.getLogger(__name__)


@base.command()
@root
@click.pass_context
def cases(ctx, root):
    """
    Show all cases in the database.

    If no database was found run puzzle init first.
    """
    root = root or ctx.obj.get('root') or os.path.expanduser("~/.puzzle")

    if os.path.isfile(root):
        logger.error("'root' can't be a file")
        ctx.abort()

    logger.info("Root directory is: {}".format(root))

    db_path = os.path.join(root, 'puzzle_db.sqlite3')
    logger.info("db path is: {}".format(db_path))

    if not os.path.exists(db_path):
        logger.warn("database not initialized, run 'puzzle init'")
        ctx.abort()

    store = SqlStore(db_path)
    for case in store.cases():
        click.echo(case)
