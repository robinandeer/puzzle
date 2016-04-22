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
    
    def test_add_genotypes(self, variant):
        adapter = GeminiPlugin()
        gemini_variant = {
            'gts': ['G/A', 'G/A', './.', './.', './.'],
            'gt_depths': [17, 19, -1, -1, -1],
            'gt_ref_depths': [10, 13, -1, -1, -1],
            'gt_alt_depths': [7, 6, -1, -1, -1],
            'gt_quals': [99, 99, -1, -1, -1],
            
        }
        ind = DotDict()
        ind.ind_index = 0
        ind.ind_id = '1'
        ind.phenotype = 2
        ind_objs = [ind]

        adapter._add_genotypes(variant, gemini_variant, 'dummy', ind_objs)
        
        genotype = variant.individuals[0]

        assert genotype.sample_id == ind.ind_id
        assert genotype.sample_id == ind.ind_id
        assert genotype.genotype == 'G/A'
        assert genotype.case_id == 'dummy'
        assert genotype.phenotype == ind.phenotype
        assert genotype.ref_depth == 10
        assert genotype.alt_depth == 7
        assert genotype.depth == 17
        assert genotype.genotype_quality == 99

class TestTranscripts:
    
    def test_add_transcripts(self, gemini_case_obj, variant):
        adapter = GeminiPlugin()
        adapter.add_case(gemini_case_obj)
        adapter.db = gemini_case_obj.variant_source
    
        gemini_variant = {'variant_id': 1}
        adapter._add_transcripts(variant, gemini_variant)
        
        transcripts = variant.transcripts
        
        assert len(transcripts) == 2

        first_transcript = transcripts[0]

        assert first_transcript.transcript_id == 'ENST00000370383'
        assert first_transcript.hgnc_symbol == 'EPHX4'
        assert first_transcript.consequence == 'missense_variant'
        assert first_transcript.ensembl_id == None
        assert first_transcript.biotype == 'protein_coding'
        assert first_transcript.sift == 'deleterious'
        assert first_transcript.polyphen == 'probably_damaging'
    