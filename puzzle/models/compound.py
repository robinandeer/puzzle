# -*- coding: utf-8 -*-
import logging

from . import DotDict

logger = logging.getLogger(__name__)


class Compound(DotDict):
    """Class that holds information about a compound variant"""
    def __init__(self, variant_id, combined_score=None):
        super(Compound, self).__init__(variant_id=variant_id,
                                       combined_score=combined_score)
