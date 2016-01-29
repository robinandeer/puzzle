# -*- coding: utf-8 -*-
import os
import logging

import click

from codecs import open
import puzzle
from .factory import create_app
from .log import configure_stream, LEVELS
try:
    from .plugins import GeminiPlugin
except ImportError:
    pass

from sqlite3 import DatabaseError
from .settings import BaseConfig
from puzzle.plugins import SqlStore, VcfPlugin

logger = logging.getLogger(__name__)


@click.group()
@click.option('-m', '--mode',
    type=click.Choice(['vcf', 'gemini']),
    default='vcf'
)
@click.option('-t', '--variant-type',
    type=click.Choice(['snv', 'sv']),
    default='snv',
    help="If Structural Variantion or Single Nucleotide variant mode should"\
         " be used"
)
@click.option('-v', '--verbose',
    count=True,
    default=2
)
@click.option('--root', '-r',
    type=click.Path(),
    help="Path to where to find variant source(s)"
)
@click.pass_context
def cli(ctx, verbose, mode, variant_type, root):
    """Puzzle: manage DNA variant resources."""
    # configure root logger to print to STDERR
    loglevel = LEVELS.get(min(verbose, 3))
    configure_stream(level=loglevel)

    # launch the command line interface
    logger.debug('Booting up command line interface')

    if root is None:
        root = os.path.join(os.environ['HOME'], '.puzzle')

    if os.path.isfile(root):
        logger.error("'root' can't be a file")
        ctx.abort()

    logger.info("Root directory is: {}".format(root))
    ctx.obj = {
        'root': root,
        'db_path': os.path.join(root, 'puzzle_db.sqlite3'),
        'mode': mode,
        'variant_type': variant_type
    }


@cli.command()
@click.option('--reset', is_flag=True)
@click.version_option(puzzle.__version__)
@click.pass_context
def init(ctx, reset):
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
    puzzle_dir = ctx.obj['root']
    if os.path.exists(puzzle_dir):
        logger.debug("Found puzzle directory: {0}".format(puzzle_dir))
    else:
        logger.info("Create directory: {0}".format(puzzle_dir))
        os.makedirs(puzzle_dir)
        logger.debug('Directory created')

    logger.debug('Connect to database and create tables')
    store = SqlStore(ctx.obj['db_path'])
    store.set_up(reset=reset)


@cli.command()
@click.option('-i', '--variant-source', type=click.Path(exists=True),
              required=True)
@click.option('-f', '--family_file', type=click.File('r'))
@click.option('-t' ,'--family_type',
                type=click.Choice(['ped', 'alt']),
                default='ped',
                help='If the analysis use one of the known setups, please specify which one.'
)
@click.option('-i', '--variant-source',
    type=click.Path(exists=True),
    required=True
)
@click.version_option(puzzle.__version__)
@click.pass_context
def load(ctx, variant_source, family_file, family_type):
    """
    Load a case into the database.

    This can be done with a config file or from command line.
    If no database was found run puzzle init first.
    """
    db_path = ctx.obj['db_path']
    if not os.path.exists(db_path):
        logger.warn("database not initialized, run 'puzzle init'")
        ctx.abort()

    logger.debug('Set puzzle backend to {0}'.format(ctx.obj['mode']))
    mode = ctx.obj['mode']
    logger.debug('Set puzzle mode to {0}'.format(ctx.obj['variant_type']))
    variant_type = ctx.obj['variant_type']

    if mode == 'vcf':
        logger.info("Initialzing VCF plugin")
        if not family_file:
            logger.error("Please provide a ped like file")
            ctx.abort()
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
        # extract case information
        logger.debug("adding case: {}".format(case_obj['case_id']))
        store.add_case(case_obj, vtype=variant_type, mode=mode)

@cli.command()
@click.option('-f', '--family_id',
    type=str,
)
@click.option('-i', '--individual_id',
    type=str,
)
@click.version_option(puzzle.__version__)
@click.pass_context
def delete(ctx, family_id, individual_id):
    """
    Delete a case or individual from the database.

    If no database was found run puzzle init first.
    """
    db_path = ctx.obj['db_path']
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


@cli.command()
@click.version_option(puzzle.__version__)
@click.pass_context
def cases(ctx):
    """
    Show all cases in the database.

    If no database was found run puzzle init first.
    """
    db_path = ctx.obj['db_path']
    if not os.path.exists(db_path):
        logger.warn("database not initialized, run 'puzzle init'")
        ctx.abort()

    store = SqlStore(db_path)
    for case in store.cases():
        print(case)

@cli.command()
@click.version_option(puzzle.__version__)
@click.pass_context
def individuals(ctx):
    """
    Show all individuals in the database.

    If no database was found run puzzle init first.
    """
    db_path = ctx.obj['db_path']
    if not os.path.exists(db_path):
        logger.warn("database not initialized, run 'puzzle init'")
        ctx.abort()

    store = SqlStore(db_path)
    for ind in store.individuals():
        print(ind)


@cli.command()
@click.option('--host',
    default='0.0.0.0'
)
@click.option('--port',
    default=5000
)
@click.option('--debug',
    is_flag=True
)
@click.option('-p', '--pattern',
    default='*.vcf'
)
@click.option('-f', '--family_file',
    type=click.File('r')
)
@click.option('-t' ,'--family_type',
                type=click.Choice(['ped', 'alt']),
                default='ped',
                help='If the analysis use one of the known setups, please specify which one.'
)
@click.option('-i', '--variant-source', type=click.Path(exists=True))
@click.version_option(puzzle.__version__)
@click.pass_context
def view(ctx, host, port, debug, pattern, family_file, family_type,
         variant_source):
    """Visualize DNA variant resources.

    1. Look for variant source(s) to visualize and inst. the right plugin
    2.
    """
    logger.debug('Set puzzle backend to {0}'.format(ctx.obj['mode']))
    mode = ctx.obj['mode']
    logger.debug('Set puzzle mode to {0}'.format(ctx.obj['variant_type']))
    variant_type = ctx.obj['variant_type']

    if variant_source is None:
        if not os.path.exists(ctx.obj['db_path']):
            logger.warn("database not initialized, run 'puzzle init'")
            ctx.abort()

        plugin = SqlStore(ctx.obj['db_path'])

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
