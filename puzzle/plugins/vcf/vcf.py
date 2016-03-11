# -*- coding: utf-8 -*-
import os
import logging

from path import path

from puzzle.plugins import Plugin
from puzzle.models import DotDict
from puzzle.utils import get_cases
from .mixins import VariantMixin, CaseMixin

logger = logging.getLogger(__name__)


class VcfPlugin(VariantMixin, CaseMixin, Plugin):
    """docstring for Plugin"""

    def __init__(self, variant_type='snv'):
        """Initialize a vcf adapter.

            When instansiating all cases are found.

            Args:
                variant_type(str) : 'snv' or 'sv'
        """
        super(VcfPlugin, self).__init__()

        self.individual_objs = []
        self.case_objs = []

        self.variant_type = variant_type
        logger.info("Setting variant type to {0}".format(variant_type))

        self.variant_columns = ['CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER']
        
        self.head = None
        self.vep_header = None
        self.snpeff_header = None
        
        
        self.filters.can_filter_gene = True
        self.filters.can_filter_frequency = True
        self.filters.can_filter_cadd = True
        self.filters.can_filter_consequence = True
        self.filters.can_filter_impact_severity = True
        self.filters.can_filter_sv = True
        self.filters.can_filter_sv_len = True
        self.filters.can_filter_inheritance = True

    def init_app(self, app):
        """Initialize plugin via Flask."""
        pass

