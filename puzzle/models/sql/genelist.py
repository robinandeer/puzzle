# -*- coding: utf-8 -*-
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .models import BASE


class CaseGenelistLink(BASE):

    """Link between case and gene list."""

    __tablename__ = 'case_genelist_link'

    case_id = Column(Integer, ForeignKey('case.id'), primary_key=True)
    genelist_id = Column(Integer, ForeignKey('gene_list.id', primary_key=True))


class GeneList(BASE):

    """Represent a list of gene identifiers."""

    __tablename__ = "gene_list"

    id = Column(Integer, primary_key=True)
    list_id = Column(String(32), nullable=False)
    # comma separated list of gene ids
    _gene_ids = Column(String(1024))

    cases = relationship('Case', secondary='case_genelist_link',
                         backref='gene_lists')

    @property
    def gene_ids(self):
        """Return a list of gene ids."""
        return self._gene_ids.split(',')

    @gene_ids.setter
    def gene_ids(self, value):
        self._gene_ids = ','.join(value)

    def __repr__(self):
        return "PhenotypeTerm(list_id={this.list_id})".format(this=self)
