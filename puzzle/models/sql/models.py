# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
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

    @property
    def resources(self):
        """Return resources for all individuals."""
        for individual in self.individuals:
            for resource in individual.resources:
                yield resource

    @property
    def phenotypes(self):
        """Return all phenotypes for included individuals."""
        for individual in self.individuals:
            for term in individual.phenotypes:
                yield term

    def phenotype_ids(self):
        """Return only phenotype ids for included individuals."""
        return [term.phenotype_id for term in self.phenotypes]

    def __repr__(self):
        return("<Case(id:{self.id}, case_id:{self.case_id}, name:{self.name},"\
                " variant_source:{self.variant_source}, variant_type:"\
                "{self.variant_type}, variant_mode:{self.variant_mode})>".format(self=self))


class Individual(BASE, PedigreeHumanMixin):
    """
    This is the class for storing individuals in the database.

    A Individual belongs to a case
    """
    __tablename__ = "individual"
    id = Column(Integer, primary_key=True)
    ind_id = Column(String(32))
    name = Column(String(32))
    mother = Column(String(32))
    father = Column(String(32))
    sex = Column(String(32))
    phenotype = Column(String(32))
    ind_index = Column(Integer)
    variant_source = Column(String(32))
    bam_path = Column(String(32))
    case_id = Column(Integer, ForeignKey("case.id"))
    case = relationship(Case, backref=("individuals"))

    @property
    def case_name(self):
        """Fetch display name of case."""
        return self.case.name

    def __repr__(self):
        return("<Individual(id:{self.id}, ind_id:{self.ind_id}, mother:{self.mother},"\
                " father{self.father}, sex:{self.sex}, phenotype.{self.phenotype}"\
                ", ind_index:{self.ind_index}, variant_source:"\
                "{self.variant_source}, case_id:{self.case_id})>".format(self=self))
