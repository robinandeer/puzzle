# -*- coding: utf-8 -*-
import os
import logging

import click

from codecs import open
from puzzle.log import configure_stream, LEVELS

from puzzle.settings import BaseConfig
from puzzle.plugins import SqlStore, VcfPlugin

from . import (root, verbose)

logger = logging.getLogger(__name__)


@click.group()
@root
@verbose
@click.pass_context
def cli(ctx, verbose, root):
    """Puzzle: manage DNA variant resources."""
    # configure root logger to print to STDERR
    loglevel = LEVELS.get(min(verbose, 3))
    configure_stream(level=loglevel)

    # launch the command line interface
    logger.debug('Booting up command line interface')
    
    if root:
        if os.path.isfile(root):
            logger.error("'root' can't be a file")
            ctx.abort()

    ctx.obj = {
        'root': root,
    }

