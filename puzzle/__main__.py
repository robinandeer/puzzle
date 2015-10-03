#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
puzzle.__main__
~~~~~~~~~~~~~~~~~~~~~

The main entry point for the command line interface.

Invoke as ``puzzle`` (if installed)
or ``python -m puzzle`` (no install required).
"""
import logging
import sys

import click

import puzzle
from .factory import create_app
from .log import configure_stream, LEVELS
from .settings import BaseConfig

logger = logging.getLogger(__name__)


@click.command()
@click.option('--host', default='0.0.0.0')
@click.option('--port', default=5000)
@click.option('-v', '--verbose', count=True, default=2)
@click.option('-p', '--pattern', default='*.vcf')
@click.argument('vcf_root')
@click.version_option(puzzle.__version__)
def cli(host, port, verbose, pattern, vcf_root):
    """Browse VCF files."""
    # configure root logger to print to STDERR
    loglevel = LEVELS.get(min(verbose, 3))
    configure_stream(level=loglevel)

    # launch the command line interface
    logger.debug('Booting up command line interface')

    BaseConfig.PUZZLE_ROOT = vcf_root
    BaseConfig.PUZZLE_PATTERN = pattern
    app = create_app(config_obj=BaseConfig)
    app.run(host=host, port=port)


if __name__ == '__main__':
    # exit using whatever exit code the CLI returned
    sys.exit(cli())
