import itertools
import logging
from .constants import (SEVERITY_DICT, HGNC_TO_OMIM, CYTOBANDS)

from phizz.utils import query_gene

from puzzle.models import Gene

logger = logging.getLogger(__name__)


def get_gene_info(ensembl_ids=None, hgnc_symbols=None):
    """Return the genes info based on the transcripts found

    Args:
        ensembl_ids (Optional[list]): list of Ensembl gene ids
        hgnc_symbols (Optional[list]): list of HGNC gene symbols

    Returns:
        iterable: an iterable with `Gene` objects
    """
    uniq_ensembl_ids = set(ensembl_id for ensembl_id in (ensembl_ids or []))
    uniq_hgnc_symbols = set(hgnc_symbol for hgnc_symbol in (hgnc_symbols or []))

    ensembl = itertools.chain(*[query_gene(ensembl_id=ensembl_id)
                                for ensembl_id in uniq_ensembl_ids])
    hgnc = itertools.chain(*[query_gene(hgnc_symbol=hgnc_symbol)
                             for hgnc_symbol in uniq_hgnc_symbols])

    gene_data = list(itertools.chain.from_iterable([ensembl, hgnc]))
    genes = [Gene(symbol=gene['hgnc_symbol'],
                  hgnc_id=gene['hgnc_id'],
                  ensembl_id=gene['ensembl_id'],
                  description=gene['description'],
                  chrom=gene['chrom'],
                  start=gene['start'],
                  stop=gene['stop'],
                  location=get_cytoband_coord(gene['chrom'], gene['start']),
                  hi_score=gene['hi_score'],
                  constraint_score=gene['constraint_score'],
                  omim_number=get_omim_number(gene['hgnc_symbol']))
             for gene in gene_data]
    return genes

def get_most_severe_consequence(transcripts):
    """Get the most severe consequence

        Go through all transcripts and get the most severe consequence

        Args:
            transcripts (list): A list of transcripts to evaluate

        Returns:
            most_severe_consequence (str): The most severe consequence
    """
    most_severe_consequence = None
    most_severe_score = None

    for transcript in transcripts:
        for consequence in transcript['consequence'].split('&'):
            logger.debug("Checking severity score for consequence: {0}".format(
                consequence
            ))
            severity_score = SEVERITY_DICT.get(
                consequence
            )
            logger.debug("Severity score found: {0}".format(
                severity_score
            ))
            if severity_score != None:
                if most_severe_score:
                    if severity_score < most_severe_score:
                        most_severe_consequence = consequence
                        most_severe_score = severity_score
                else:
                    most_severe_consequence = consequence
                    most_severe_score = severity_score

    return most_severe_consequence

def get_cytoband_coord(chrom, pos):
    """Get the cytoband coordinate for a position

        Args:
            chrom(str): A chromosome
            pos(int): The position

        Returns:
            cytoband
    """
    chrom = chrom.strip('chr')
    pos = int(pos)
    result = None
    logger.debug("Finding Cytoband for chrom:{0} pos:{1}".format(chrom, pos))
    if chrom in CYTOBANDS:
        for interval in CYTOBANDS[chrom][pos]:
            result = "{0}{1}".format(chrom, interval.data)

    return result

def get_omim_number(hgnc_symbol):
    """Get the omim number for a hgnc symbol

        Args:
            hgnc_symbol (str): A hgnc symbol

        Returns:
            omim_number (int): The omim number
    """

    omim_number = HGNC_TO_OMIM.get(hgnc_symbol,{}).get('mim_nr', None)

    return omim_number
