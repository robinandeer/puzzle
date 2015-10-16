from puzzle.models import Variant


def get_variant(CHROM="1",POS='100',ID='rs01',REF='A',ALT='T',QUAL='100',
                FILTER='PASS'):
    """Return a variant dictionary"""
    return {
        'CHROM': CHROM,
        'POS': POS,
        'ID': ID,
        'REF': REF,
        'ALT': ALT,
        'QUAL': QUAL,
        'FILTER': FILTER
    }


def test_variant():
    """docstring for test_variant"""
    variant = Variant(**get_variant())

    assert variant['CHROM'] == '1'
    assert variant['variant_id'] == '1_100_A_T'


def test_adding_transcript():
    """docstring for test_variant"""
    variant = Variant(**get_variant())

    assert variant['transcripts'] == []

    transcript = {'SYMBOL': 'ADK'}
    variant.add_transcript(transcript)

    assert variant['transcripts'] == [transcript]


def test_add_frequency():
    """docstring for test_variant"""
    variant = Variant(**get_variant())
    assert variant['frequencies'] == []
    variant.add_frequency(name='1000G', value=0.01)
    assert variant['frequencies'] == [{'label': '1000G', 'value': 0.01}]


def test_add_severity():
    """docstring for test_variant"""
    variant = Variant(**get_variant())

    assert variant['severities'] == []

    variant.add_severity(
        name='SIFT',
        value=0.9
    )

    assert variant['severities'] == [{'SIFT':0.9}]


def test_add_individual():
    """docstring for test_variant"""
    variant = Variant(**get_variant())

    assert variant['individuals'] == []

    genotype = {'GT':'0/1'}

    variant.add_individual(genotype)

    assert variant['individuals'] == [genotype]


def test_add_gene():
    """docstring for test_variant"""
    variant = Variant(**get_variant())

    assert variant['genes'] == []

    gene = {'HGNC_ID':'ADK'}

    variant.add_gene(gene)

    assert variant['genes'] == [gene]


def test_add_compound():
    """docstring for test_variant"""
    variant = Variant(**get_variant())

    assert variant['compounds'] == []

    compound = {'variant_id':'1_2_A_C'}

    variant.add_compound(compound)

    assert variant['compounds'] == [compound]


def test_update_variant_id():
    """docstring for test_variant"""
    variant = Variant(**get_variant())

    assert variant['variant_id'] == '1_100_A_T'

    variant_id = 'family1_1_2_A_C'

    variant.update_variant_id(variant_id)

    assert variant['variant_id'] == variant_id
