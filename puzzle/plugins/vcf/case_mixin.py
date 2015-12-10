import os
import logging

from path import path

from ped_parser import FamilyParser
from vcftoolbox import HeaderParser

from puzzle.models import (Case, Individual)


logger = logging.getLogger(__name__)

class CaseMixin(object):
    """Class to store methods that deal with Cases in vcf plugin"""
    
    def load_case(self, case_lines=None, case_type='ped', bam_paths=None):
        """Load a case to the case database
        
            Args:
                lines (iterable(str)): iterable with individuals
                family_type (str): The family type
                bam_paths (dict): Dictionary with case_id as key and bam 
                                  path as value
        
        """
        if not self.puzzle_db:
            logger.error("Connect to database before loading case!")
            ##TODO raise proper exception
            raise SyntaxError
        
        case_table = self.puzzle_db['case']
        individuals = self._get_family_individuals(
            lines = case_lines,
            family_type = family_type
        )
        case = self._get_family_case(individuals)
    
    def _get_family_individuals(self, lines, family_type):
        """Get the individuals found in family file
        
            Args:
                lines (iterable(str)): iterable with individuals
                family_type (str): The family type
            Returns:
                individuals(list(Individual))
        """
        individuals = []
        family_parser = FamilyParser(lines, family_type)
        families = family_parser.families
        logger.info("Found families".format(
                        ','.join(list(families.keys()))))
        if len(families) != 1:
            logger.error("Only one family can be used with vcf adapter")
            raise IOError
        
        logger.info("Family used in analysis: {0}".format(
                        ','.join(list(families.keys()))))
        for ind_id in family_parser.individuals:
            individual_object = family_parser.individuals[ind_id]
            logger.info("Adding individual {0} to adapter".format(
                individual_object.individual_id))
            
            individuals.append(
                Individual(
                    ind_id=individual_object.individual_id,
                    case_id=individual_object.family,
                    mother=individual_object.mother,
                    father=individual_object.father,
                    sex=str(individual_object.sex),
                    phenotype=str(individual_object.phenotype),
                    variant_source=self.db,
                    bam_path=None)
            )
            
        logger.info("Individuals included in analysis: {0}".format(
                        ','.join(list(family_parser.individuals.keys()))))
        
        return individuals
        
    def _get_family_case(self, individuals):
        """Get a Case object from the family file info
        
            Args:
                individuals (list(Individual))
            
            Returns:
                case(Case)
        """
        first_individual = individuals[0]
        case_id = first_individual['case_id']
        case = Case(case_id=self.db, name=case_id)

        for individual in individuals:
            case.add_individual(individual)
        
        return case
    
    def _find_vcfs(self, pattern='*.vcf'):
        """Walk subdirectories and return VCF files."""
        return path(self.root_path).walkfiles(pattern)

    def _get_case(self, vcf):
        """Create a cases and populate it with individuals
        
            Args:
                vcfs (str): Path to vcf files
            
            Returns:
                case_objs (list): List with Case objects
        """
        internal_vcf = vcf.replace('/', '|')
        logger.debug("Looking for cases in {0}".format(internal_vcf))
        
        case = Case(case_id=internal_vcf,
                    name=vcf.basename())
        
        logger.debug("Found case with case_id: {0} and name: {1}".format(
            case['id'], case['name']))
        
        for individual in self._get_individuals(vcf):
            case.add_individual(individual)

        return case
        
    def _get_individuals(self, vcf):
        """Get the individuals from a vcf file
        
            Args:
                vcf (str): Path to a vcf
            
            Returns:
                individuals (generator): generator with Individuals
        """
        individuals = []
        head = HeaderParser()
        with open(vcf, 'r') as vcf_file:
            for line in vcf_file:
                line = line.rstrip()
                if line.startswith('#'):
                    if line.startswith('##'):
                        head.parse_meta_data(line)
                    else:
                        head.parse_header_line(line)
                else:
                    break
        
        for index, ind in enumerate(head.individuals):
            individual = Individual(
                        ind_id=ind, 
                        case_id=vcf.replace('/', '|'), 
                        index=index, 
                        variant_source=vcf)
            individuals.append(individual)
            logger.debug("Found individual {0} in {1}".format(
                individual['ind_id'], vcf))
        
        return individuals

    def cases(self, pattern=None):
        """Return all VCF file paths."""
        pattern = pattern or self.pattern
        
        if self.case_obj:
            case_objs = [self.case_obj]
        else:
            # if pointing to a single file
            if os.path.isfile(self.root_path):
                vcfs = [path(self.root_path)]
            else:
                vcfs = self._find_vcfs(pattern)
        
            case_objs = (self._get_case(vcf) for vcf in vcfs)
                    
        return case_objs

    def case(self, case_id=None):
        """Return a Case object

            If no case_id is given return one case

            Args:
                case_id (str): A case id

            Returns:
                A Case object
        """
        if self.case_obj:
            return self.case_obj
        
        cases = self.cases()

        if case_id:
            for case in cases:
                if case['case_id'] == case_id:
                    return case
        else:
            if cases:
                return list(cases)[0]

        return Case(case_id='unknown')
        