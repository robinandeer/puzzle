# -*- coding: utf-8 -*-
import itertools
import logging

from puzzle.plugins import BaseVariantMixin

logger = logging.getLogger(__name__)


class VariantMixin(BaseVariantMixin):
    def variants(self, case_id, skip=0, count=1000, filters=None):
        """Fetch variants for a case."""
        filters = filters or {}
        logger.debug("Fetching case with case_id: {0}".format(case_id))
        case_obj = self.case(case_id)
        plugin, case_id = self.select_plugin(case_obj)
        self.filters = plugin.filters

        gene_lists = (self.gene_list(list_id) for list_id
                      in filters.get('gene_lists', []))
        nested_geneids = (gene_list.gene_ids for gene_list in gene_lists)
        gene_ids = set(itertools.chain.from_iterable(nested_geneids))

        if filters.get('gene_ids'):
            filters['gene_ids'].extend(gene_ids)
        else:
            filters['gene_ids'] = gene_ids
        variants = plugin.variants(case_id, skip, count, filters)
        return variants

    def variant(self, case_id, variant_id):
        """Fetch a single variant from variant source."""
        case_obj = self.case(case_id)
        plugin, case_id = self.select_plugin(case_obj)
        variant = plugin.variant(case_id, variant_id)
        return variant
