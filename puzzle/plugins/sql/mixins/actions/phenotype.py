# -*- coding: utf-8 -*-
import logging

import phizz

from puzzle.utils import hpo_genes
from puzzle.models.sql import PhenotypeTerm

logger = logging.getLogger(__name__)


class PhenotypeActions(object):
    def add_phenotype(self, ind_obj, phenotype_id):
        """Add a phenotype term to the case."""
        if phenotype_id.startswith('HP:') or len(phenotype_id) == 7:
            logger.debug('querying on HPO term')
            hpo_results = phizz.query_hpo([phenotype_id])
        else:
            logger.debug('querying on OMIM term')
            hpo_results = phizz.query_disease([phenotype_id])

        added_terms = [] if hpo_results else None
        existing_ids = set(term.phenotype_id for term in ind_obj.phenotypes)
        for result in hpo_results:
            if result['hpo_term'] not in existing_ids:
                term = PhenotypeTerm(phenotype_id=result['hpo_term'],
                                     description=result['description'])
                logger.info('adding new HPO term: %s', term.phenotype_id)
                ind_obj.phenotypes.append(term)
                added_terms.append(term)

        logger.debug('storing new HPO terms')
        self.save()

        if added_terms is not None and len(added_terms) > 0:
            for case_obj in ind_obj.cases:
                self.update_hpolist(case_obj)

        return added_terms

    def update_hpolist(self, case_obj):
        """Update the HPO gene list for a case based on current terms."""
        hpo_list = self.case_genelist(case_obj)
        hpo_results = hpo_genes(case_obj.phenotype_ids(),
                                *self.phenomizer_auth)

        if hpo_results is None:
            pass
            # Why raise here?
            # raise RuntimeError("couldn't link to genes, try again")
        else:
            gene_ids = [result['gene_id'] for result in hpo_results
                        if result['gene_id']]
            hpo_list.gene_ids = gene_ids
            self.save()

    def remove_phenotype(self, ind_obj, phenotypes=None):
        """Remove multiple phenotypes from an individual."""
        if phenotypes is None:
            logger.info("delete all phenotypes related to %s", ind_obj.ind_id)
            self.query(PhenotypeTerm).filter_by(ind_id=ind_obj.id).delete()
        else:
            for term in ind_obj.phenotypes:
                if term.phenotype_id in phenotypes:
                    logger.info("delete phenotype: %s from %s",
                                term.phenotype_id, ind_obj.ind_id)
                    self.session.delete(term)
        logger.debug('persist removals')
        self.save()
        for case_obj in ind_obj.cases:
            self.update_hpolist(case_obj)
