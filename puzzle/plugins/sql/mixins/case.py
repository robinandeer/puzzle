# -*- coding: utf-8 -*-
import logging

from puzzle.plugins import BaseCaseMixin
from puzzle.models import Case as BaseCase, Individual as BaseIndividual
from puzzle.models.sql import Case, Individual

logger = logging.getLogger(__name__)


class CaseMixin(BaseCaseMixin):

    """Handle case related methods."""

    def add_case(self, case_obj, vtype='snv', mode='vcf', ped_svg=None):
        """Load a case with individuals.

        Args:
            case_obj (puzzle.models.Case): initialized case model
        """
        new_case = Case(case_id=case_obj.case_id,
                        name=case_obj.name,
                        variant_source=case_obj.variant_source,
                        variant_type=vtype,
                        variant_mode=mode,
                        pedigree=ped_svg,
                        compressed=case_obj.compressed,
                        tabix_index=case_obj.tabix_index)

        # build individuals
        inds = [Individual(
            ind_id=ind.ind_id,
            name=ind.name,
            mother=ind.mother,
            father=ind.father,
            sex=ind.sex,
            phenotype=ind.phenotype,
            ind_index=ind.ind_index,
            variant_source=ind.variant_source,
            bam_path=ind.bam_path,
        ) for ind in case_obj.individuals]
        new_case.individuals = inds
        
        if self.case(new_case.case_id):
            logger.warning("Case already exists in database!")
        else:
            self.session.add(new_case)
            self.save()
        return new_case

    def delete_case(self, case_obj):
        """Delete a case from the database

        Args:
            case_obj (puzzle.models.Case): initialized case model
        """
        for ind_obj in case_obj.individuals:
            self.delete_individual(ind_obj)
        logger.info("Deleting case {0} from database".format(case_obj.case_id))
        self.session.delete(case_obj)
        self.save()
        return case_obj

    def delete_individual(self, ind_obj):
        """Delete a case from the database

        Args:
            ind_obj (puzzle.models.Individual): initialized individual model
        """
        logger.info("Deleting individual {0} from database"
                    .format(ind_obj.ind_id))
        self.session.delete(ind_obj)
        self.save()
        return ind_obj

    def case(self, case_id):
        """Fetch a case from the database."""
        case_obj = self.query(Case).filter_by(case_id=case_id).first()
        return case_obj

    def individual(self, ind_id):
        """Fetch a case from the database."""
        ind_obj = self.query(Individual).filter_by(ind_id=ind_id).first()
        if ind_obj is None:
            ind_obj = BaseIndividual(ind_id='unknown')
        return ind_obj

    def cases(self):
        """Fetch all cases from the database."""
        return self.query(Case)

    def individuals(self, ind_ids=None):
        """Fetch all individuals from the database."""
        query = self.query(Individual)
        if ind_ids:
            query = query.filter(Individual.ind_id.in_(ind_ids))
        return query
