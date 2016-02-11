##TODO mock a gemini db

from puzzle.plugins import GeminiPlugin

GEMINI_DB = "tests/fixtures/HapMapFew.db"


class MockApp(object):
    """Mock a flask app"""
    def __init__(self, db):
        super(MockApp, self).__init__()


class TestGeminiAdapter(object):
    """Setup and test a gemini adapter"""

    def setup(self):
        """docstring for setup"""

        self.adapter = GeminiPlugin(GEMINI_DB)

    def test_gemini_individuals(self):
        """docstring for test_gemini_individuals"""
        ind_ids = set([individual['ind_id']
                       for individual in self.adapter.individuals])
        assert ind_ids == set(['NA12877', 'NA12878', 'NA12882'])

    def test_gemini_cases(self):
        """docstring for test_gemini_individuals"""
        cases = set([case['name']
                    for case in self.adapter.cases()])
        assert cases == set(['643594'])

    def test_get_variants(self):
        """Test to get some variants from the gemini adapter"""
        variants = []
        for variant in self.adapter.variants('643594', count=5):
            variants.append(variant)

        assert len(variants) == 5

    def test_get_variant(self):
        """Test to get one variant"""
        variant = self.adapter.variant(
            case_id='643594',
            variant_id=4
        )

        assert variant['CHROM'] == '6'
        assert variant['POS'] == '32487163'
