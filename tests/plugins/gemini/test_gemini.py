##TODO mock a gemini db
import pytest
from puzzle.plugins import GeminiPlugin

from sqlite3 import DatabaseError

class TestInitGeminiAdapter:
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

class TestCaseMixin:
    """Test the functionality for the case mixin"""
    
    def test_get_individuals(self, gemini_path):
        adapter = GeminiPlugin(db=gemini_path)
        
        ind_ids = [ind.ind_id for ind in adapter.get_individuals()]
        assert set(ind_ids) == set(['NA12877', 'NA12878', 'NA12882'])

    def test_get_individuals_one_ind(self, gemini_path):
        adapter = GeminiPlugin(db=gemini_path)
        
        ind_ids = [ind.ind_id for ind in adapter.get_individuals('NA12877')]
        assert set(ind_ids) == set(['NA12877'])

    def test_get_individuals_two_inds(self, gemini_path):
        adapter = GeminiPlugin(db=gemini_path)
        
        ind_ids = [ind.ind_id for ind in adapter.get_individuals('NA12877', 'NA12878')]
        assert set(ind_ids) == set(['NA12877', 'NA12878'])

    def test__get_individuals(self, gemini_path):
        adapter = GeminiPlugin(db=gemini_path)
        
        ind_ids = [ind.ind_id for ind in adapter._get_individuals()]
        assert set(ind_ids) == set(['NA12877', 'NA12878', 'NA12882'])

    def test__get_cases(self, gemini_path):
        adapter = GeminiPlugin(db=gemini_path)
        
        individuals = adapter._get_individuals()
        case_ids = [case.case_id for case in adapter._get_cases(individuals)]
        assert set(case_ids) == set(['643594'])

    def test_cases(self, gemini_path):
        adapter = GeminiPlugin(db=gemini_path)
        
        case_ids = [case.case_id for case in adapter.cases()]
        assert set(case_ids) == set(['643594'])

    def test_case(self, gemini_path):
        adapter = GeminiPlugin(db=gemini_path)
        
        case_id = '643594'
        assert adapter.case(case_id).case_id == case_id

    def test_case_no_id(self, gemini_path):
        adapter = GeminiPlugin(db=gemini_path)
        
        case_id = '643594'
        assert adapter.case().case_id == case_id

    def test_case_wrong_id(self, gemini_path):
        adapter = GeminiPlugin(db=gemini_path)
        
        case_id = 'hello'
        assert adapter.case(case_id) == None

class TestVariantMixin:
    """Test the functionalty for the variant mixin"""
    
    def test_get_variants(self, gemini_path):
        """Test to get some variants from the gemini adapter"""
        adapter = GeminiPlugin(db=gemini_path)
        variants = []
        for variant in adapter.variants('643594', count=5):
            variants.append(variant)

        assert len(variants) == 5

    def test_variant(self, gemini_path):
        """Test to get one variant"""
        adapter = GeminiPlugin(db=gemini_path)
        variant = adapter.variant(
            case_id='643594',
            variant_id=4
        )

        assert variant['CHROM'] == '6'
        assert variant['POS'] == '32487163'
