# -*- coding: utf-8 -*-


class Case(dict):
    """Case representation."""
    def __init__(self, case_id, name=None):
        super(Case, self).__init__()
        self.id = case_id
        self.name = name or case_id
