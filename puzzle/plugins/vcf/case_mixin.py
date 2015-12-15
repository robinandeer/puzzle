import os
import logging

from path import path

from ped_parser import FamilyParser
from vcftoolbox import HeaderParser

from puzzle.models import (Case, Individual)


logger = logging.getLogger(__name__)

class CaseMixin(object):
    """Class to store methods that deal with Cases in vcf plugin"""

    def _insert_case(self, case, pedigree=None):
        """Insert a case into the puzzle database
        
            Args:
                case(Case)
        """
        case_table = self.puzzle_db['cases']
        logger.info("Inserting case {0} into databse".format(case['case_id']))
        if self.case(case_id=case['case_id']):
            logger.warning("Case already inserted!")
            return
        
        case_table.insert(dict(
            case_id=case['case_id'],
            name=case['name'],
            variant_source=case['variant_source'],
            pedigree=pedigree
            )
        )
        logger.debug("Case inserted")
        return

    def _insert_individual(self, individual):
        """Insert a case into the puzzle database
        
            Args:
                case(Case)
        """
        individual_table = self.puzzle_db['individuals']
        logger.info("Inserting individual {0} into databse".format(
            individual['ind_id']))
        
        individual_table.insert(dict(
            ind_id=individual['ind_id'],
            case_id=individual['case_id'],
            mother=individual['mother'],
            father=individual['father'],
            sex=individual['sex'],
            phenotype=individual['phenotype'],
            variant_source=individual['variant_source'],
            bam_path=individual['bam_path']
            )
        )
        logger.debug("Individual inserted")
    
    def load_case(self, case_lines, variant_source, case_type, bam_paths,
                    pedigree=None):
        """Load a case to the case database
        
            Args:
                lines (iterable(str)): iterable with individuals
                variant_soure (str): Path to vcf
                family_type (str): The family type
                bam_paths (dict): Dictionary with case_id as key and bam 
                                  path as value
        
        """
        if not self.puzzle_db:
            logger.error("Connect to database before loading case!")
            ##TODO raise proper exception
            raise SyntaxError
        
        case = self._get_case(
            variant_source=variant_source,
            case_lines=case_lines,
            case_type=case_type,
            bam_paths=bam_paths
        )
        
        self._insert_case(case, pedigree)
        
        for individual in case['individuals']:
            self._insert_individual(individual)
    
    
    def _get_case(self, variant_source, case_lines = None, case_type='ped',
                    bam_paths={}):
        """Create a cases and populate it with individuals
        
            Args:
                vcfs (str): Path to vcf files
            
            Returns:
                case_objs (list): List with Case objects
        """
        individuals = self._get_individuals(
            variant_source=variant_source,
            case_lines=case_lines,
            case_type=case_type,
            bam_paths=bam_paths
        )
        
        if case_lines:
            try:
                first_individual = individuals[0]
                case_id = first_individual['case_id']
            except IndexError:
                logger.error("No individuals found in pedigree file")
                ##TODO Raise pedigree error
                raise SyntaxError()
        else:
            case_id = os.path.basename(variant_source)
        
        case = self._get_case_object(
                    case_id=case_id,
                    variant_source=variant_source,
                    name=case_id
                )
        
        logger.debug("Found case with case_id: {0} and name: {1}".format(
            case['case_id'], case['name']))
        
        for individual in individuals:
            case.add_individual(individual)

        return case
        
    def _get_individuals(self, variant_source, case_lines=None, case_type='ped',
                            bam_paths={}):
        """Get the individuals from a vcf file
        
            Args:
                vcf (str): Path to a vcf
            
            Returns:
                individuals (generator): generator with Individuals
        """
        individuals = []
        if case_lines:
            #Read individuals from ped file
            family_parser = FamilyParser(case_lines, family_type=case_type)
            families = family_parser.families
            logger.info("Found families".format(
                            ','.join(list(families.keys()))))
            if len(families) != 1:
                logger.error("Only one family can be used with vcf adapter")
                raise IOError
            
            case_id = list(families.keys())[0]
            logger.info("Family used in analysis: {0}".format(case_id))
        
            for ind_id in family_parser.individuals:
                ind = family_parser.individuals[ind_id]
                logger.info("Found individual {0}".format(
                    ind.individual_id))
            
                individuals.append(self._get_individual_object(
                    ind_id=ind.individual_id,
                    case_id=case_id,
                    mother=ind.mother,
                    father=ind.father, 
                    sex=str(ind.sex), 
                    phenotype=str(ind.phenotype), 
                    bam_path=bam_paths.get(ind.individual_id)
                    )
                )
                
        else:
            #Read individuals from vcf file
            head = HeaderParser()
            with open(variant_source, 'r') as vcf_file:
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
                individuals.append(self._get_individual_object(
                    ind_id=ind,
                    case_id=os.path.basename(variant_source),
                    bam_path=bam_paths.get(ind)
                    )
                )
                
                logger.debug("Found individual {0} in {1}".format(
                    ind, variant_source))
        
        return individuals

    def _find_vcfs(self, pattern='*.vcf'):
        """Walk subdirectories and return VCF files."""
        return path(self.root_path).walkfiles(pattern)

    def cases(self, pattern=None):
        """Return all VCF file paths."""
        pattern = pattern or self.pattern
        case_objs = []
        if self.puzzle_db:
            result = []
            for case in self.puzzle_db['cases'].all():
                case_obj = self._get_case_object(
                    case_id=case['case_id'], 
                    variant_source=case['variant_source'], 
                    name=case['name']
                )
                logger.info("Fetching individuals from puzzle database")
                individuals = self.puzzle_db['individuals'].find(case_id=case['case_id'])
                for individual in individuals:
                    case_obj.add_individual(self._get_individual_object(
                        ind_id=individual['ind_id'], 
                        case_id=individual['case_id'], 
                        mother=individual['mother'], 
                        father=individual['father'], 
                        sex=individual['sex'], 
                        phenotype=individual['phenotype'], 
                        index=individual['ind_index'], 
                        bam_path=individual['bam_path']
                    ))
                case_objs.append(case_obj)

        elif self.case_obj:
            case_objs = [self.case_obj]
        
        else:
            # if pointing to a single file
            if os.path.isfile(self.root_path):
                vcfs = [path(self.root_path)]
            else:
                vcfs = self._find_vcfs(pattern)
        
            case_objs = (self._get_case(vcf) for vcf in vcfs)
        print(case_objs)
        return case_objs

    def case(self, case_id=None):
        """Return a Case object

            If no case_id is given return one case

            Args:
                case_id (str): A case id

            Returns:
                A Case object
        """
        cases = self.cases()

        if case_id:
            for case in cases:
                if case['case_id'] == case_id:
                    return case
        else:
            if cases:
                return list(cases)[0]

        return Case(case_id='unknown')
        