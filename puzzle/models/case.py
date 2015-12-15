# -*- coding: utf-8 -*-


class Case(dict):
    """Case representation."""
    def __init__(self, case_id, name=None, variant_source=None):
        super(Case, self).__init__(case_id=case_id, name=name or case_id,
        variant_source=variant_source)
        self['individuals'] = []

    def add_individual(self, individual):
        """Add a individual object to the case

            Args:
                individual (dict): An Individual object
        """
        self['individuals'].append(individual)
