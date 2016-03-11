import os

import logging
import click

from . import (base, root, family_file, family_type)

from puzzle.plugins import SqlStore

try:
    from puzzle.plugins import GeminiPlugin
    GEMINI = True
except ImportError:
    GEMINI=False

from puzzle.utils import (get_file_type, get_variant_type, get_cases)

from sqlite3 import DatabaseError

logger = logging.getLogger(__name__)

@base.command()
@click.argument('variant-source',
    type=click.Path(exists=True),
)
@family_file
@family_type
@root
@click.pass_context
def load(ctx, variant_source, family_file, family_type, root):
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


    if not os.path.isfile(variant_source):
        logger.error("Variant source has to be a file")
        ctx.abort()
    
    mode = get_file_type(variant_source)
    if mode == 'unknown':
        logger.error("Unknown file type")
        ctx.abort()
    #Test if gemini is installed
    elif mode == 'gemini':
        logger.debug("Initialzing GEMINI plugin")
        if not GEMINI:
            logger.error("Need to have gemini installed to use gemini plugin")
            ctx.abort()

    logger.debug('Set puzzle backend to {0}'.format(mode))
    
    variant_type = get_variant_type(variant_source)
    logger.debug('Set variant type to {0}'.format(variant_type))
    
    cases = get_cases(
        variant_source=variant_source,
        case_lines=family_file, 
        case_type=family_type, 
        variant_type=variant_type, 
        variant_mode=mode
    )
    
    if len(cases) == 0:
        logger.warning("No cases found")
        ctx.abort()

    logger.info("Initializing sqlite plugin")
    store = SqlStore(db_path)

    for case_obj in cases:
        if store.case(case_obj.case_id) is not None:
            logger.warn("{} already exists in the database"
                        .format(case_obj.case_id))
            continue
        # extract case information
        logger.debug("adding case: {} to puzzle db".format(case_obj.case_id))
        store.add_case(case_obj, vtype=variant_type, mode=mode)
