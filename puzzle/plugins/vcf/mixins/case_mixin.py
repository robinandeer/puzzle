# -*- coding: utf-8 -*-
import logging

from puzzle.models import Case

from puzzle.plugins import BaseCaseMixin

logger = logging.getLogger(__name__)

class CaseMixin(BaseCaseMixin):
    """Class to store methods that deal with Cases in vcf plugin"""
    
    def _add_individual(self, ind_obj):
        """Add a individual to the adapter
        
            Args:
                ind_obj (puzzle.models.Individual)
        """
        logger.debug("Adding individual {0} to plugin".format(ind_obj.ind_id))
        self.individual_objs.append(ind_obj)

    def add_case(self, case_obj):
        """Add a case obj with individuals to adapter
        
            Args:
                case_obj (puzzle.models.Case)
                
        """
        for ind_obj in case_obj.individuals:
            self._add_individual(ind_obj)
        logger.debug("Adding case {0} to plugin".format(case_obj.case_id))
        self.case_objs.append(case_obj)
        if case_obj.tabix_index:
            logger.debug("Setting filters.can_filter_range to True")
            self.filters.can_filter_range = True
    
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
                if case.case_id == case_id:
                    return case
        else:
            if self.cases:
                return list(self.case_objs)[0]

        return Case(case_id='unknown')
    
    def individual(self, ind_id=None):
        """Return a individual object
        
            Args:
                ind_id (str): A individual id
            
            Returns:
                individual (puzzle.models.individual)
        """
        for ind_obj in self.individual_objs:
            if ind_obj.ind_id == ind_id:
                return ind_obj
        return None
    
    def individuals(self, ind_ids=None):
        """Return information about individuals
        
            Args:
                ind_ids (list(str)): List of individual ids
            
            Returns:
                individuals (Iterable): Iterable with Individuals
        """
        if ind_ids:
            for ind_id in ind_ids:
                for ind in self.individual_objs:
                    if ind.ind_id == ind_id:
                        yield ind
        else:
            for ind in self.individual_objs:
                yield ind
