# -*- coding: utf-8 -*-
import logging

from sqlite3 import DatabaseError

from gemini import GeminiQuery

from puzzle.plugins import Plugin
from . import (CaseMixin, VariantMixin)

logger = logging.getLogger(__name__)

class GeminiPlugin(CaseMixin, VariantMixin, Plugin):
    """This is the base class for puzzle plugins

        Args:
            db(str): Path to gemini database
            vtype: Variant type (snv or sv)

    """

    def __init__(self, db=None, vtype='snv'):
        super(GeminiPlugin, self).__init__()
        logger.debug("Setting self.db to {0}".format(db))
        self.db = db
        logger.debug("Setting variant type to {0}".format(vtype))
        self.variant_type = vtype

        if self.db:
            logger.info("Check if database is in correct format")
            self.test_gemini_db()
            
            self.individuals = self._get_individuals()
            self.case_objs = self._get_cases(self.individuals)

        self.filters.can_filter_gene = True
        self.filters.can_filter_frequency = True
        self.filters.can_filter_cadd = True
        self.filters.can_filter_consequence = True
        self.filters.can_filter_impact_severity = True
        self.filters.can_query_gemini=True

    def test_gemini_db(self):
        """Check if self.db is a valid gemini database
            
            Raises sqlite3.DatabaseError if not a valid databse
        """
        gq = GeminiQuery(self.db)
        return True

    def init_app(self, app):
        """Initialize plugin via Flask."""
        pass
