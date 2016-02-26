# -*- coding: utf-8 -*-
import logging

from puzzle.models.sql import Resource

logger = logging.getLogger(__name__)


class ResourceActions(object):
    def add_resource(self, name, file_path, ind_obj):
        """Link a resource to an individual."""
        new_resource = Resource(name=name, individual=ind_obj, path=file_path)
        self.session.add(new_resource)
        self.save()
        return new_resource

    def resource(self, resource_id):
        """Fetch a resource."""
        return self.query(Resource).get(resource_id)

    def delete_resource(self, resource_id):
        """Link a resource to an individual."""
        resource_obj = self.resource(resource_id)
        logger.debug("Deleting resource {0}".format(resource_obj.name))
        self.session.delete(resource_obj)
        self.save()
