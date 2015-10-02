# -*- coding: utf-8 -*-
from vcf_parser import VCFParser


class Plugin(object):
    """docstring for Plugin"""
    def __init__(self, vcf_file=None):
        self.vcf_file = vcf_file

    def init_app(self, app):
        """Initialize plugin via Flask."""
        self.vcf_file = app.config['PUZZLE_VCF_FILE']

    def _variants(self):
        variants = VCFParser(self.vcf_file, check_info=False)
        for index, variant in enumerate(variants):
            variant['id'] = index
            variant['index'] = index + 1
            yield variant

    def variants(self, skip=0, count=30):
        """Return all variants in the VCF."""
        limit = count + skip
        for variant in self._variants():
            if variant['index'] >= skip:
                if variant['index'] <= limit:
                    yield variant
                else:
                    break

    def variant(self, variant_id):
        """Return a specific variant."""
        for variant in self._variants():
            if variant['variant_id'] == variant_id:
                return variant
        return None
