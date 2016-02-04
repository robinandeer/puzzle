# -*- coding: utf-8 -*-
import logging

from .mixins import PedigreeHumanMixin
from . import DotDict

logger = logging.getLogger(__name__)


class Gene(DotDict):
    """Class that holds information about a Gene"""
    def __init__(self, symbol, omim_number=None, ensembl_id=None, 
                description=None, chrom=None, start=None, stop=None,
                location=None, hi_score=None, constraint_score=None,
                hgnc_id=None):
        super(Gene, self).__init__(symbol=symbol, omim_number=omim_number,
        ensembl_id=ensembl_id, description=description, chrom=chrom, 
        start=start, stop=stop, location=location, hi_score=hi_score, 
        constraint_score=constraint_score, hgnc_id=hgnc_id)
        
        self['morbid'] = None
