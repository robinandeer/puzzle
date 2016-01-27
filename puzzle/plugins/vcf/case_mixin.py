# -*- coding: utf-8 -*-
import logging

from puzzle.models import Case


logger = logging.getLogger(__name__)


class CaseMixin(object):
    """Class to store methods that deal with Cases in vcf plugin"""

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
            if self.cases:
                return list(self.case_objs)[0]

        return Case(case_id='unknown')
