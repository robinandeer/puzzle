# -*- coding: utf-8 -*-
import logging

import dataset

from puzzle.plugins import Plugin
from . import VariantMixin, CaseMixin

logger = logging.getLogger(__name__)


class VcfPlugin(VariantMixin, CaseMixin, Plugin):
    """docstring for Plugin"""

    def __init__(self):
        super(VcfPlugin, self).__init__()
        self.individuals = None
        self.case_obj = None

    def connect(self, db_name, host='localhost', port=27017, username=None,
                password=None, dialect='sqlite'):
        """Connect to a database with cases and comments"""
        ##TODO make this more intelligent
        if dialect == 'sqlite':
            db_string = "sqlite:///{0}".format(db_name)
        ##TODO add support for more dialects
        elif dialect == 'mysql':
            db_string = "mysql://{0}:{1}@{2}/{3}".format(
                user, password, host, db_name)
            
        logger.info("Connecting to database {0}".format(db_string))
        self.puzzle_db = dataset.connect(db_string)

    def init_app(self, app):
        """Initialize plugin via Flask."""
        logger.debug("Updating root path to {0}".format(
            app.config['PUZZLE_ROOT']
        ))
        self.root_path = app.config['PUZZLE_ROOT']
        logger.debug("Updating pattern to {0}".format(
            app.config['PUZZLE_PATTERN']
        ))
        self.pattern = app.config['PUZZLE_PATTERN']
        
        self.mode = app.config['PUZZLE_MODE']
        logger.info("Setting mode to {0}".format(self.mode))
        logger.debug("Setting can_filter_gene to 'True'")
        self.can_filter_gene = True
        if self.mode == 'sv':
            logger.debug("Setting can_filter_sv to 'True'")
            self.can_filter_sv = True
            logger.debug("Setting can_filter_sv_len to 'True'")
            self.can_filter_sv_len = True
        else:
            logger.debug("Setting can_filter_frequency to 'True'")
            self.can_filter_frequency = True
            logger.debug("Setting can_filter_cadd to 'True'")
            self.can_filter_cadd = True
            logger.debug("Setting can_filter_consequence to 'True'")
            self.can_filter_consequence = True
            logger.debug("Setting can_filter_inheritance to 'True'")
            self.can_filter_inheritance = True

        if app.config.get('FAMILY_FILE'):
            #If ped file we know there is only one vcf
            self.case_obj = self._get_case(
                variant_source=self.root_path, 
                case_lines = app.config['FAMILY_FILE'], 
                case_type=app.config.get('FAMILY_TYPE'),
                bam_paths=app.config.get('BAM_PATHS', {}))

