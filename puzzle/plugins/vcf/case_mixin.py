import os
import logging

from ped_parser import FamilyParser
from vcftoolbox import HeaderParser,get_vcf_handle

from puzzle.models import (Case, Individual)


logger = logging.getLogger(__name__)

class CaseMixin(object):
    """Class to store methods that deal with Cases in vcf plugin"""

    def _get_case(self, variant_source, case_lines = None, case_type='ped'):
        """Create a cases and populate it with individuals
            
            Args:
                variant_source (str): Path to vcf files
                case_lines (Iterable): Ped like lines
                case_type (str): Format of case lines
            
            Returns:
                case_objs (list): List with Case objects
        """
        individuals = self._get_individuals(
            vcf=variant_source,
            case_lines=case_lines,
            case_type=case_type,
        )
        
        for individual in individuals:
            self.individuals.append(individual)
            case_id = individual['case_id']
        
        case = Case(
                    case_id=case_id,
                    variant_source=variant_source,
                    name=case_id
                )
        
        logger.debug("Found case with case_id: {0} and name: {1}".format(
            case['case_id'], case['name']))
        
        for individual in individuals:
            case.add_individual(individual)
        
        return case

    def _get_individuals(self, vcf=None, case_lines=None, case_type='ped'):
        """Get the individuals from a vcf file, and/or a ped file.
        
            Args:
                vcf (str): Path to a vcf
                case_lines(Iterable): Ped like lines
                case_type(str): Format of ped lines 
            
            Returns:
                individuals (generator): generator with Individuals
        """
        individuals = []
        
        if case_lines:
            #Read individuals from ped file
            family_parser = FamilyParser(case_lines, family_type=case_type)
            families = family_parser.families
            logger.info("Found families {0}".format(
                            ','.join(list(families.keys()))))
            if len(families) != 1:
                logger.error("Only one family can be used with vcf adapter")
                raise IOError
            
            case_id = list(families.keys())[0]
            logger.info("Family used in analysis: {0}".format(case_id))
        
            for ind_id in family_parser.individuals:
                ind = family_parser.individuals[ind_id]
                logger.info("Found individual {0}".format(ind.individual_id))
                
                individual = Individual(
                    ind_id=ind.individual_id,
                    case_id=case_id,
                    mother=ind.mother,
                    father=ind.father, 
                    sex=str(ind.sex), 
                    phenotype=str(ind.phenotype),
                    variant_source=vcf,
                )
                individuals.append(individual)
        
        elif vcf:
            #Read individuals from vcf file
            case_id = os.path.basename(vcf)
            head = HeaderParser()
            handle = get_vcf_handle(infile=vcf)
            for line in handle:
                line = line.rstrip()
                if line.startswith('#'):
                    if line.startswith('##'):
                        head.parse_meta_data(line)
                    else:
                        head.parse_header_line(line)
                else:
                    break

            for index, ind in enumerate(head.individuals):
                #If we only have a vcf file we can not get metadata about the
                # individuals
                individual = Individual(
                    ind_id=ind,
                    case_id=case_id,
                    variant_source=vcf,
                )
                individuals.append(individual)
                
                logger.debug("Found individual {0} in {1}".format(
                    ind, vcf))
        
        return individuals

    def cases(self, pattern=None):
        """Cases found for the adapter."""
        
        return self.case_objs

    def case(self, case_id=None):
        """Return a Case object

            If no case_id is given return one case

            Args:
                case_id (str): A case id

            Returns:
                A Case object
        """
        if case_id:
            for case in self.case_objs:
                if case['case_id'] == case_id:
                    return case
        else:
            if cases:
                return list(self.case_objs)[0]

        return Case(case_id='unknown')
        