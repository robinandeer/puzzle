##TODO mock a gemini db
import pytest
from puzzle.plugins import GeminiPlugin
from puzzle.models import Individual, Variant, DotDict

def test_get_all_variants(gemini_case_obj):
    """Test to get some variants from the gemini adapter"""
    plugin = GeminiPlugin()
    plugin.add_case(gemini_case_obj)

    filters = {}
    result = plugin.variants('643594', filters=filters, count=1000)
    variants = result.variants
    nr_of_variants = result.nr_of_variants

    assert nr_of_variants == 14

def test_get_variants(gemini_case_obj):
    """Test to get some variants from the gemini plugin"""
    plugin = GeminiPlugin()
    plugin.add_case(gemini_case_obj)

    filters = {}
    result = plugin.variants('643594', filters=filters, count=5)
    variants = result.variants
    nr_of_variants = result.nr_of_variants

    assert nr_of_variants == 5

def test_variant(gemini_case_obj):
    """Test to get one variant"""
    plugin = GeminiPlugin()
    plugin.add_case(gemini_case_obj)

    variant = plugin.variant(
        case_id='643594',
        variant_id=4
    )

    assert variant['CHROM'] == '6'
    assert variant['POS'] == '32487163'
    assert type(variant['genes']) == type([])

def test_is_variant(gemini_case_obj):
    plugin = GeminiPlugin()
    genotypes = ['G/A', 'G/A', 'G/G', 'G/G', './.']
    gt_types = [1, 1, 0, 0, 2]
    ind_objs = [
        Individual(ind_id=0, ind_index=0),
        Individual(ind_id=1, ind_index=1),
    ]
    #Mock a gemini variant
    gemini_variant = {
        'gts':genotypes,
        'gt_types':gt_types,
        'alt':'A'
    }

    assert plugin._is_variant(gemini_variant, ind_objs)

    #Check with individuals that are hom ref
    ind_objs = [
        Individual(ind_id=0, ind_index=2),
        Individual(ind_id=1, ind_index=3),
    ]

    assert not plugin._is_variant(gemini_variant, ind_objs)

    #Check with individual that has no call
    ind_objs = [
        Individual(ind_id=0, ind_index=4),
    ]

    assert not plugin._is_variant(gemini_variant, ind_objs)

def test_build_gemini_query():
    plugin = GeminiPlugin()
    query = "SELECT * from variants"
    extra_info = "max_aaf_all < 0.01"
    new_query = plugin.build_gemini_query(query, extra_info)
    assert new_query == "SELECT * from variants WHERE max_aaf_all < 0.01"

    extra_info = "cadd_score > 10"
    new_query = plugin.build_gemini_query(new_query, extra_info)
    assert new_query == "SELECT * from variants WHERE max_aaf_all < 0.01 AND cadd_score > 10"

