# -*- coding: utf-8 -*-
import logging

from .dotdict import DotDict

logger = logging.getLogger(__name__)


class Transcript(DotDict):
    """Class that holds information about a transcript"""
    def __init__(self, hgnc_symbol, transcript_id, consequence, ensembl_id=None, biotype=None, 
                strand=None, sift=None, polyphen=None, exon=None, HGVSc=None, 
                HGVSp=None, GMAF=None, ExAC_MAF=None):
        super(Transcript, self).__init__(
            hgnc_symbol=hgnc_symbol, transcript_id=transcript_id, biotype=biotype,
            consequence=consequence, ensembl_id=ensembl_id, strand=strand, sift=sift,
            polyphen=polyphen, exon=exon, HGVSc=HGVSc, HGVSp=HGVSp, GMAF=GMAF, 
            ExAC_MAF=ExAC_MAF)
