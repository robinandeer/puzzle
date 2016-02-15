# -*- coding: utf-8 -*-
import query_phenomizer


def hpo_genes(phenotype_ids):
    """Return list of HGNC symbols matching HPO phenotype ids.

    Returns:
        query_result: a list of dictionaries on the form
        {
            'p_value': float,
            'gene_id': str,
            'omim_id': int,
            'orphanet_id': int,
            'decipher_id': int,
            'any_id': int,
            'mode_of_inheritance': str,
            'description': str,
            'raw_line': str
        }
    """
    if phenotype_ids:
        try:
            results = query_phenomizer.query(phenotype_ids)
            return [result for result in results
                    if result['p_value'] is not None]
        except SystemExit, RuntimeError:
            pass
    return None
