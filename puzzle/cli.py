# -*- coding: utf-8 -*-
import sys
import os
import logging
import yaml

import click

from codecs import open

import puzzle
from .factory import create_app
from .log import configure_stream, LEVELS
try:
    from .plugins import GeminiPlugin
except ImportError:
    pass

from sqlite3 import OperationalError
from .settings import BaseConfig
from puzzle import resource_package
from puzzle.plugins import SqlStore, VcfPlugin
from .utils import init_db

logger = logging.getLogger(__name__)


@click.group()
@click.option('-p', '--plugin',
    type=click.Choice(['vcf', 'gemini']),
    default='vcf'
)
@click.option('-m', '--mode',
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
    type=click.Path(exists=True),
    help="Path to where to find variant source(s)"
)
@click.pass_context
def cli(ctx, plugin, verbose, mode, root):
    """Puzzle: manage DNA variant resources."""
    # configure root logger to print to STDERR
    loglevel = LEVELS.get(min(verbose, 3))
    configure_stream(level=loglevel)

    # launch the command line interface
    logger.debug('Booting up command line interface')
    db_path = ""
    if root is None:
        root = os.path.join(os.environ['HOME'], '.puzzle')
        db_path = os.path.join(root, 'puzzle_db.sqlite3')
        if not os.path.exists(db_path):
            logger.error("Please set up a database with puzzle init or point"\
                          " to file(s) with '--root'")
        ctx.abort()
    logger.info("Root directory is: {}".format(root))
    ctx.root = root
    # ctx.obj['db_path'] = db_path

    ctx.mode = mode
    ctx.type = plugin


@cli.command()
@click.version_option(puzzle.__version__)
@click.pass_context
def init(ctx):
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
    puzzle_dir = ctx.parent.root
    if os.path.exists(puzzle_dir):
        logger.debug("Found puzzle directory: {0}".format(puzzle_dir))
    else:
        logger.info("Creating directory {0}".format(puzzle_dir))
        os.makedirs(puzzle_dir)
        logger.debug("Directory {0} created".format(puzzle_dir))

    logger.debug('Connecting to database and creating tables')
    store = SqlStore(ctx.obj['db_path'])
    store.set_up()



@cli.command()
@click.option('-i', '--variant-source', type=click.Path(exists=True),
              required=True)
@click.option('-f', '--family_file', type=click.File('r'))
@click.version_option(puzzle.__version__)
@click.pass_context
def load(ctx, variant_source, family_file):
    """Load a case into the database.

        This can be done with a config file or from command line.
        If no database was found run puzzle init first.
    """
    db_path = ctx.obj['db_path']
    if not os.path.exists(db_path):
        logger.warn("database not initialized, run 'puzzle init'")
        ctx.abort()

    # TODO: initialize the correct adapter
    # from gemini can create multiple cases
    store = SqlStore(db_path)
    if ctx.parent.mode == 'vcf' and family_file is None:
        logger.error("Please provide a family file")
        ctx.abort()

    # extract case information

    ctx.parent.plugin.load_case(
        case_lines=case_lines,
        variant_source=variant_source,
        case_type=ctx.parent.family_type,
        bam_paths=ctx.parent.bam_paths,
    )


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
@click.option('--database', type=str)
@click.version_option(puzzle.__version__)
@click.pass_context
def view(ctx, host, port, debug, pattern, family_file, family_type, 
database):
    """Visualize DNA variant resources.

    1. Look for variant source(s) to visualize and inst. the right plugin
    2.
    """
    logger.debug('Set puzzle backend to {0}'.format(ctx.parent.type))
    plugin = ctx.parent.type
    logger.debug('Set puzzle mode to {0}'.format(ctx.parent.mode))
    mode = ctx.parent.mode
    
    root = ctx.parent.root
    valid_vcf_suffixes = ('.vcf', '.vcf.gz')
    if plugin == 'vcf':
        #If root is a file we need to check that it has the correct ending
        if root:
            if family_file:
                # If family file we only allow one vcf file as input
                if not os.path.isfile(root):
                    logger.error("root has to be a vcf file when running with family file")
                    logger.info("Exiting")
                    sys.exit(1)

            if os.path.isfile(root):
                if not root.endswith(valid_vcf_suffixes):
                    logger.error("Vcf file has to end with with .vcf or .vcf.gz")
                    logger.info("Please check vcf file {0} or use other"\
                                " plugin".format(root))
                    logger.info("Exiting")
                    sys.exit(1)

            logger.info("Initialzing VCF plugin")
        ctx.plugin = VcfPlugin(root_path=root, case_lines=family_file, 
                                case_type=family_type, pattern=pattern, mode=mode)

    elif plugin == 'gemini':
        try:
            #First check if gemini is properly installed:
            from gemini import GeminiQuery
            #Then check if we are looking at a proper database
            if root:
                try:
                    gq = GeminiQuery(root)
                except OperationalError as e:
                    logger.error("{0} is not a valid gemini db".format(root))
                    logger.info("root has to point to a gemini databse")
                    logger.info("Exiting")
                    sys.exit(1)
            logger.info("Initialzing GEMINI plugin")
            ctx.plugin = GeminiPlugin()
        except ImportError:
            logger.error("Need to have gemini installed to use gemini plugin")
            logger.info("Exiting")
            sys.exit(1)
    
    app = create_app(config_obj=BaseConfig)

    app.run(host=host, port=port, debug=debug)
