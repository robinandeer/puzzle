from puzzle.utils import get_csq

def test_get_csq():
    description = '"Consequence annotations from Ensembl VEP. Format: Allele|Consequence"'
    csq_cols = get_csq(description)
    assert csq_cols == ['Allele', 'Consequence']