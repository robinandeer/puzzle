from puzzle.plugins import GeminiPlugin

from puzzle.models import DotDict

class TestFrequencies:
    
    def test_add_thousand_g(self, variant):
        adapter = GeminiPlugin()
        gemini_variant = {'aaf_1kg_all':0.01}
        adapter._add_thousand_g(variant, gemini_variant)
        
        assert variant.thousand_g == 0.01
        assert len(variant.frequencies) == 1

    def test_add_thousand_g_no_frequency(self, variant):
        adapter = GeminiPlugin()
        gemini_variant = {'aaf_1kg_all':None}
        adapter._add_thousand_g(variant, gemini_variant)
        
        assert variant.thousand_g == None
        assert len(variant.frequencies) == 0

    def test_add_exac(self, variant):
        adapter = GeminiPlugin()
        gemini_variant = {'aaf_exac_all':0.01}
        adapter._add_exac(variant, gemini_variant)
        
        assert variant.thousand_g == None
        assert len(variant.frequencies) == 1

    def test_add_exac_no_frequency(self, variant):
        adapter = GeminiPlugin()
        gemini_variant = {'aaf_exac_all':None}
        adapter._add_exac(variant, gemini_variant)
        
        assert len(variant.frequencies) == 0

    def test_add_gmaf(self, variant):
        adapter = GeminiPlugin()
        gemini_variant = {'max_aaf_all':0.01}
        adapter._add_gmaf(variant, gemini_variant)
        
        assert len(variant.frequencies) == 0
        assert variant.max_freq == 0.01

    def test_add_gmaf_no_frequency(self, variant):
        adapter = GeminiPlugin()
        gemini_variant = {'max_aaf_all':None}
        adapter._add_gmaf(variant, gemini_variant)
        
        assert len(variant.frequencies) == 0
        assert variant.max_freq == None

class TestGenotypes:
    
    def test_add_genotypes(self):
        """docstring for test_add_genotypes"""
        pass