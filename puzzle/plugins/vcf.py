# -*- coding: utf-8 -*-
from path import path
from vcf_parser import VCFParser


class Plugin(object):
    """docstring for Plugin"""
    def __init__(self, vcf_file=None):
        self.vcf_file = vcf_file

    def init_app(self, app):
        """Initialize plugin via Flask."""
        self.root_path = app.config['PUZZLE_ROOT']
        self.pattern = app.config['PUZZLE_PATTERN']

    def _find_vcfs(self, pattern=None):
        """Walk subdirectories and return VCF files."""
        pattern = pattern or self.pattern
        return path(self.root_path).walkfiles(pattern)

    def vcf_files(self, pattern=None):
        """Return all VCF file paths."""
        pattern = pattern or self.pattern
        return self._find_vcfs(pattern)

    def load_vcf(self, vcf_path):
        """Load a new VCF file."""
        self.vcf_file = vcf_path

    def _variants(self):
        variants = VCFParser(self.vcf_file, check_info=False)
        for index, variant in enumerate(variants):
            variant['id'] = index
            variant['index'] = index + 1
            variant['start'] = int(variant['POS'])
            variant['stop'] = int(variant['POS']) + (len(variant['REF'])
                                                     - len(variant['ALT']))
            yield variant

    def variants(self, skip=0, count=30, gene_list=None):
        """Return all variants in the VCF."""
        limit = count + skip
        if gene_list:
            filtered_variants = (variant for variant in self._variants()
                                 if gene_list in
                                 variant['info_dict']['Clinical_db_gene_annotation'])
        else:
            filtered_variants = self._variants()

        for variant in filtered_variants:
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
