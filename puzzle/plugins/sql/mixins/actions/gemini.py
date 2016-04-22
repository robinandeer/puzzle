# -*- coding: utf-8 -*-
import logging

from puzzle.models.sql import GeminiQuery

logger = logging.getLogger(__name__)


class GeminiActions(object):
    def gemini_query(self, query_id):
        """Return a gemini query

        Args:
            name (str)
        """
        logger.debug("Looking for query with id {0}".format(query_id))
        return self.query(GeminiQuery).filter_by(id=query_id).first()

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

    def delete_gemini_query(self, query_id):
        """Delete a gemini query

        Args:
            name (str)
        """
        query_obj = self.gemini_query(query_id)
        logger.debug("Delete query: {0}".format(query_obj.name_query))
        self.session.delete(query_obj)
        self.save()
