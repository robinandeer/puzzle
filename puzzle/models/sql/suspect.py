# -*- coding: utf-8 -*-
from sqlalchemy import (Column, ForeignKey, Integer, String, UniqueConstraint,
                        Text)
from sqlalchemy.orm import relationship

from .models import BASE


class Suspect(BASE):

    """Represent a list of suspect variants."""

    __tablename__ = "suspect"
    __table_args__ = (UniqueConstraint('case_id', 'variant_id',
                                       name='_case_variant_uc'),)

    id = Column(Integer, primary_key=True)
    variant_id = Column(Text, nullable=False)
    name = Column(String(128))

    case_id = Column(Integer, ForeignKey('case.id'), nullable=False)
    case = relationship('Case', backref=('suspects'))

    def __repr__(self):
        return ("Suspect(case_id={this.case_id} variant_id={this.variant_id})"
                .format(this=self))
