##TODO mock a gemini db
import pytest
from puzzle.plugins import GeminiPlugin
from puzzle.models import Individual, Variant, DotDict

def test_get_all_variants(gemini_case_obj):
    """Test to get some variants from the gemini adapter"""
    adapter = GeminiPlugin()
    adapter.add_case(gemini_case_obj)

    variants = []
    for variant in adapter.variants('643594'):
        variants.append(variant)

    assert len(variants) == 14

def test_get_variants(gemini_case_obj):
    """Test to get some variants from the gemini adapter"""
    adapter = GeminiPlugin()
    adapter.add_case(gemini_case_obj)

    variants = []
    for variant in adapter.variants('643594', count=5):
        variants.append(variant)

    assert len(variants) == 5

def test_variant(gemini_case_obj):
    """Test to get one variant"""
    adapter = GeminiPlugin()
    adapter.add_case(gemini_case_obj)

    variant = adapter.variant(
        case_id='643594',
        variant_id=4
    )

    assert variant['CHROM'] == '6'
    assert variant['POS'] == '32487163'
    assert type(variant['genes']) == type([])

def test_is_variant(gemini_case_obj):
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

    def test_filters_frequency(self, gemini_case_obj):
        adapter = GeminiPlugin()
        adapter.add_case(gemini_case_obj)

        filters = {'frequency':'0.01'}
        for variant in adapter.variants('643594', filters=filters):
            assert variant.max_freq < 0.01

    def test_filters_cadd(self, gemini_case_obj):
        adapter = GeminiPlugin()
        adapter.add_case(gemini_case_obj)

        filters = {'cadd':'20'}
        for variant in adapter.variants('643594', filters=filters):
            assert variant.cadd_score > 20

    def test_filters_impact_severities(self, gemini_case_obj):
        adapter = GeminiPlugin()
        adapter.add_case(gemini_case_obj)

        variants = []
        filters = {'impact_severities':['HIGH']}
        for variant in adapter.variants('643594', filters=filters):
            variants.append(variant)
            assert variant.impact_severity == 'HIGH'
        assert len(variants) == 2

    def test_filters_gene_ids(self, gemini_case_obj):
        adapter = GeminiPlugin()
        adapter.add_case(gemini_case_obj)

        filters = {'gene_ids':['HLA-DRB5']}
        variants = []
        for variant in adapter.variants('643594', filters=filters):
            variants.append(variant)
            assert 'HLA-DRB5' in variant.gene_symbols
        assert len(variants) == 5

    def test_filters_consequence(self, gemini_case_obj):
        adapter = GeminiPlugin()
        adapter.add_case(gemini_case_obj)

        filters = {'consequence':['stop_gained']}
        variants = []
        for variant in adapter.variants('643594', filters=filters):
            assert 'stop_gained' in variant.consequences
            variants.append(variant)
        assert len(variants) == 2

    def test_no_filters_sv(self, gemini_sv_case_obj):
        adapter = GeminiPlugin()
        adapter.add_case(gemini_sv_case_obj)

        filters = {}
        variants = []
        for variant in adapter.variants('hapmap', filters=filters, count=1000):
            variants.append(variant)
        assert len(variants) == 513

    def test_filters_sv_len(self, gemini_sv_case_obj):
        adapter = GeminiPlugin()
        adapter.add_case(gemini_sv_case_obj)

        filters = {'sv_len':'800'}
        variants = []
        for variant in adapter.variants('hapmap', filters=filters, count=1000):
            assert variant.sv_len >= 800
            variants.append(variant)
        assert len(variants) == 176

    def test_filters_range(self, gemini_case_obj):
        adapter = GeminiPlugin()
        adapter.add_case(gemini_case_obj)
        
        start = 92498060
        end = 92498100
        
        filters = {'range': {'chromosome': 'chr1', 'start': start, 'end':end}}
        variants = []
        for variant in adapter.variants('643594', filters=filters, count=1000):
            assert variant.start >= start
            assert variant.stop <= end
            variants.append(variant)
        assert len(variants) == 1
