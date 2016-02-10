# -*- coding: utf-8 -*-
import os
import logging

from path import path

from puzzle.plugins import Plugin
from puzzle.models import DotDict
from puzzle.utils import get_case
from . import VariantMixin, CaseMixin

logger = logging.getLogger(__name__)


class VcfPlugin(VariantMixin, CaseMixin, Plugin):
    """docstring for Plugin"""

    def __init__(self, root_path=None, case_lines=None,
                 case_type=None, pattern='*.vcf', vtype='snv',
                 case_obj=None):
        """Initialize a vcf adapter.

            When instansiating all cases are found.

            Args:
                root_path(str) : Path to a vcf file or a dir with vcf files
                case_lines(Iterable) : Lines with ped like information
                case_type(str) : Format of pedigreeinformation
                patter(str) : What pattern to search for in directory
                vtype(str) : 'snv' or 'sv'
                case_obj(puzzle.models.case) : If initialized with a case
        """
        super(VcfPlugin, self).__init__()

        self.individuals = []
        self.case_objs = []
        logger.info("Updating root path to {0}".format(root_path))
        self.root_path = root_path

        self.check_setup(case_lines)

        self.variant_type = vtype
        logger.info("Setting variant type to {0}".format(vtype))

        self.pattern = pattern
        logger.debug("Updating pattern to {0}".format(pattern))

        if root_path:
            if os.path.isdir(root_path):
                logger.info("Looking for vcf files in {0}".format(root_path))
                for vcf_file in self._find_vcfs(pattern=pattern):
                    logger.info("Found vcf {0}".format(vcf_file))
                    case_obj = get_case(variant_source=vcf_file)
                    self.case_objs.append(case_obj)
            else:
                self.case_objs.append(get_case(
                    variant_source=self.root_path,
                    case_lines=case_lines,
                    case_type=case_type
                    )
                )

            for case_obj in self.case_objs:
                for ind in case_obj.individuals:
                    self.individuals.append(ind)

        self.filters = DotDict(
            can_filter_frequency=True,
            can_filter_cadd=True,
            can_filter_consequence=True,
            can_filter_gene=True,
            can_filter_inheritance=True,
            can_filter_sv=True,
            can_filter_impact_severity=True
            
        )

    def check_setup(self, case_lines):
        """Make some small tests to see if setup is correct"""
        valid_vcf_suffixes = ('.vcf', '.vcf.gz')
        if self.root_path:
            if case_lines:
                # If family file we only allow one vcf file as input
                if not os.path.isfile(self.root_path):
                    raise SyntaxError("Variant source has to be a vcf file when"\
                                     " running with family file")
            if os.path.isfile(self.root_path):
                if not self.root_path.endswith(valid_vcf_suffixes):
                    raise SyntaxError("Vcf file has to end with with .vcf or .vcf.gz")
        return


    def _find_vcfs(self, pattern='*.vcf'):
        """Walk subdirectories and return VCF files.

            Args:
                pattern (str): What pattern to serch for in filenames

            Return:
                paths (Iterable): The paths found
        """
        return path(self.root_path).walkfiles(pattern)

    def init_app(self, app):
        """Initialize plugin via Flask."""
        pass

