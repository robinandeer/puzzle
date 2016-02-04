# -*- coding: utf-8 -*-
import logging

from . import (DotDict, PedigreeHumanMixin)

logger = logging.getLogger(__name__)

class Genotype(DotDict, PedigreeHumanMixin):
    """Class that holds information about a genotype call"""
    def __init__(self, sample_id, genotype, case_id=None, phenotype=None,
                ref_depth='.', alt_depth='.', genotype_quality='.', depth='.',
                supporting_evidence='0', pe_support='0', sr_support='0'):
        super(Genotype, self).__init__(sample_id=sample_id, genotype=genotype,
            case_id=case_id, phenotype=phenotype, ref_depth=ref_depth, 
            alt_depth=alt_depth, depth=depth, genotype_quality=genotype_quality,
            supporting_evidence=supporting_evidence, pe_support=pe_support, 
            sr_support=sr_support)
