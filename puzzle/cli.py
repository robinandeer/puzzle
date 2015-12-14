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
from .plugins import VcfPlugin
try:
    from .plugins import GeminiPlugin
except ImportError:
    pass

from sqlite3 import OperationalError
from .settings import BaseConfig
from puzzle import resource_package
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
@click.option('-f', '--family_file',
    type=click.File('r')
)
@click.option('-t' ,'--family_type', 
                type=click.Choice(['ped', 'alt']), 
                default='ped',
                help='If the analysis use one of the known setups, please specify which one.'
)
@click.option('-b', '--bam_path',
    nargs=2,
    multiple=True,
    # type=click.Tuple([str, str]),
    help="Provide a sample name and path to bam file"
)
@click.option('--root', '-r',
    type=click.Path(exists=True),
    help="Path to where to find variant source(s)"
)
@click.pass_context
def cli(ctx, plugin, verbose, root, family_file, family_type, mode, bam_path):
    """Puzzle: manage DNA variant resources."""
    # configure root logger to print to STDERR
    loglevel = LEVELS.get(min(verbose, 3))
    configure_stream(level=loglevel)
    
    # launch the command line interface
    logger.debug('Booting up command line interface')
    ctx.root = root

    ctx.mode = mode
    ctx.family_file = family_file
    ctx.family_type = family_type
    valid_vcf_suffixes = ('.vcf', '.vcf.gz')
    ctx.bam_paths = bam_path
    ctx.type = plugin
    if plugin == 'vcf':
        #If root is a file we need to check that it has the correct ending
        if os.path.isfile(root):
            if not root.endswith(valid_vcf_suffixes):
                logger.error("Vcf file has to end with with .vcf or .vcf.gz")
                logger.info("Please check vcf file {0} or use other"\
                            " plugin".format(root))
                logger.info("Exiting")
                sys.exit(1)
        if family_file:
            # If family file we only allow one vcf file as input
            if not os.path.isfile(root):
                logger.error("root has to be a vcf file when running with family file")
                logger.info("Exiting")
                sys.exit(1)
        logger.info("Initialzing VCF plugin")
        ctx.plugin = VcfPlugin()
        
            
    elif plugin == 'gemini':
        try:
            #First check if gemini is properly installed:
            from gemini import GeminiQuery
            #Then check if we are looking at a proper database
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

@cli.command()
@click.option("--db_location", 
    envvar='HOME',
    help="Path to where database should be located. Default is $HOME"
)
@click.version_option(puzzle.__version__)
@click.pass_context
def init(ctx, db_location):
    """Initialize a database that store metadata
        
        Builds the database at --db_location. If a database already exists, 
        do nothing.
        
        The behaviour will be different with different plugins. A config file
        in YAML format will be created in puzzle/configs with information about
        the database.
        
        VCF:
            A sqlite database will be built in the home directory of the user
        GEMINI:
            A sqlite database will be built in the home directory of the user
    """
    plugin_type = ctx.parent.type
    logger.info("Plugin type: {0}".format(plugin_type))
    if plugin_type in ['vcf', 'gemini']:
        db_location = str(os.path.join(db_location, '.puzzle.db'))
        logger.info("Path to database: {0}".format(db_location))
        config_path = os.path.join('configs', 'sqlite_config.ini')
        config_file = os.path.join(resource_package, config_path)
        
        if not os.path.exists(db_location):
            logger.info("Creating database")
            db = dataset.connect("sqlite:///{0}".format(db_location))
            logger.info("Database created")
            ##TODO add username, password etc
            configs = {
                'dialect': 'sqlite',
                'location': db_location,
            }

            stream = open(config_file, 'w')
            logger.info("Write config file for database to {0}".format(
                config_file))
            yaml.dump(configs, stream)
            logger.debug("Config written")
        else:
            logger.warning("Database already exists!")
    
@cli.command()
@click.option('-c', '--puzzle_config',
    type=click.Path(exists=True),
    help="Path to puzzle database config. If not used puzzle will check"\
         "puzzle/configs for a file"
)
@click.option('--case_config',
    type=click.Path(exists=True),
    help="Path to a case config"
)
@click.version_option(puzzle.__version__)
@click.pass_context
def load(ctx, puzzle_config, case_config):
    """Load a case into the database.  
    
        This can be done with a config file or from command line.
        If no database was found run puzzle init first.
    """
    if not puzzle_config:
        config_path = os.path.join('configs', 'sqlite_config.ini')
        puzzle_config = os.path.join(resource_package, config_path)
    
    if not os.path.exists(puzzle_config):
        logger.error("Puzzle config {0} does not seem to exist!".format(
            puzzle_config))
        logger.info("Please run puzzle init before loading case")
        sys.exit(1)
    
    logger.info("Read database configs from {0}".format(puzzle_config))
    db_configs = yaml.load(open(puzzle_config, 'r'))
    
    print(db_configs)
    pass

@cli.command()
@click.option('--host', default='0.0.0.0')
@click.option('--port', default=5000)
@click.option('--debug', is_flag=True)
@click.option('-p', '--pattern', default='*.vcf')
@click.version_option(puzzle.__version__)
@click.pass_context
def view(ctx, host, port, debug, pattern):
    """Visualize DNA variant resources."""
    logger.info('Set puzzle root to {0}'.format(ctx.parent.root))
    BaseConfig.PUZZLE_ROOT = ctx.parent.root
    logger.debug('Set puzzle pattern to {0}'.format(pattern))
    BaseConfig.PUZZLE_PATTERN = pattern
    logger.debug('Set puzzle backend to {0}'.format(ctx.parent.plugin))
    BaseConfig.PUZZLE_BACKEND = ctx.parent.plugin
    logger.debug('Set puzzle mode to {0}'.format(ctx.parent.mode))
    BaseConfig.PUZZLE_MODE = ctx.parent.mode
    
    if ctx.parent.family_file:
        BaseConfig.FAMILY_FILE = ctx.parent.family_file
        BaseConfig.FAMILY_TYPE = ctx.parent.family_type

    app = create_app(config_obj=BaseConfig)

    app.run(host=host, port=port, debug=debug)
