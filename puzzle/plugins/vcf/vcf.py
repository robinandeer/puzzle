# -*- coding: utf-8 -*-
import os
import logging

from path import path
import dataset

from puzzle.plugins import Plugin
from . import VariantMixin, CaseMixin

logger = logging.getLogger(__name__)


class VcfPlugin(VariantMixin, CaseMixin, Plugin):
    """docstring for Plugin"""

    def __init__(self, root_path=None, case_lines=None,
        case_type=None, pattern='*.vcf', mode='snv'):
        """Initialize a vcf adapter.
        
            When instansiating all cases are found.
            
            Args:
                root_path(str) : Path to a vcf file or a dir with vcf files
                case_lines(Iterable) : Lines with ped like information
                case_type(str) : Format of pedigreeinformation
                patter(str) : What pattern to search for in directory
                mode(str) : 'snv' or 'sv'
        """
        super(VcfPlugin, self).__init__()
        
        self.individuals = []
        self.case_objs = []
        logger.debug("Updating root path to {0}".format(root_path))
        self.root_path = root_path
        
        self.mode = mode
        logger.info("Setting mode to {0}".format(self.mode))
        logger.debug("Updating pattern to {0}".format(pattern))
        self.pattern = pattern
        
        self.mode = mode
        logger.info("Using mode {0}".format(mode)) 
        
        if root_path:
            if os.path.isdir(root_path):
                logger.info("Looking for vcf files in {0}".format(root_path))
                for vcf_file in self._find_vcfs(pattern=pattern):
                    logger.info("Found vcf {0}".format(vcf_file))
                    self.case_objs.append(self._get_case(
                        variant_source=vcf_file
                    ))
            else:
                self.case_objs.append(self._get_case(
                    variant_source=self.root_path, 
                    case_lines=case_lines, 
                    case_type=case_type
                    )
                )
        
        logger.debug("Setting can_filter_gene to 'True'")
        self.can_filter_gene = True
        if self.mode == 'sv':
            logger.debug("Setting can_filter_sv to 'True'")
            self.can_filter_sv = True
            logger.debug("Setting can_filter_sv_len to 'True'")
            self.can_filter_sv_len = True
        else:
            logger.debug("Setting can_filter_frequency to 'True'")
            self.can_filter_frequency = True
            logger.debug("Setting can_filter_cadd to 'True'")
            self.can_filter_cadd = True
            logger.debug("Setting can_filter_consequence to 'True'")
            self.can_filter_consequence = True
            logger.debug("Setting can_filter_inheritance to 'True'")
            self.can_filter_inheritance = True
    
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


