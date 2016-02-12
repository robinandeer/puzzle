##TODO mock a gemini db
import pytest
from puzzle.plugins import GeminiPlugin

from sqlite3 import DatabaseError

class TestGeminiAdapter:
    """Setup and test a gemini adapter"""

    def test_setup_no_db(self):
        """Test to initialize a gemini database without any file"""

        adapter = GeminiPlugin()
        assert adapter.db == None
        
        assert adapter.variant_type == 'snv'
        
        assert adapter.filters.can_filter_gene == True
        assert adapter.filters.can_filter_inheritance == False

    def test_setup_with_db(self, gemini_path):
        """Test to initialize a gemini database without any file"""

        adapter = GeminiPlugin(db=gemini_path)
        assert adapter.db == gemini_path


    def test_check_gemini_db(self, gemini_path, vcf_file):
        """Test to initialize a gemini database without any file"""

        adapter = GeminiPlugin()
        adapter.db = gemini_path
        assert adapter.test_gemini_db()
        
        adapter.db = vcf_file
        with pytest.raises(DatabaseError):
            adapter.test_gemini_db()

    # def test_gemini_individuals(self):
    #     """docstring for test_gemini_individuals"""
    #     ind_ids = set([individual['ind_id']
    #                    for individual in self.adapter.individuals])
    #     assert ind_ids == set(['NA12877', 'NA12878', 'NA12882'])
    #
    # def test_gemini_cases(self):
    #     """docstring for test_gemini_individuals"""
    #     cases = set([case['name']
    #                 for case in self.adapter.cases()])
    #     assert cases == set(['643594'])
    #
    # def test_get_variants(self):
    #     """Test to get some variants from the gemini adapter"""
    #     variants = []
    #     for variant in self.adapter.variants('643594', count=5):
    #         variants.append(variant)
    #
    #     assert len(variants) == 5
    #
    # def test_get_variant(self):
    #     """Test to get one variant"""
    #     variant = self.adapter.variant(
    #         case_id='643594',
    #         variant_id=4
    #     )
    #
    #     assert variant['CHROM'] == '6'
    #     assert variant['POS'] == '32487163'
