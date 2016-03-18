# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import Column, types, ForeignKey
from sqlalchemy.orm import relationship

from .models import BASE


class Comment(BASE):

    """Represent a comment on case or variant level."""

    __tablename__ = "comment"

    id = Column(types.Integer, primary_key=True)
    text = Column(types.Text, nullable=False)
    username = Column(types.String(32), default='Anonymous')
    created_at = Column(types.DateTime, default=datetime.now)

    case_id = Column(types.Integer, ForeignKey('case.id'), nullable=False)
    case = relationship('Case', backref=('comments'))
    # md5 sum of chrom, pos, ref, alt
    variant_id = Column(types.String(32))

    def __repr__(self):
        return ("Comment(name={this.username}, text={this.text}"
                .format(this=self))
