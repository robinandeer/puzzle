# -*- coding: utf-8 -*-
from sqlalchemy import (Column, Integer, String)

from .models import BASE


class GeminiQuery(BASE):

    """Represent a user defined gemini query."""

    __tablename__ = "gemini_query"

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False, unique=True)
    query = Column(String(128))

    @property
    def name_query(self):
        return self.name or self.query

    def __repr__(self):
        return ("GeminiQuery(name={this.name), query={this.query}"
                .format(this=self))
