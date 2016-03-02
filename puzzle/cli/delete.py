import os

import logging
import click

from . import (base, root)

from puzzle.plugins import SqlStore

logger = logging.getLogger(__name__)


@base.command()
@click.option('-f', '--family_id', type=str)
@click.option('-i', '--individual_id', type=str)
@root
@click.pass_context
def delete(ctx, family_id, individual_id, root):
    """
    Delete a case or individual from the database.

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

    if family_id:
        case_obj = store.case(case_id=family_id)
        if case_obj is None:
            logger.warning("Family {0} does not exist in database"
                           .format(family_id))
            ctx.abort()
        store.delete_case(case_obj)
    elif individual_id:
        ind_obj = store.individual(ind_id=individual_id)
        if ind_obj.ind_id != individual_id:
            logger.warning("Individual {0} does not exist in database"
                           .format(individual_id))
            ctx.abort()
        store.delete_individual(ind_obj)
    else:
        logger.warning("Please provide a family or individual id")
        ctx.abort()
