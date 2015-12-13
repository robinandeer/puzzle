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
        self.config = {
            'PUZZLE_ROOT': db,
            'PUZZLE_PATTERN': pattern,
            'FAMILY_FILE': family,
            'FAMILY_TYPE': family_type,
            'PUZZLE_MODE': 'snv',
            }


def test_variants():
    vcf_plugin = VcfPlugin()
    variant = next(vcf_plugin.variants(vcf))
    assert variant['CHROM'] == 'X'
    assert variant['index'] == 1


def test_variant():
    vcf_plugin = VcfPlugin()
    variant = vcf_plugin.variant(vcf, 'X_155239821_G_A')
    assert variant['CHROM'] == 'X'
    assert variant['POS'] == '155239821'

    # get 10th variant
    variant = vcf_plugin.variant(vcf, '3_124998098_C_A')
    assert variant['index'] == 10

def test_ped_info():
    app = MockApp(vcf, individuals)
    adapter=VcfPlugin()
    adapter.init_app(app)
    assert len(adapter.individuals) == 3
    assert adapter.case_obj['name'] == "636808"
    print(adapter.case_obj)
    assert adapter.case_obj['id'] == vcf.replace('/', '|')
