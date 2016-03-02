# -*- coding: utf-8 -*-
from puzzle.models.sql import GeneList, CaseGenelistLink


class GeneListActions(object):
    def gene_list(self, list_id):
        """Get a gene list from the database."""
        return self.query(GeneList).filter_by(list_id=list_id).first()

    def gene_lists(self):
        """Return all gene lists from the database."""
        return self.query(GeneList)

    def add_genelist(self, list_id, gene_ids, case_obj=None):
        """Create a new gene list and optionally link to cases."""
        new_genelist = GeneList(list_id=list_id)
        new_genelist.gene_ids = gene_ids
        if case_obj:
            new_genelist.cases.append(case_obj)

        self.session.add(new_genelist)
        self.save()
        return new_genelist

    def remove_genelist(self, list_id, case_obj=None):
        """Remove a gene list and links to cases."""
        gene_list = self.gene_list(list_id)

        if case_obj:
            # remove a single link between case and gene list
            case_ids = [case_obj.id]
        else:
            # remove all links and the list itself
            case_ids = [case.id for case in gene_list.cases]
            self.session.delete(gene_list)

        case_links = self.query(CaseGenelistLink).filter(
            CaseGenelistLink.case_id.in_(case_ids),
            CaseGenelistLink.genelist_id == gene_list.id
        )
        for case_link in case_links:
            self.session.delete(case_link)

        self.save()

    def case_genelist(self, case_obj):
        """Get or create a new case specific gene list record."""
        list_id = "{}-HPO".format(case_obj.case_id)
        gene_list = self.gene_list(list_id)

        if gene_list is None:
            gene_list = GeneList(list_id=list_id)
            case_obj.gene_lists.append(gene_list)
            self.session.add(gene_list)

        return gene_list
