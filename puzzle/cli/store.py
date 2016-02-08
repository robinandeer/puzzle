import os
from os.path import expanduser

import logging
import click

from . import (base, root, family_file, family_type, variant_type, mode)

from puzzle.plugins import SqlStore, VcfPlugin
try:
    from puzzle.plugins import GeminiPlugin
except ImportError:
    pass

from sqlite3 import DatabaseError


logger = logging.getLogger(__name__)

@base.command()
@click.option('--reset', is_flag=True)
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
        root = expanduser("~/.puzzle")

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
    else:
        logger.info("Create directory: {0}".format(resource_dir))
        os.makedirs(resource_dir)
        logger.debug('Directory created')

    logger.debug('Connect to database and create tables')
    store = SqlStore(db_path)
    store.set_up(reset=reset)


@base.command()
@click.argument('variant-source',
    type=click.Path(exists=True),
)
@family_file
@family_type
@root
@mode
@variant_type
@click.pass_context
def load(ctx, variant_source, family_file, family_type, root, mode,
        variant_type):
    """
    Load a case into the database.

    This can be done with a config file or from command line.
    If no database was found run puzzle init first.
    """
    if root is None:
        root = expanduser("~")

    if os.path.isfile(root):
        logger.error("'root' can't be a file")
        ctx.abort()

    logger.info("Root directory is: {}".format(root))

    db_path = os.path.join(root, 'puzzle_db.sqlite3')
    logger.info("db path is: {}".format(db_path))

    if not os.path.exists(db_path):
        logger.warn("database not initialized, run 'puzzle init'")
        ctx.abort()

    logger.debug('Set puzzle backend to {0}'.format(mode))

    logger.debug('Set variant type to {0}'.format(variant_type))

    if mode == 'vcf':
        logger.info("Initialzing VCF plugin")

        try:
            plugin = VcfPlugin(
                root_path=variant_source,
                case_lines=family_file,
                case_type=family_type,
                vtype=variant_type
            )
        except SyntaxError as e:
            logger.error(e.message)
            ctx.abort()

    elif mode == 'gemini':
        logger.debug("Initialzing GEMINI plugin")
        try:
            plugin = GeminiPlugin(db=variant_source, vtype=variant_type)
        except NameError:
            logger.error("Need to have gemini installed to use gemini plugin")
            ctx.abort()
        except DatabaseError as e:
            logger.error("{0} is not a valid gemini db".format(variant_source))
            logger.info("variant-source has to point to a gemini database")
            ctx.abort()

    logger.debug("Plugin setup was succesfull")
    # from gemini can create multiple cases
    store = SqlStore(db_path)

    for case_obj in plugin.cases():
        if store.case(case_id=case_obj.case_id).case_id == case_obj.case_id:
            logger.warn("{} already exists in the database"
                        .format(case_obj.case_id))
            continue

        # extract case information
        logger.debug("adding case: {}".format(case_obj.case_id))
        store.add_case(case_obj, vtype=variant_type, mode=mode)

@base.command()
@click.option('-f', '--family_id',
    type=str,
)
@click.option('-i', '--individual_id',
    type=str,
)
@root
@click.pass_context
def delete(ctx, family_id, individual_id, root):
    """
    Delete a case or individual from the database.

    If no database was found run puzzle init first.
    """
    if root is None:
        root = expanduser("~")

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
        if case_obj.case_id != family_id:
            logger.warning("Family {0} does not exist in database".format(family_id))
            ctx.abort()
        store.delete_case(case_obj)
    elif individual_id:
        ind_obj = store.individual(ind_id=individual_id)
        if ind_obj.ind_id != individual_id:
            logger.warning("Individual {0} does not exist in database".format(individual_id))
            ctx.abort()
        store.delete_individual(ind_obj)


@base.command()
@root
@click.pass_context
def cases(ctx, root):
    """
    Show all cases in the database.

    If no database was found run puzzle init first.
    """
    if root is None:
        root = expanduser("~")

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
        print(case)

@base.command()
@root
@click.pass_context
def individuals(ctx, root):
    """
    Show all individuals in the database.

    If no database was found run puzzle init first.
    """
    if root is None:
        root = expanduser("~")

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
    for ind in store.get_individuals():
        print(ind)
