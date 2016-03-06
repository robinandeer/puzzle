import os
from puzzle.utils.ped import (get_individuals, get_case)

class TestGetIndividuals:
    
    def test_get_individuals_from_vcf(self, vcf_file):
        individuals = get_individuals(vcf=vcf_file)
        assert len(individuals) == 3
        ind_ids = set(['ADM1059A1','ADM1059A2','ADM1059A3'])
        assert ind_ids == set([ind.ind_id for ind in individuals])

    def test_get_individuals_from_compressed_vcf(self, compressed_vcf_file):
        individuals = get_individuals(vcf=compressed_vcf_file)
        assert len(individuals) == 3
        ind_ids = set(['ADM1059A1','ADM1059A2','ADM1059A3'])
        assert ind_ids == set([ind.ind_id for ind in individuals])
    
    def test_get_individuals_case_lines(self, ped_lines):
        individuals = get_individuals(case_lines=ped_lines)
        assert len(individuals) == 3
        ind_ids = set(['ADM1059A1','ADM1059A2','ADM1059A3'])
        assert ind_ids == set([ind.ind_id for ind in individuals])

class TestGetCase:
    
    def test_get_case_from_vcf(self, vcf_file):
        case_id = os.path.basename(vcf_file)
        case_obj = get_case(vcf_file)
        assert case_obj.case_id == case_id
        assert case_obj.compressed == False
        assert case_obj.tabix_index == False
        
        individuals = case_obj.individuals
        assert len(individuals) == 3
        ind_ids = set(['ADM1059A1','ADM1059A2','ADM1059A3'])
        assert ind_ids == set([ind.ind_id for ind in individuals])

    def test_get_case_from_compressed_vcf(self, compressed_vcf_file):
        case_id = os.path.basename(compressed_vcf_file)
        case_obj = get_case(compressed_vcf_file)
        assert case_obj.case_id == case_id
        assert case_obj.compressed == True
        assert case_obj.tabix_index == False
        
        individuals = case_obj.individuals
        assert len(individuals) == 3
        ind_ids = set(['ADM1059A1','ADM1059A2','ADM1059A3'])
        assert ind_ids == set([ind.ind_id for ind in individuals])

    def test_get_case_from_indexed_vcf(self, indexed_vcf_file):
        case_id = os.path.basename(indexed_vcf_file)
        case_obj = get_case(indexed_vcf_file)
        assert case_obj.case_id == case_id
        assert case_obj.compressed == True
        assert case_obj.tabix_index == True
        
        individuals = case_obj.individuals
        assert len(individuals) == 3
        ind_ids = set(['ADM1059A1','ADM1059A2','ADM1059A3'])
        assert ind_ids == set([ind.ind_id for ind in individuals])
    
    def test_get_case_from_ped(self, vcf_file, ped_lines):
        case_id = '636808'
        case_obj = get_case(vcf_file, case_lines=ped_lines)
        assert case_obj.case_id == case_id
        assert case_obj.compressed == False
        assert case_obj.tabix_index == False
        
        individuals = case_obj.individuals
        assert len(individuals) == 3
        ind_ids = set(['ADM1059A1','ADM1059A2','ADM1059A3'])
        assert ind_ids == set([ind.ind_id for ind in individuals])

    def test_get_case_from_ped_indexed_vcf(self, indexed_vcf_file, ped_lines):
        case_id = '636808'
        case_obj = get_case(indexed_vcf_file, case_lines=ped_lines)
        assert case_obj.case_id == case_id
        assert case_obj.compressed == True
        assert case_obj.tabix_index == True
        
        individuals = case_obj.individuals
        assert len(individuals) == 3
        ind_ids = set(['ADM1059A1','ADM1059A2','ADM1059A3'])
        assert ind_ids == set([ind.ind_id for ind in individuals])
    