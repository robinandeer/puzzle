# -*- coding: utf-8 -*-
from path import path

from puzzle.models import Variant

from vcftoolbox import (get_variant_dict, HeaderParser, get_info_dict)


class Plugin(object):
    """docstring for Plugin"""
    def __init__(self, vcf_file=None):
        self.vcf_file = vcf_file

    def init_app(self, app):
        """Initialize plugin via Flask."""
        self.root_path = app.config['PUZZLE_ROOT']
        self.pattern = app.config['PUZZLE_PATTERN']

    def _find_vcfs(self, pattern = '*.vcf'):
        """Walk subdirectories and return VCF files."""
        return path(self.root_path).walkfiles(pattern)

    def cases(self, pattern=None):
        """Return all VCF file paths."""
        pattern = pattern or self.pattern
        return self._find_vcfs(pattern)

    def _variants(self, vcf_file_path):
        head = HeaderParser()
        #Parse the header
        with open(vcf_file_path, 'r') as variant_file:
            for line in variant_file:
                line = line.rstrip()
                if line.startswith('#'):
                    if line.startswith('##'):
                        head.parse_meta_data(line)
                    else:
                        head.parse_header_line(line)
                else:
                    break
        
        header_line = head.header
        if len(header_line) > 8:
            variant_columns = header_line[:9]
        else:
            variant_columns = header_line[:8]
        
        print(header.info_dict)
        sys.exit()
        
        with open(vcf_file_path, 'r') as vcf_file:
            index = 0
            for variant_line in vcf_file:
                if not variant_line.startswith('#'):
                    index += 1
                    variant_dict =  get_variant_dict(
                        variant_line = variant_line,
                        header_line = header_line
                    )
                    variant_dict['info_dict'] = get_info_dict(variant_dict['INFO'])
                    variant_dict['vep_dict'] = get_vep_dict(
                        vep_string = variant_dict['info_dict'].get('CSQ', '')
                    )
                    variant = Variant(
                        **{column: variant_dict[column] for column in variant_columns}
                        )
                    print(variant)
        #
        # for index, variant in enumerate(variants):
        #     variant['id'] = index
        #     variant['index'] = index + 1
        #     variant['start'] = int(variant['POS'])
        #     variant['stop'] = int(variant['POS']) + (len(variant['REF'])
        #                                              - len(variant['ALT']))
        #     yield variant

    def variants(self, case_id, skip=0, count=30, gene_list=None):
        """Return all variants in the VCF."""
        
        limit = count + skip
        if gene_list:
            filtered_variants = (variant for variant in self._variants(case_id)
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


if __name__ == '__main__':
    vcf_file = "tests/fixtures/15031.vcf"
    plugin = Plugin()
    plugin._variants(vcf_file)
    print("hej")