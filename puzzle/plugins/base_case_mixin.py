
class BaseCaseMixin(object):
    "Base plugin for caase mixins"
    
    def cases(self, pattern=None):
        """Return all cases."""
        raise NotImplementedError

    def case(self, case_id=None):
        """Return a case."""
        raise NotImplementedError

    def add_case(self, ind_id=None):
        """Return a individual."""
        raise NotImplementedError

    def individual(self, ind_id=None):
        """Return a individual."""
        raise NotImplementedError

    def individuals(self, ind_id=None):
        """Return a individual."""
        raise NotImplementedError

    