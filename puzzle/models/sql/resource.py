# -*- coding: utf-8 -*-
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .models import BASE


class Resource(BASE):

    """Represent an external resource."""

    __tablename__ = "resource"

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False)
    path = Column(String(128), nullable=False)
    description = Column(String(128))

    ind_id = Column(Integer, ForeignKey('individual.id'))
    individual = relationship('Individual', backref=('resources'))

    def __repr__(self):
        return ("Resource(filename={this.filename})".format(this=self))
