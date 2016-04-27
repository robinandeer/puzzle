# -*- coding: utf-8 -*-
from puzzle.plugins import VcfPlugin


def test_variants_case(case_obj):
    vcf_plugin = VcfPlugin()
    vcf_plugin.add_case(case_obj)
    #case_id is 'hapmap.vcf' since no ped file is given
    result = vcf_plugin.variants(case_id=case_obj.case_id)
    variants = result.variants
    variant = variants[0]
    assert variant['CHROM'] == 'X'
    assert int(variant['POS']) == 84563218
    assert variant['index'] == 1

    variant = variants[1]
    assert variant['CHROM'] == '2'
    assert int(variant['POS']) == 233349186
    assert variant['index'] == 2

def test_variant(case_obj):
    vcf_plugin = VcfPlugin()
    vcf_plugin.add_case(case_obj)

    variant = vcf_plugin.variant(case_obj.case_id, 'X_155239821_G_A')
    assert variant['CHROM'] == 'X'
    assert int(variant['POS']) == 155239821

    # get 10th variant
    variant = vcf_plugin.variant(case_obj.case_id, '3_124998098_C_A')
    assert variant['index'] == 10

def test_format_variants(cyvcf_variant, case_obj, header):
    vcf_plugin = VcfPlugin()
    vcf_plugin.head = header
    vcf_plugin.vep_header = header.vep_columns
    vcf_plugin.snpeff_header = header.snpeff_columns

    variant_obj = vcf_plugin._format_variants(cyvcf_variant, index=1,
                             case_obj=case_obj, add_all_info=False)

    assert variant_obj.CHROM == cyvcf_variant.CHROM
    assert variant_obj.start == cyvcf_variant.start

class TestFilters:

    def test_filters_no_filter(self, case_obj):
        plugin = VcfPlugin()
        plugin.add_case(case_obj)
        case_id = case_obj.case_id

        filters = {}
        result = plugin.variants(case_id, filters=filters, count=1000)
        
        assert result.nr_of_variants == 108

    def test_filters_frequency(self, case_obj):
        plugin = VcfPlugin()
        plugin.add_case(case_obj)
        case_id = case_obj.case_id

        filters = {'frequency':'0.001'}
        result = plugin.variants(case_id, filters=filters, count=1000)
        variants = result.variants
        nr_of_variants = result.nr_of_variants
        for variant_obj in variants:
            assert variant_obj.max_freq <= 0.001
        
        assert nr_of_variants == 73

    def test_filters_cadd(self, case_obj):
        plugin = VcfPlugin()
        plugin.add_case(case_obj)
        case_id = case_obj.case_id

        filters = {'cadd':'20'}
        result = plugin.variants(case_id, filters=filters, count=1000)
        variants = result.variants
        nr_of_variants = result.nr_of_variants
        
        for variant_obj in variants:
            variant_obj.cadd_score >= 20
        
        assert nr_of_variants == 50

    def test_filters_impact_severities_high(self, case_obj):
        plugin = VcfPlugin()
        plugin.add_case(case_obj)
        case_id = case_obj.case_id

        filters = {'impact_severities':['HIGH']}
        result = plugin.variants(case_id, filters=filters, count=1000)
        variants = result.variants
        nr_of_variants = result.nr_of_variants
        
        for variant_obj in variants:
            assert variant_obj.impact_severity == 'HIGH'
        
        assert nr_of_variants == 7

    def test_filters_impact_severities_medium(self, case_obj):
        plugin = VcfPlugin()
        plugin.add_case(case_obj)
        case_id = case_obj.case_id

        filters = {'impact_severities':['MEDIUM']}
        result = plugin.variants(case_id, filters=filters, count=1000)
        variants = result.variants
        nr_of_variants = result.nr_of_variants
        
        for variant_obj in variants:
            assert variant_obj.impact_severity == 'MEDIUM'
        
        assert nr_of_variants == 82

    def test_filters_impact_severities_low(self, case_obj):
        plugin = VcfPlugin()
        plugin.add_case(case_obj)
        case_id = case_obj.case_id

        filters = {'impact_severities':['LOW']}
        result = plugin.variants(case_id, filters=filters, count=1000)
        variants = result.variants
        nr_of_variants = result.nr_of_variants
        
        for variant_obj in variants:
            assert variant_obj.impact_severity == 'LOW'
        
        assert nr_of_variants == 19

    def test_filters_impact_severities_high_and_med(self, case_obj):
        plugin = VcfPlugin()
        plugin.add_case(case_obj)
        case_id = case_obj.case_id

        filters = {'impact_severities':['HIGH', 'MEDIUM']}
        result = plugin.variants(case_id, filters=filters, count=1000)
        variants = result.variants
        nr_of_variants = result.nr_of_variants
        
        for variant_obj in variants:
            assert variant_obj.impact_severity in ['HIGH', 'MEDIUM']
        
        assert nr_of_variants == 89

    def test_filters_gene_ids(self, case_obj):
        plugin = VcfPlugin()
        plugin.add_case(case_obj)
        case_id = case_obj.case_id

        filters = {'gene_ids':['POF1B']}
        result = plugin.variants(case_id, filters=filters, count=1000)
        variants = result.variants
        nr_of_variants = result.nr_of_variants
        
        for variant_obj in variants:
            assert 'POF1B' in variant_obj.gene_symbols
        
        assert nr_of_variants == 1

    def test_filters_consequence(self, case_obj):
        plugin = VcfPlugin()
        plugin.add_case(case_obj)
        case_id = case_obj.case_id

        filters = {'consequence':['frameshift_variant']}
        result = plugin.variants(case_id, filters=filters, count=1000)
        variants = result.variants
        nr_of_variants = result.nr_of_variants
        
        for variant_obj in variants:
            assert 'frameshift_variant' in variant_obj.consequences
        
        assert nr_of_variants == 4

    def test_filters_range(self, case_obj, indexed_vcf_file):
        plugin = VcfPlugin()
        case_obj.variant_source = indexed_vcf_file
        case_obj.compressed = True
        case_obj.tabix_index = True
        
        plugin.add_case(case_obj)
        case_id = case_obj.case_id
        start = 1771120
        end = 1771130

        filters = {'range':{'chromosome':'1', 'start':start, 'end':end}}
        result = plugin.variants(case_id, filters=filters, count=1000)
        variants = result.variants
        nr_of_variants = result.nr_of_variants
        
        for variant_obj in variants:
            assert variant_obj.start >= start
            assert variant_obj.stop <= end
        
        assert nr_of_variants == 1
