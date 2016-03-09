# -*- coding: utf-8 -*-
from puzzle.plugins import VcfPlugin


def test_variants_case_no_ped(vcf_file):
    vcf_plugin = VcfPlugin(root_path=vcf_file)
    #case_id is 'hapmap.vcf' since no ped file is given
    variants = vcf_plugin.variants(case_id='hapmap.vcf')
    variant = next(variants)
    assert variant['CHROM'] == 'X'
    assert int(variant['POS']) == 84563218
    assert variant['index'] == 1

    variant = next(variants)
    assert variant['CHROM'] == '2'
    assert int(variant['POS']) == 233349186
    assert variant['index'] == 2

def test_variants_case_with_ped(vcf_file, ped_lines):
    vcf_plugin = VcfPlugin(root_path=vcf_file, case_lines=ped_lines, case_type='ped')
    variants = vcf_plugin.variants(case_id='636808')
    variant = next(variants)
    assert variant['CHROM'] == 'X'
    assert int(variant['POS']) == 84563218
    assert variant['index'] == 1

    variant = next(variants)
    assert variant['CHROM'] == '2'
    assert int(variant['POS']) == 233349186
    assert variant['index'] == 2


def test_variant(vcf_file):
    vcf_plugin = VcfPlugin(root_path=vcf_file)
    variant = vcf_plugin.variant('hapmap.vcf', 'X_155239821_G_A')
    assert variant['CHROM'] == 'X'
    assert int(variant['POS']) == 155239821

    # get 10th variant
    variant = vcf_plugin.variant('hapmap.vcf', '3_124998098_C_A')
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
