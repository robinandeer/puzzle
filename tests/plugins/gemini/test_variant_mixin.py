##TODO mock a gemini db
import pytest
from puzzle.plugins import GeminiPlugin
from puzzle.models import Individual

def test_get_variants(gemini_path):
    """Test to get some variants from the gemini adapter"""
    adapter = GeminiPlugin(db=gemini_path)
    variants = []
    for variant in adapter.variants('643594', count=5):
        variants.append(variant)

    assert len(variants) == 5

def test_variant(gemini_path):
    """Test to get one variant"""
    adapter = GeminiPlugin(db=gemini_path)
    variant = adapter.variant(
        case_id='643594',
        variant_id=4
    )

    assert variant['CHROM'] == '6'
    assert variant['POS'] == '32487163'

def test_is_variant(case_obj):
    adapter = GeminiPlugin()
    genotypes = ['G/A', 'G/A', 'G/G', 'G/G', './.']
    ind_objs = [
        Individual(ind_id=0, ind_index=0),
        Individual(ind_id=1, ind_index=1),
    ]
    #Mock a gemini variant
    gemini_variant = {
        'gts':genotypes,
        'alt':'A'
    }
    
    assert adapter._is_variant(gemini_variant, ind_objs)
    
    #Check with individuals that are hom ref
    ind_objs = [
        Individual(ind_id=0, ind_index=2),
        Individual(ind_id=1, ind_index=3),
    ]

    assert not adapter._is_variant(gemini_variant, ind_objs)

    #Check with individual that has no call
    ind_objs = [
        Individual(ind_id=0, ind_index=4),
    ]

    assert not adapter._is_variant(gemini_variant, ind_objs)
