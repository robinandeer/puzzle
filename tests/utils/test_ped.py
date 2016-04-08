import os
from puzzle.utils.ped import (get_individuals, get_cases)

class TestGetIndividuals:
    
    def test_get_individuals_from_vcf(self, vcf_file):
        individuals = get_individuals(variant_source=vcf_file)
        assert len(individuals) == 3
        ind_ids = set(['ADM1059A1','ADM1059A2','ADM1059A3'])
        assert ind_ids == set([ind.ind_id for ind in individuals])

    def test_get_individuals_from_compressed_vcf(self, compressed_vcf_file):
        individuals = get_individuals(variant_source=compressed_vcf_file)
        assert len(individuals) == 3
        ind_ids = set(['ADM1059A1','ADM1059A2','ADM1059A3'])
        assert ind_ids == set([ind.ind_id for ind in individuals])
    
    def test_get_individuals_case_lines(self, vcf_file, ped_lines):
        individuals = get_individuals(variant_source=vcf_file, case_lines=ped_lines)
        assert len(individuals) == 3
        ind_ids = set(['ADM1059A1','ADM1059A2','ADM1059A3'])
        assert ind_ids == set([ind.ind_id for ind in individuals])

    def test_get_individuals_gemini_database(self, gemini_path):
        individuals = get_individuals(variant_source=gemini_path, variant_mode='gemini')
        assert len(individuals) == 3
        ind_ids = set(['NA12878', 'NA12882','NA12877'])
        assert ind_ids == set([ind.ind_id for ind in individuals])

    def test_get_individuals_from_vcf_no_ind(self, vcf_file_no_ind):
        individuals = get_individuals(variant_source=vcf_file_no_ind)
        assert len(individuals) == 0


class TestGetCase:
    
    def test_get_case_from_vcf(self, vcf_file):
        case_id = os.path.basename(vcf_file)
        case_obj = get_cases(vcf_file)[0]
        assert case_obj.case_id == case_id
        assert case_obj.compressed == False
        assert case_obj.tabix_index == False
        
        individuals = case_obj.individuals
        assert len(individuals) == 3
        ind_ids = set(['ADM1059A1','ADM1059A2','ADM1059A3'])
        assert ind_ids == set([ind.ind_id for ind in individuals])

    def test_get_case_no_ind(self, vcf_file_no_ind):
        case_id = os.path.basename(vcf_file_no_ind)
        case_obj = get_cases(vcf_file_no_ind)[0]
        assert case_obj.case_id == case_id
        assert case_obj.compressed == False
        assert case_obj.tabix_index == False
        
        individuals = case_obj.individuals
        assert len(individuals) == 0

    def test_get_case_from_compressed_vcf(self, compressed_vcf_file):
        case_id = os.path.basename(compressed_vcf_file)
        case_obj = get_cases(compressed_vcf_file)[0]
        assert case_obj.case_id == case_id
        assert case_obj.compressed == True
        assert case_obj.tabix_index == False
        
        individuals = case_obj.individuals
        assert len(individuals) == 3
        ind_ids = set(['ADM1059A1','ADM1059A2','ADM1059A3'])
        assert ind_ids == set([ind.ind_id for ind in individuals])

    def test_get_case_from_indexed_vcf(self, indexed_vcf_file):
        case_id = os.path.basename(indexed_vcf_file)
        case_obj = get_cases(indexed_vcf_file)[0]
        assert case_obj.case_id == case_id
        assert case_obj.compressed == True
        assert case_obj.tabix_index == True
        
        individuals = case_obj.individuals
        assert len(individuals) == 3
        ind_ids = set(['ADM1059A1','ADM1059A2','ADM1059A3'])
        assert ind_ids == set([ind.ind_id for ind in individuals])
    
    def test_get_case_from_ped(self, vcf_file, ped_lines):
        case_id = '636808'
        case_obj = get_cases(vcf_file, case_lines=ped_lines)[0]
        assert case_obj.case_id == case_id
        assert case_obj.compressed == False
        assert case_obj.tabix_index == False
        
        individuals = case_obj.individuals
        assert len(individuals) == 3
        ind_ids = set(['ADM1059A1','ADM1059A2','ADM1059A3'])
        assert ind_ids == set([ind.ind_id for ind in individuals])

    def test_get_case_from_ped_indexed_vcf(self, indexed_vcf_file, ped_lines):
        case_id = '636808'
        case_obj = get_cases(indexed_vcf_file, case_lines=ped_lines)[0]
        assert case_obj.case_id == case_id
        assert case_obj.compressed == True
        assert case_obj.tabix_index == True
        
        individuals = case_obj.individuals
        assert len(individuals) == 3
        ind_ids = set(['ADM1059A1','ADM1059A2','ADM1059A3'])
        assert ind_ids == set([ind.ind_id for ind in individuals])
    
    def test_get_case_from_gemini(self, gemini_path):
        case_id = '643594'
        case_obj = get_cases(gemini_path, variant_mode='gemini')[0]
        assert case_obj.case_id == case_id
        assert case_obj.compressed == False
        assert case_obj.tabix_index == False
        
        individuals = case_obj.individuals
        assert len(individuals) == 3
        ind_ids = set(['NA12878', 'NA12882','NA12877'])
        assert ind_ids == set([ind.ind_id for ind in individuals])
    