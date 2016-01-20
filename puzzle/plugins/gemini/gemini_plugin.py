# -*- coding: utf-8 -*-
import logging

from puzzle.plugins import Plugin
from puzzle.models import (Variant, Genotype, Gene, Transcript, Case, Individual)
from puzzle.utils import (get_omim_number, get_ensembl_id, get_hgnc_symbols,
                          get_most_severe_consequence)

from . import (CaseMixin, VariantMixin)

logger = logging.getLogger(__name__)


class GeminiPlugin(CaseMixin, VariantMixin, Plugin):
    """This is the base class for puzzle plugins"""

    def __init__(self):
        super(GeminiPlugin, self).__init__()

    def init_app(self, app):
        """Initialize plugin via Flask."""
        logger.debug("Updating root path to {0}".format(
            app.config['PUZZLE_ROOT']
        ))
        self.db = app.config['PUZZLE_ROOT']
        logger.debug("Updating pattern to {0}".format(
            app.config['PUZZLE_ROOT']
        ))
        self.individuals = self._get_individuals()
        self.case_objs = self._get_cases(self.individuals)
        
        self.mode = app.config['PUZZLE_MODE']
        logger.info("Setting mode to {0}".format(self.mode))
        
        logger.debug("Setting can_filter_gene to 'True'")
        self.can_filter_gene = True
        # logger.debug("Setting can_filter_sv to 'True'")
        # self.can_filter_sv = True
        # logger.debug("Setting can_filter_sv_len to 'True'")
        # self.can_filter_sv_len = True
        logger.debug("Setting can_filter_frequency to 'True'")
        self.can_filter_frequency = True
        logger.debug("Setting can_filter_cadd to 'True'")
        self.can_filter_cadd = True
        logger.debug("Setting can_filter_consequence to 'True'")
        self.can_filter_consequence = True
