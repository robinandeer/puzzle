import os

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
    Load a variant source into the database.

    If no database was found run puzzle init first.
    
    1. VCF: If a vcf file is used it can be loaded with a ped file
    2. GEMINI: Ped information will be retreived from the gemini db
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
            logger.error("{} is not a valid gemini db".format(variant_source))
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
