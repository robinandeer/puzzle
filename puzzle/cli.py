# -*- coding: utf-8 -*-
import sys
import logging

import click

import puzzle
from .factory import create_app
from .log import configure_stream, LEVELS
from .plugins import VcfPlugin
from .settings import BaseConfig

logger = logging.getLogger(__name__)


@click.group()
@click.option('-t', '--plugin', type=click.Choice(['vcf']), default='vcf')
@click.option('-v', '--verbose', count=True, default=2)
<<<<<<< HEAD
@click.argument('root')
@click.pass_context
def cli(ctx, plugin, verbose, root):
    """Puzzle: manage DNA variant resources."""
=======
@click.option('-p', '--pattern')
@click.option('-t', '--type', 
    type=click.Choice(['vcf', 'gemini']),
    default='vcf'
)
@click.argument('project_root')
@click.version_option(puzzle.__version__)
def cli(host, port, debug, verbose, pattern, type, project_root):
    """Browse variant source."""
>>>>>>> Updated vcf plugin and gemini stuff
    # configure root logger to print to STDERR
    loglevel = LEVELS.get(min(verbose, 3))
    configure_stream(level=loglevel)
    
    logger.info("Running puzzle with {0} backend".format(type))
    
    if not pattern:
        if type == 'vcf':
            pattern = '*.vcf'
            logger.info("Searching for sources with pattern {0} in subdirectories"\
                " of {1}".format(pattern, project_root))
        elif type == 'gemini':
            try:
                import gemini
            except ImportError:
                logger.error("Could not import gemini")
                logger.error("Please install gemini to use gemini adapter")
                logger.info("Exiting")
                sys.exit(1)
            #When using gemini we look at one database
            pattern = project_root
            try:
                gq = gemini.GeminiQuery(pattern)
            except OperationalError as e:
                logger.error("{0} is not a valid gemini db".format(gemini_db))
                logger.info("Exiting")
                sys.exit(1)
            logger.info("Using database {0} to show variants".format(pattern))
                
            
    
    # launch the command line interface
    logger.debug('Booting up command line interface')
<<<<<<< HEAD
    ctx.root = root

    if plugin == 'vcf':
        ctx.plugin = VcfPlugin()


@cli.command()
@click.option('--host', default='0.0.0.0')
@click.option('--port', default=5000)
@click.option('--debug', is_flag=True)
@click.option('-p', '--pattern', default='*.vcf')
@click.version_option(puzzle.__version__)
@click.pass_context
def view(ctx, host, port, debug, pattern):
    """Visualize DNA variant resources."""
    BaseConfig.PUZZLE_ROOT = ctx.parent.root
    BaseConfig.PUZZLE_PATTERN = pattern
    BaseConfig.PUZZLE_BACKEND = ctx.parent.plugin
=======
    
    logger.debug("Setting PUZZLE_ROOT to {0}".format(project_root))
    BaseConfig.PUZZLE_ROOT = project_root
    logger.debug("Setting PUZZLE_PATTERN to {0}".format(pattern))
    BaseConfig.PUZZLE_PATTERN = pattern
    
>>>>>>> Updated vcf plugin and gemini stuff
    app = create_app(config_obj=BaseConfig)
    app.run(host=host, port=port, debug=debug)
