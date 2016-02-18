# -*- coding: utf-8 -*-
import logging

from puzzle.models.dotdict import DotDict

logger = logging.getLogger(__name__)


class Plugin(object):
    """docstring for Plugin"""
    def __init__(self):
        super(Plugin, self).__init__()
        self.db = None
        self.puzzle_db = None
        self.individuals = None
        self.case_objs = None
        self.variant_type = 'snv'
        self.filters = DotDict(
            can_filter_frequency=False,
            can_filter_cadd=False,
            can_filter_consequence=False,
            can_filter_gene=False,
            can_filter_inheritance=False,
            can_filter_sv=False,
            can_filter_impact_severity=False,
        )

    def init_app(self, app):
        """Initialize plugin via Flask."""
        raise NotImplementedError

    def individual_dict(self, ind_ids):
        """Return a dict with ind_id as key and Individual as values."""
        ind_dict = {ind.ind_id: ind for ind in self.individuals(ind_ids=ind_ids)}
        return ind_dict
