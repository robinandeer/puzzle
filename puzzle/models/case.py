# -*- coding: utf-8 -*-
from .dotdict import DotDict


class Case(DotDict):
    """Case representation."""
    def __init__(self, case_id, name=None, variant_source=None,
                 variant_type='snv', variant_mode='vcf', compressed=False,
                 tabix_index=False):
        super(Case, self).__init__(
            case_id=case_id,
            name=name or case_id,
            variant_source=variant_source,
            variant_type=variant_type,
            variant_mode=variant_mode,
            compressed=compressed,
            tabix_index=tabix_index,
        )

        self['individuals'] = []

    def add_individual(self, individual):
        """Add a individual object to the case

            Args:
                individual (dict): An Individual object
        """
        self['individuals'].append(individual)
