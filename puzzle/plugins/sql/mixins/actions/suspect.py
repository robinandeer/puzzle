# -*- coding: utf-8 -*-
import logging

from puzzle.models.sql import Suspect

logger = logging.getLogger(__name__)


class SuspectActions(object):
    def add_suspect(self, case_obj, variant_obj):
        """Link a suspect to a case."""
        new_suspect = Suspect(case=case_obj, variant_id=variant_obj.variant_id,
                              name=variant_obj.display_name)
        self.session.add(new_suspect)
        self.save()
        return new_suspect

    def suspect(self, suspect_id):
        """Fetch a suspect."""
        return self.query(Suspect).get(suspect_id)

    def delete_suspect(self, suspect_id):
        """De-link a suspect from a case."""
        suspect_obj = self.suspect(suspect_id)
        logger.debug("Deleting suspect {0}".format(suspect_obj.name))
        self.session.delete(suspect_obj)
        self.save()
