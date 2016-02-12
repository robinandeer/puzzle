from puzzle.utils import (get_most_severe_consequence, get_cytoband_coord,
                          get_omim_number, get_gene_info)


def test_get_gene_info():
    # test with HGNC symbol
    genes = list(get_gene_info(hgnc_symbols=['CHAT']))
    assert len(genes) == 1
    assert genes[0].symbol == 'CHAT'
    assert genes[0].ensembl_id == 'ENSG00000070748'

    # test with Ensembl id
    genes = list(get_gene_info(ensembl_ids=['ENSG00000156110']))
    assert len(genes) == 1
    assert genes[0].symbol == 'ADK'
    assert genes[0].ensembl_id == 'ENSG00000156110'

def test_get_most_severe_consequence():
    """Test get_most_sever_consequence(transcripts) method"""

    print("Test get_most_sever_consequence with a 'regular' transcripts list")
    transcripts = [
        {'consequence': 'transcript_ablation'}
    ]
    assert get_most_severe_consequence(transcripts) == 'transcript_ablation'

    print("Test get_most_sever_consequence with empty transcripts list")
    transcripts = []
    assert get_most_severe_consequence(transcripts) is None

    print("Test get_most_sever_consequence with 'unknown' consequence")
    transcripts = [
        {'consequence': 'unknown'}
    ]
    assert get_most_severe_consequence(transcripts) is None

    print("Test most_severe_consequence with multiple transcripts")
    transcripts = [
        {'consequence': 'inframe_deletion'},
        {'consequence': 'start_lost'},
        {'consequence': 'synonymous_variant'}
    ]
    assert get_most_severe_consequence(transcripts) == 'start_lost'

    print("Test most_severe_consequence with multiple transcripts (annotations)")
    transcripts = [
        {'consequence': 'start_lost&synonymous_variant'},
    ]
    assert get_most_severe_consequence(transcripts) == 'start_lost'

def test_get_cytoband_coord():
    """test get_cytoband_coord(chrom, pos) method"""

    print("Test get_cytoband_coord with different input formats")
    assert get_cytoband_coord('1', 3) == '1p36.33'
    assert get_cytoband_coord('chr1', 3) == '1p36.33'
    assert get_cytoband_coord('chr1', '3') == '1p36.33'

    print("Test get_cytoband_coord with non existing chromosome")
    assert get_cytoband_coord('chrMT', '3') is None

    print("Test get_cytoband_coord with non existing position")
    assert get_cytoband_coord('chrX', '155270600') is None

def test_get_omim_number():
    """Test get_omim_number(hgnc_symbol) method"""

    print("Test get_omim_number with valid hgnc_symbol")
    assert get_omim_number('IFT172') == 607386

    print("Test get_omim_number with invalid hgnc_symbol")
    assert get_omim_number('HEJ') is None

    print("Test getting phenotype")
    assert get_omim_number('MCCRP2') != get_omim_number('PLK4')
    assert get_omim_number('MCCRP2') is None
    assert get_omim_number('PLK4') == 605031
