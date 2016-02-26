# -*- coding: utf-8 -*-
import logging

from puzzle.models.sql import GeminiQuery

logger = logging.getLogger(__name__)


class GeminiActions(object):
    def gemini_query(self, name):
        """Return a gemini query

        Args:
            name (str)
        """
        logger.debug("Looking for query with name {0}".format(name))
        return self.query(GeminiQuery).get(name=name)

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

    def delete_gemini_query(self, name):
        """Delete a gemini query

        Args:
            name (str)
        """
        query_obj = self.gemini_query(name)
        logger.debug("Delete query with name {0}".format(name))
        self.session.delete(query_obj)
        self.save()
