# -*- coding: utf-8 -*-
import logging

from puzzle.models.sql import Comment

logger = logging.getLogger(__name__)


class GeminiActions(object):
    def comments(self, case_id, variant_id=None):
        """Return comments for a case or variant.

        Args:
            case_id (str): id for a related case
            variant_id (Optional[str]): id for a related variant
        """
        logger.debug("Looking for comments")
        comment_objs = self.query(Comment).filter_by(case_id=case_id)

        if variant_id:
            comment_objs = comment_objs.filter_by(variant_id=variant_id)
        elif:
            comment_objs = comment_objs.filter_by(variant_id == None)

        return self.query(GeminiQuery).filter_by(name=name).first()

    def gemini_queries(self):
        """Return all gemini queries"""
        return self.query(GeminiQuery)

    def add_gemini_query(self, name, query):
        """Add a user defined gemini query

        Args:
            name (str)
            query (str)
        """
        logger.info("Adding query {0} with text {1}".format(name, query))
        new_query = GeminiQuery(name=name, query=query)
        self.session.add(new_query)
        self.save()
        return new_query

    def delete_gemini_query(self, name):
        """Delete a gemini query

        Args:
            name (str)
        """
        query_obj = self.gemini_query(name)
        logger.debug("Delete query with name {0}".format(name))
        self.session.delete(query_obj)
        self.save()
