# -*- coding: utf-8 -*-


class Plugin(object):
    """docstring for Plugin"""
    def __init__(self):
        super(Plugin, self).__init__()
        self.db = None
        self.individuals = None
        self.case_obj = None
        self.mode = 'sv'
    
    def init_app(self, app):
        """Initialize plugin via Flask."""
        self.root_path = app.config['PUZZLE_ROOT']
        self.pattern = app.config['PUZZLE_PATTERN']

    def cases(self, pattern=None):
        """Return all cases."""
        raise NotImplementedError

    def variants(self, case_id, skip=0, count=30, gene_list=None):
        """Return count variants for a case.

        """
        raise NotImplementedError

    def variant(self, variant_id):
        """Return a specific variant."""
        raise NotImplementedError
