# -*- coding: utf-8 -*-
import os
import logging

import yaml
import click

from puzzle.log import configure_stream, LEVELS
from puzzle.constants import PUZZLE_CONFIG_PATH

from . import (root, version, verbose)


logger = logging.getLogger(__name__)


@click.group()
@version
@verbose
@click.option('-c', '--config',
    type=click.Path(),
    default=PUZZLE_CONFIG_PATH
)
@click.pass_context
def base(ctx, verbose, config):
    """Puzzle: manage DNA variant resources."""
    # configure root logger to print to STDERR
    loglevel = LEVELS.get(min(verbose, 3))
    configure_stream(level=loglevel)
    ctx.obj = {}
    if config and os.path.exists(config):
        ctx.obj = yaml.load(open(config, 'r')) or {}
        ctx.obj['config_path'] = config
    # launch the command line interface
    logger.debug('Booting up command line interface')
