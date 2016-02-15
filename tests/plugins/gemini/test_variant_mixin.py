##TODO mock a gemini db
import pytest
from puzzle.plugins import GeminiPlugin
from puzzle.models import Individual

def test_get_all_variants(gemini_path):
    """Test to get some variants from the gemini adapter"""
    adapter = GeminiPlugin(db=gemini_path)
    variants = []
    for variant in adapter.variants('643594'):
        variants.append(variant)

    assert len(variants) == 14

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
    assert type(variant['genes']) == type([])

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

def test_build_gemini_query():
    adapter = GeminiPlugin()
    query = "SELECT * from variants"
    extra_info = "max_aaf_all < 0.01"
    new_query = adapter.build_gemini_query(query, extra_info)
    assert new_query == "SELECT * from variants WHERE max_aaf_all < 0.01"
    
    extra_info = "cadd_score > 10"
    new_query = adapter.build_gemini_query(new_query, extra_info)
    assert new_query == "SELECT * from variants WHERE max_aaf_all < 0.01 AND cadd_score > 10"

class TestFilters:

    def test_filters_frequency(self, gemini_path):
        adapter = GeminiPlugin(db=gemini_path)
        filters = {'frequency':'0.01'}
        variants = []
        for variant in adapter.variants('643594', filters=filters):
            variants.append(variant)
        assert len(variants) == 13

    def test_filters_cadd(self, gemini_path):
        adapter = GeminiPlugin(db=gemini_path)
        filters = {'cadd':'20'}
        variants = []
        for variant in adapter.variants('643594', filters=filters):
            variants.append(variant)
        assert len(variants) == 4
    
    def test_filters_impact_severities(self, gemini_path):
        adapter = GeminiPlugin(db=gemini_path)
        filters = {'impact_severities':['HIGH']}
        variants = []
        for variant in adapter.variants('643594', filters=filters):
            variants.append(variant)
        assert len(variants) == 2

    def test_filters_gene_ids(self, gemini_path):
        adapter = GeminiPlugin(db=gemini_path)
        filters = {'gene_ids':['HLA-DRB5']}
        variants = []
        for variant in adapter.variants('643594', filters=filters):
            variants.append(variant)
        assert len(variants) == 5

    def test_filters_consequence(self, gemini_path):
        adapter = GeminiPlugin(db=gemini_path)
        filters = {'consequence':['stop_gained']}
        variants = []
        for variant in adapter.variants('643594', filters=filters):
            variants.append(variant)
        assert len(variants) == 2
    