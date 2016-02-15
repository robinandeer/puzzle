# -*- coding: utf-8 -*-
from puzzle.plugins import VcfPlugin

# TODO: define a vcf in the test
vcf = "tests/fixtures/hapmap.vcf"
family_file = "tests/fixtures/hapmap.ped"

individuals = [
    "636808	ADM1059A1	0	0	1	1",
    "636808	ADM1059A2	ADM1059A1	ADM1059A3	1	2",
    "636808	ADM1059A3	0	0	2	1"
]


class MockApp(object):
    """Mock a flask app"""
    def __init__(self, db=None, family=None, family_type='ped',
                 pattern='*.vcf', mode='snv'):
        super(MockApp, self).__init__()
        self.config = {'FAMILY_FILE': family, 'FAMILY_TYPE': family_type}


def test_variants():
    vcf_plugin = VcfPlugin(root_path=vcf)
    variants = vcf_plugin.variants("hapmap.vcf")
    variant = next(variants)
    assert variant['CHROM'] == 'X'
    assert int(variant['POS']) == 84563218
    assert variant['index'] == 1

    variant = next(variants)
    assert variant['CHROM'] == '2'
    assert int(variant['POS']) == 233349186
    assert variant['index'] == 2

def test_variants_case_no_ped():
    vcf_plugin = VcfPlugin(root_path=vcf)
    variants = vcf_plugin.variants(case_id='hapmap.vcf')
    variant = next(variants)
    assert variant['CHROM'] == 'X'
    assert int(variant['POS']) == 84563218
    assert variant['index'] == 1

    variant = next(variants)
    assert variant['CHROM'] == '2'
    assert int(variant['POS']) == 233349186
    assert variant['index'] == 2

def test_variants_case_with_ped():
    vcf_plugin = VcfPlugin(root_path=vcf, case_lines=individuals, case_type='ped')
    variants = vcf_plugin.variants(case_id='636808')
    variant = next(variants)
    assert variant['CHROM'] == 'X'
    assert int(variant['POS']) == 84563218
    assert variant['index'] == 1

    variant = next(variants)
    assert variant['CHROM'] == '2'
    assert int(variant['POS']) == 233349186
    assert variant['index'] == 2


def test_variant():
    vcf_plugin = VcfPlugin(root_path=vcf)
    variant = vcf_plugin.variant('hapmap.vcf', 'X_155239821_G_A')
    assert variant['CHROM'] == 'X'
    assert variant['POS'] == '155239821'

    # get 10th variant
    variant = vcf_plugin.variant('hapmap.vcf', '3_124998098_C_A')
    assert variant['index'] == 10

def test_ped_info():
    adapter=VcfPlugin(root_path=vcf, case_lines=individuals, case_type='ped')
    assert len(adapter.individuals) == 3
    case_obj = adapter.case_objs[0]
    assert case_obj.name == "636808"

def test_vcf_case():
    adapter=VcfPlugin(root_path=vcf)
    assert len(adapter.individuals) == 3
    case_obj = adapter.case_objs[0]
    assert case_obj['name'] == 'hapmap.vcf'

def test_vcf_case_dir():
    adapter=VcfPlugin(root_path="tests/fixtures/")
    assert len(adapter.case_objs) == 3

