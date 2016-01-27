# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import (Column, DateTime, Float, ForeignKey, Integer, String,
                        Table, UniqueConstraint)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

from puzzle.models.mixins import PedigreeHumanMixin

# base for declaring a mapping
BASE = declarative_base()


class Case(BASE):
    """
    This is the class for storing cases in the database.

    A case will be related to Individuals
    """
    __tablename__ = "case"
    id = Column(Integer, primary_key=True)
    case_id = Column(String(32), unique=True)
    name = Column(String(32)) # This is the display name
    variant_source = Column(String)
    variant_type = Column(String) # snv or sv
    variant_mode = Column(String) # vcf or gemini
    pedigree = Column(String) # For storing madeline info
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return("<Case({self.id}, {self.case_id}, {self.name}, {self.id},"\
                " {self.variant_source}, {self.variant_mode})>".format(self=self))

class Individual(BASE, PedigreeHumanMixin):
    """
    This is the class for storing individuals in the database.

    A Individual belongs to a case
    """
    __tablename__ = "individual"
    id = Column(Integer, primary_key=True)
    ind_id = Column(String(32))
    mother = Column(String(32))
    father = Column(String(32))
    sex = Column(String(32))
    phenotype = Column(String(32))
    ind_index = Column(Integer)
    variant_source = Column(String(32))
    bam_path = Column(String(32))
    case_id = Column(Integer, ForeignKey("case.id"))
    case = relationship(Case, backref=("individuals"))
