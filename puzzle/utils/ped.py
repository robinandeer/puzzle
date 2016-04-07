# -*- coding: utf-8 -*-
import logging
import os

from ped_parser import FamilyParser
from ped_parser.exceptions import PedigreeError

from puzzle.models import Case, Individual

try:
    from gemini import GeminiQuery
except ImportError:
    pass

from . import get_header

logger = logging.getLogger(__name__)


def get_cases(variant_source, case_lines=None, case_type='ped',
              variant_type='snv', variant_mode='vcf'):
        """Create a cases and populate it with individuals

            Args:
                variant_source (str): Path to vcf files
                case_lines (Iterable): Ped like lines
                case_type (str): Format of case lines

            Returns:
                case_objs (list(puzzle.models.Case))
        """
        individuals = get_individuals(
            variant_source=variant_source,
            case_lines=case_lines,
            case_type=case_type,
            variant_mode=variant_mode
        )
        case_objs = []
        case_ids = set()

        compressed = False
        tabix_index = False
        #If no individuals we still need to have a case id
        if variant_source.endswith('.gz'):
            logger.debug("Found compressed variant source")
            compressed = True
            tabix_file = '.'.join([variant_source, 'tbi'])
            if os.path.exists(tabix_file):
                logger.debug("Found index file")
                tabix_index = True

        if len(individuals) > 0:
            for individual in individuals:
                case_ids.add(individual.case_id)
        else:
            case_ids = [os.path.basename(variant_source)]

        for case_id in case_ids:
            logger.info("Found case {0}".format(case_id))
            case = Case(
                case_id=case_id,
                name=case_id,
                variant_source=variant_source,
                variant_type=variant_type,
                variant_mode=variant_mode,
                compressed=compressed,
                tabix_index=tabix_index
                )

            # Add the individuals to the correct case
            for individual in individuals:
                if individual.case_id == case_id:
                    logger.info("Adding ind {0} to case {1}".format(
                        individual.name, individual.case_id
                    ))
                    case.add_individual(individual)

            case_objs.append(case)

        return case_objs


def get_individuals(variant_source, case_lines=None, case_type='ped', variant_mode='vcf'):
        """Get the individuals from a vcf file, gemini database, and/or a ped file.

            Args:
                variant_source (str): Path to a variant source
                case_lines(Iterable): Ped like lines
                case_type(str): Format of ped lines

            Returns:
                individuals (generator): generator with Individuals
        """
        individuals = []
        ind_dict ={}

        if variant_mode == 'vcf':
            head = get_header(variant_source)
            #Dictionary with ind_id:index where index show where in vcf ind info is

            for index, ind in enumerate(head.individuals):
                ind_dict[ind] = index

            if case_lines:
                # read individuals from ped file
                family_parser = FamilyParser(case_lines, family_type=case_type)
                families = family_parser.families
                logger.debug("Found families {0}".format(
                            ','.join(list(families.keys()))))
                if len(families) != 1:
                    logger.error("Only one family can be used with vcf adapter")
                    raise IOError

                case_id = list(families.keys())[0]
                logger.debug("Family used in analysis: {0}".format(case_id))

                for ind_id in family_parser.individuals:
                    ind = family_parser.individuals[ind_id]
                    logger.info("Found individual {0}".format(ind.individual_id))
                    try:
                        individual = Individual(
                            ind_id=ind_id,
                            case_id=case_id,
                            mother=ind.mother,
                            father=ind.father,
                            sex=str(ind.sex),
                            phenotype=str(ind.phenotype),
                            variant_source=variant_source,
                            ind_index=ind_dict[ind_id],
                            )
                        individuals.append(individual)
                    except KeyError as err:
                        #This is the case when individuals in ped does not exist
                        #in vcf
                        raise PedigreeError(
                            family_id=case_id,
                            individual_id=ind_id,
                            message="Individual {0} exists in ped file but not in vcf".format(ind_id)
                            )

            else:
                case_id = os.path.basename(variant_source)

                for ind in ind_dict:
                    individual = Individual(
                        ind_id=ind,
                        case_id=case_id,
                        variant_source=variant_source,
                        ind_index=ind_dict[ind]
                        )
                    individuals.append(individual)

                    logger.debug("Found individual {0} in {1}".format(
                                 ind, variant_source))
        elif variant_mode == 'gemini':
            gq = GeminiQuery(variant_source)
            #Dictionaru with sample to index in the gemini database
            ind_dict = gq.sample_to_idx
            query = "SELECT * from samples"
            gq.run(query)
            for individual in gq:
                logger.debug("Found individual {0} with family id {1}".format(
                    individual['name'], individual['family_id']))
                individuals.append(
                    Individual(
                        ind_id=individual['name'],
                        case_id=individual['family_id'],
                        mother=individual['maternal_id'],
                        father=individual['paternal_id'],
                        sex=individual['sex'],
                        phenotype=individual['phenotype'],
                        ind_index=ind_dict.get(individual['name']),
                        variant_source=variant_source,
                        bam_path=None)
                        )

        return individuals
