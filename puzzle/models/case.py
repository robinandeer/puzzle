# -*- coding: utf-8 -*-


class Case(dict):
    """Case representation."""
    def __init__(self, case_id, name=None):
        super(Case, self).__init__(id=case_id, name=name or case_id)
