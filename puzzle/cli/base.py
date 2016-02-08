# -*- coding: utf-8 -*-
import logging

import click

from puzzle.log import configure_stream, LEVELS

from . import (root, version, verbose)

logger = logging.getLogger(__name__)


@click.group()
@version
@verbose
@click.pass_context
def base(ctx, verbose):
    """Puzzle: manage DNA variant resources."""
    # configure root logger to print to STDERR
    loglevel = LEVELS.get(min(verbose, 3))
    configure_stream(level=loglevel)

    # launch the command line interface
    logger.debug('Booting up command line interface')
    
    ctx.obj = {}

