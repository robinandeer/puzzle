##TODO mock a gemini db
import pytest
from puzzle.plugins import GeminiPlugin

from sqlite3 import DatabaseError

def test_setup_no_db():
    """Test to initialize a gemini database without any file"""

    adapter = GeminiPlugin()
    assert adapter.db == None
    
    assert adapter.variant_type == 'snv'
    
    assert adapter.filters.can_filter_gene == True
    assert adapter.filters.can_filter_inheritance == False

def test_setup_with_db(gemini_path):
    """Test to initialize a gemini database without any file"""

    adapter = GeminiPlugin(db=gemini_path)
    assert adapter.db == gemini_path


def test_check_gemini_db(gemini_path, vcf_file):
    adapter = GeminiPlugin()
    adapter.db = gemini_path
    assert adapter.test_gemini_db()
    
    adapter.db = vcf_file
    with pytest.raises(DatabaseError):
        adapter.test_gemini_db()
