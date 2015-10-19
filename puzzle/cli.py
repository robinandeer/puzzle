# -*- coding: utf-8 -*-
import sys
import logging

import click

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

logger = logging.getLogger(__name__)


@click.group()
@click.option('-p', '--plugin', type=click.Choice(['vcf', 'gemini']), default='vcf')
@click.option('-v', '--verbose', count=True, default=2)
@click.argument('root')
@click.pass_context
def cli(ctx, plugin, verbose, root):
    """Puzzle: manage DNA variant resources."""
    # configure root logger to print to STDERR
    loglevel = LEVELS.get(min(verbose, 3))
    configure_stream(level=loglevel)

    # launch the command line interface
    logger.debug('Booting up command line interface')
    ctx.root = root

    if plugin == 'vcf':
        ctx.plugin = VcfPlugin()
    elif plugin == 'gemini':
        try:
            from gemini import GeminiQuery
            ctx.plugin = GeminiPlugin()
        except ImportError:
            logger.error("Need to have gemini installed to use gemini plugin")
            logger.info("Exiting")
            sys.exit(1)
        try:
            gq = GeminiQuery(root)
        except OperationalError as e:
            logger.error("{0} is not a valid gemini db".format(root))
            logger.info("root has to point to a gemini databse")
            logger.info("Exiting")
            sys.exit(1)
            


@cli.command()
@click.option('--host', default='0.0.0.0')
@click.option('--port', default=5000)
@click.option('--debug', is_flag=True)
@click.option('-p', '--pattern', default='*.vcf')
@click.version_option(puzzle.__version__)
@click.pass_context
def view(ctx, host, port, debug, pattern):
    """Visualize DNA variant resources."""
    logger.debug('Set puzzle root to {0}'.format(ctx.parent.root))
    BaseConfig.PUZZLE_ROOT = ctx.parent.root
    logger.debug('Set puzzle pattern to {0}'.format(pattern))
    BaseConfig.PUZZLE_PATTERN = pattern
    logger.debug('Set puzzle backend to {0}'.format(ctx.parent.plugin))
    BaseConfig.PUZZLE_BACKEND = ctx.parent.plugin
    
    app = create_app(config_obj=BaseConfig)
    
    app.run(host=host, port=port, debug=debug)
