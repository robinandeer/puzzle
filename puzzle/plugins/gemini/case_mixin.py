import os
import logging

from gemini import GeminiQuery

from puzzle.models import (Case, Individual)

from puzzle.plugins import BaseCaseMixin


logger = logging.getLogger(__name__)

class CaseMixin(BaseCaseMixin):
    """Class to store methods that deal with Cases in geimni plugin"""

    def cases(self, pattern=None):
        """Return all cases.
        
            Args:
                pattern: Allways None in gemini adapter
            
            Returns:
                case_objs(An iterator with Cases)
        """

        return self.case_objs

    def case(self, case_id=None):
        """Return a Case object

            If no case_id is given return one case

            Args:
                case_id (str): A case id

            Returns:
                case(Case): A Case object
        """
        cases = self.cases()
        if case_id:
            for case in cases:
                if case.case_id == case_id:
                    return case
        else:
            if cases:
                return cases[0]

        return None

    def individual(self, ind_id=None):
        """Return a individual object
        
            Args:
                ind_id (str): A individual id
            
            Returns:
                individual (puzzle.models.individual)
        """
        for ind_obj in self.individuals:
            if ind_obj.ind_id == ind_id:
                return ind_obj
        return None

    def get_individuals(self, *ind_ids):
        """Return information about individuals
        
            Args:
                ind_ids (list(str)): List of individual ids
            
            Returns:
                individuals (Iterable): Iterable with Individuals
        """
        if ind_ids:
            for ind_id in ind_ids:
                for ind in self.individuals:
                    if ind.ind_id == ind_id:
                        yield ind
        else:
            for ind in self.individuals:
                yield ind

    
    def _get_cases(self, individuals):
        """Return the cases found in the database

            Args:
                individuals(list): List of Individuals

            Returns:
                case_objs(list): List of Cases
        """
        case_objs = []
        case_ids = set()
        logger.info("Looking for cases in {0}".format(
            self.db
        ))
        for individual in individuals:
            case_ids.add(individual.case_id)

        for case_id in case_ids:
            logger.info("Found case {0}".format(case_id))
            case = Case(
                case_id=case_id,
                name=case_id,
                variant_source=self.db,
                variant_type=self.variant_type,
                variant_mode='gemini',
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

    def _get_individuals(self):
        """Return a list with the individual objects found in db

            Returns:
                individuals (list): List of Individuals

        """
        individuals = []
        gq = GeminiQuery(self.db)
        #Dictionaru with sample to index in the gemini database
        sample_to_idx = gq.sample_to_idx

        query = "SELECT * from samples"
        gq.run(query)

        for individual in gq:
            logger.info("Found individual {0} with family id {1}".format(
                individual['name'], individual['family_id']))
            
            individuals.append(
                Individual(
                    ind_id=individual['name'],
                    case_id=individual['family_id'],
                    mother=individual['maternal_id'],
                    father=individual['paternal_id'],
                    sex=individual['sex'],
                    phenotype=individual['phenotype'],
                    ind_index=sample_to_idx.get(individual['name']),
                    variant_source=self.db,
                    bam_path=None)
            )
        return individuals
