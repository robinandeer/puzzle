# -*- coding: utf-8 -*-
from puzzle.models.sql import GeneList


def test_delete_gene():
    gene_list = GeneList(list_id='my cool list')
    assert gene_list.list_id == 'my cool list'
    assert gene_list.gene_ids == []

    gene_ids = ['ADK', 'SKD', 'EGFR']
    gene_list.gene_ids = gene_ids
    assert gene_list._gene_ids == ','.join(gene_ids)

    # remove one gene
    gene_list.delete_gene('ADK')
    assert gene_list.gene_ids == gene_ids[1:]

    # remove multiple genes
    gene_list.delete_gene('SKD', 'EGFR')
    assert gene_list.gene_ids == []
