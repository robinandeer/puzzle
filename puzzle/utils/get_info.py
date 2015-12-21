import logging
from .constants import (SEVERITY_DICT, HGNC_TO_OMIM, CYTOBAND_READER)
from tabix import TabixError

from phizz.utils import query_gene

from puzzle.models import Gene

logger = logging.getLogger(__name__)


def get_gene_info(transcripts):
    """Return the genes info based on the transcripts found
    
        Args:
            transcript(Transcript): A dictionary with transcript info
        
        Returns:
            genes (iterable): An iterable with Genes
    """
    ensembl_ids = set([transcript['Gene'] for transcript in transcripts])
    hgnc_symbols = set([transcript['SYMBOL'] for transcript in transcripts])
    genes = []
    
    if ensembl_ids:
        for ensembl_id in ensembl_ids:
            if ensembl_id:
                for gene in query_gene(ensembl_id=ensembl_id):
                    genes.append(Gene(
                        symbol=gene['hgnc_symbol'],
                        hgnc_id=gene['hgnc_symbol'],
                        ensembl_id=gene['ensembl_id'],
                        description=gene['description'],
                        chrom=gene['chrom'],
                        start=gene['start'],
                        stop=gene['stop'],
                        location=get_cytoband_coord(gene['chrom'], gene['start']),
                        hi_score=gene['hi_score'],
                        constraint_score=gene['constraint_score'],
                        omim_number=get_omim_number(gene['hgnc_symbol']),
                    ))
    elif hgnc_symbols:
        for hgnc_symbol in hgnc_symbols:
            if hgnc_symbol:
                for gene in query_gene(hgnc_symbol=hgnc_symbol):
                    genes.append(Gene(
                        symbol=gene['hgnc_symbol'],
                        hgnc_id=gene['hgnc_symbol'],
                        ensembl_id=gene['ensembl_id'],
                        description=gene['description'],
                        chrom=gene['chrom'],
                        start=gene['start'],
                        stop=gene['stop'],
                        location=get_cytoband_coord(gene['chrom'], gene['start']),
                        hi_score=gene['hi_score'],
                        constraint_score=gene['constraint_score'],
                        omim_number=get_omim_number(gene['hgnc_symbol']),
                    ))
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
        for consequence in transcript['Consequence'].split('&'):
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
    chrom = "chr{0}".format(chrom.lstrip('chr'))
    pos = int(pos)
    result = None
    logger.debug("Finding Cytoband for chrom:{0} pos:{1}".format(chrom, pos))
    try:
        for record in CYTOBAND_READER.query(chrom, pos, pos+1):
            record_chrom = record[0].lstrip('chr')
            coord = record[3]
            result = "{0}{1}".format(record_chrom, coord)
    except TabixError:
        pass
    return result

def get_hgnc_symbols(transcripts):
    """Get the hgnc symbols

        Go through all transcripts and get hgnc symbols

        Args:
            transcripts (list): A list of transcripts to evaluate

        Returns:
            hgnc_symbols (list): The hgnc symbols
    """

    hgnc_symbols = set()
    for transcript in transcripts:
        hgnc_symbol = transcript['SYMBOL']

        if hgnc_symbol:
            hgnc_symbols.add(hgnc_symbol)

    return hgnc_symbols


def get_omim_number(hgnc_symbol):
    """Get the omim number for a hgnc symbol

        Args:
            hgnc_symbol (str): A hgnc symbol

        Returns:
            omim_number (int): The omim number
    """

    omim_number = HGNC_TO_OMIM.get(hgnc_symbol,{}).get('mim_nr', None)

    return omim_number

def get_ensembl_id(hgnc_symbol):
    """Get the ensembl id for a hgnc symbol

        Args:
            hgnc_symbol (str): A hgnc symbol

        Returns:
            ensembl_id (int): The ensembl id
    """
    ensembl_id = HGNC_TO_OMIM.get(hgnc_symbol, {}).get('ensembl_id', None)

    return ensembl_id
