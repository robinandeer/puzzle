# -*- coding: utf-8 -*-


class PedigreeHumanMixin(object):
    @property
    def sex_human(self):
        """Return a human readable string for the sex."""
        sex_string = self.sex
        if sex_string == '1':
            return 'male'
        elif sex_string == '2':
            return 'female'
        else:
            return 'unknown'

    @property
    def is_affected(self):
        """Boolean for telling if the sample is affected."""
        phenotype = self.phenotype
        if phenotype == '1':
            return False
        elif phenotype == '2':
            return True
        else:
            return False
