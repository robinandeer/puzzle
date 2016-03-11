# -*- coding: utf-8 -*-
from puzzle.plugins import VcfPlugin


def test_variants_case(case_obj):
    vcf_plugin = VcfPlugin()
    vcf_plugin.add_case(case_obj)
    #case_id is 'hapmap.vcf' since no ped file is given
    variants = vcf_plugin.variants(case_id=case_obj.case_id)
    variant = next(variants)
    assert variant['CHROM'] == 'X'
    assert int(variant['POS']) == 84563218
    assert variant['index'] == 1

    variant = next(variants)
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
        variants = []
        for variant in plugin.variants(case_id, filters=filters, count=1000):
            variants.append(variant)
        assert len(variants) == 108

    def test_filters_frequency(self, case_obj):
        plugin = VcfPlugin()
        plugin.add_case(case_obj)
        case_id = case_obj.case_id

        filters = {'frequency':'0.001'}
        variants = []
        for variant in plugin.variants(case_id, filters=filters, count=1000):
            variants.append(variant)
        assert len(variants) == 88

    def test_filters_cadd(self, case_obj):
        plugin = VcfPlugin()
        plugin.add_case(case_obj)
        case_id = case_obj.case_id

        filters = {'cadd':'20'}
        variants = []
        for variant in plugin.variants(case_id, filters=filters, count=1000):
            variants.append(variant)
        assert len(variants) == 50

    def test_filters_impact_severities(self, case_obj):
        plugin = VcfPlugin()
        plugin.add_case(case_obj)
        case_id = case_obj.case_id

        filters = {'impact_severities':['HIGH']}
        variants = []
        for variant in plugin.variants(case_id, filters=filters, count=1000):
            variants.append(variant)
        assert len(variants) == 7

    def test_filters_gene_ids(self, case_obj):
        plugin = VcfPlugin()
        plugin.add_case(case_obj)
        case_id = case_obj.case_id

        filters = {'gene_ids':['POF1B']}
        variants = []
        for variant in plugin.variants(case_id, filters=filters, count=1000):
            variants.append(variant)
        assert len(variants) == 1

    def test_filters_consequence(self, case_obj):
        plugin = VcfPlugin()
        plugin.add_case(case_obj)
        case_id = case_obj.case_id

        filters = {'consequence':['frameshift_variant']}
        variants = []
        for variant in plugin.variants(case_id, filters=filters, count=1000):
            variants.append(variant)
        assert len(variants) == 4