class TestFilters:

    def test_filters_no_filters(self, gemini_case_obj):
        plugin = GeminiPlugin()
        plugin.add_case(gemini_case_obj)

        filters = {}
        result = plugin.variants('643594', filters=filters, count=1000)
        variants = result.variants
        nr_of_variants = result.nr_of_variants

        assert nr_of_variants == 14

    def test_filters_frequency(self, gemini_case_obj):
        plugin = GeminiPlugin()
        plugin.add_case(gemini_case_obj)

        filters = {'frequency':'0.01'}
        result = plugin.variants('643594', filters=filters, count=1000)
        variants = result.variants
        nr_of_variants = result.nr_of_variants
        
        for variant_obj in variants:
            assert variant_obj.max_freq < 0.01
        
        assert nr_of_variants == 13

    def test_filters_cadd(self, gemini_case_obj):
        plugin = GeminiPlugin()
        plugin.add_case(gemini_case_obj)

        filters = {'cadd':'20'}
        result = plugin.variants('643594', filters=filters, count=1000)
        variants = result.variants
        nr_of_variants = result.nr_of_variants
        
        for variant_obj in variants:
            assert variant_obj.cadd_score > 20
        
        assert nr_of_variants == 4

    def test_filters_impact_severities_high(self, gemini_case_obj):
        plugin = GeminiPlugin()
        plugin.add_case(gemini_case_obj)

        filters = {'impact_severities':['HIGH']}
        result = plugin.variants('643594', filters=filters, count=1000)
        variants = result.variants
        nr_of_variants = result.nr_of_variants
        
        for variant_obj in variants:
            assert variant_obj.impact_severity == 'HIGH'
        
        assert nr_of_variants == 2

    def test_filters_impact_severities_medium(self, gemini_case_obj):
        plugin = GeminiPlugin()
        plugin.add_case(gemini_case_obj)

        filters = {'impact_severities':['MEDIUM']}
        result = plugin.variants('643594', filters=filters, count=1000)
        variants = result.variants
        nr_of_variants = result.nr_of_variants
        
        for variant_obj in variants:
            assert variant_obj.impact_severity == 'MEDIUM'
        assert nr_of_variants == 10

    def test_filters_impact_severities_low(self, gemini_case_obj):
        plugin = GeminiPlugin()
        plugin.add_case(gemini_case_obj)

        filters = {'impact_severities':['LOW']}
        result = plugin.variants('643594', filters=filters, count=1000)
        variants = result.variants
        nr_of_variants = result.nr_of_variants
        
        for variant_obj in variants:
            assert variant_obj.impact_severity == 'LOW'
        
        assert nr_of_variants == 2

    def test_filters_impact_severities_high_and_med(self, gemini_case_obj):
        plugin = GeminiPlugin()
        plugin.add_case(gemini_case_obj)

        filters = {'impact_severities':['HIGH', 'MEDIUM']}
        result = plugin.variants('643594', filters=filters, count=1000)
        variants = result.variants
        nr_of_variants = result.nr_of_variants
        
        for variant_obj in variants:
            assert variant_obj.impact_severity in ['HIGH', 'MEDIUM']
        
        assert nr_of_variants == 12

    def test_filters_gene_ids(self, gemini_case_obj):
        plugin = GeminiPlugin()
        plugin.add_case(gemini_case_obj)

        filters = {'gene_ids':['HLA-DRB5']}
        result = plugin.variants('643594', filters=filters, count=1000)
        variants = result.variants
        nr_of_variants = result.nr_of_variants
        
        for variant_obj in variants:
            assert 'HLA-DRB5' in variant_obj.gene_symbols
        
        assert nr_of_variants == 5

    def test_filters_consequence(self, gemini_case_obj):
        plugin = GeminiPlugin()
        plugin.add_case(gemini_case_obj)

        filters = {'consequence':['stop_gained']}
        result = plugin.variants('643594', filters=filters, count=1000)
        variants = result.variants
        nr_of_variants = result.nr_of_variants
        
        for variant_obj in variants:
            assert 'stop_gained' in variant_obj.consequences
        
        assert nr_of_variants == 2

    def test_no_filters_sv(self, gemini_sv_case_obj):
        plugin = GeminiPlugin()
        plugin.add_case(gemini_sv_case_obj)

        filters = {}
        result = plugin.variants('hapmap', filters=filters, count=1000)
        variants = result.variants
        nr_of_variants = result.nr_of_variants
        
        assert nr_of_variants == 513

    def test_filters_sv_len(self, gemini_sv_case_obj):
        plugin = GeminiPlugin()
        plugin.add_case(gemini_sv_case_obj)

        filters = {'sv_len':'800'}
        result = plugin.variants('hapmap', filters=filters, count=1000)
        variants = result.variants
        nr_of_variants = result.nr_of_variants
        
        for variant_obj in variants:
            assert variant_obj.sv_len >= 800
        
        assert nr_of_variants == 176

    def test_filters_range(self, gemini_case_obj):
        plugin = GeminiPlugin()
        plugin.add_case(gemini_case_obj)

        start = 92498060
        end = 92498100

        filters = {'range': {'chromosome': 'chr1', 'start': start, 'end':end}}
        result = plugin.variants('643594', filters=filters, count=1000)
        variants = result.variants
        nr_of_variants = result.nr_of_variants
        
        for variant_obj in variants:
            assert variant_obj.start >= start
            assert variant_obj.stop <= end
        
        assert nr_of_variants == 1
