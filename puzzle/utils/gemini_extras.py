import logging

logger = logging.getLogger(__name__)

class Args(object):
    """
    >>> args = Args(db='some.db')
    >>> args.db
    'some.db'
    """
    _opts = ("columns", "db", "filter", "min_kindreds", "families",
                 "pattern_only", "max_priority", # only for compound_het
                 "allow_unaffected", "min_gq", "lenient", "min_sample_depth")
    def __init__(self, **kwargs):
        if not "min_gq" in kwargs:
            kwargs['min_gq'] = 0
        
        if not "lenient" in kwargs:
            kwargs['lenient'] = False
        
        for k in ("families", "filter"):
            if not k in kwargs:
                kwargs[k] = None
        
        if not "gt_phred_ll" in kwargs:
            kwargs['gt_phred_ll'] = None
        
        if not "min_sample_depth" in kwargs:
            kwargs['min_sample_depth'] = 0

        for k in ("min_kindreds", "max_priority"):
            if not k in kwargs: kwargs[k] = 1
        
        for k in ("pattern_only", "allow_unaffected"):
            if not k in kwargs: kwargs[k] = False
        
        self.__dict__.update(**kwargs)


def add_to_query(query, extra_info, add_where=True):
    """Append sql to a gemini query

    Args:
        query(str): The gemini query
        extra_info(str): The text that should be added

    Return:
        extended_query(str)
    """
    if add_where:
        if not 'WHERE' in query:
            return "{0} WHERE {1}".format(query, extra_info)
        else:
            return "{0} AND {1}".format(query, extra_info)
    else:
        if not query:
            return "{0}".format(extra_info)
        else:
            return "{0} AND {1}".format(query, extra_info)

def build_gemini_query(filters, add_where=True):
    """Build a gemini query based on the filters
    
    Args:
        filters (dict): A dictionary with filters
    
    Returns:
        gemini_query (str): A gemini query string
    """
    if add_where:
        gemini_query = filters.get('gemini_query') or "SELECT * from variants"
    else:
        gemini_query = ""
    
    if filters.get('frequency'):
        frequency = filters['frequency']

        extra_info = "(max_aaf_all < {0} or max_aaf_all is"\
                     " Null)".format(frequency)
        gemini_query = add_to_query(gemini_query, extra_info, add_where)

    if filters.get('cadd'):
        cadd_score = filters['cadd']

        extra_info = "(cadd_scaled > {0})".format(cadd_score)
        gemini_query = add_to_query(gemini_query, extra_info, add_where)

    if filters.get('gene_ids'):
        gene_list = [gene_id.strip() for gene_id in filters['gene_ids']]

        gene_string = "gene in ("
        for index, gene_id in enumerate(gene_list):
            if index == 0:
                gene_string += "'{0}'".format(gene_id)
            else:
                gene_string += ", '{0}'".format(gene_id)
        gene_string += ")"

        gemini_query = add_to_query(gemini_query, gene_string, add_where)

    if filters.get('range'):
        chrom = filters['range']['chromosome']
        if not chrom.startswith('chr'):
            chrom = "chr{0}".format(chrom)
        
        range_string = "chrom = '{0}' AND "\
                       "((start BETWEEN {1} AND {2}) OR "\
                       "(end BETWEEN {1} AND {2}))".format(
                           chrom,
                           filters['range']['start'],
                           filters['range']['end']
                       )
        gemini_query = add_to_query(gemini_query, range_string, add_where)

    return gemini_query
    
