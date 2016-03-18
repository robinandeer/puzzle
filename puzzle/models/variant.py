# -*- coding: utf-8 -*-
import logging
import hashlib
from . import (DotDict, Transcript, Gene, Compound, Genotype)

logger = logging.getLogger(__name__)


class Variant(DotDict):
    """docstring for Variant"""
    def __init__(self, CHROM, POS, ID, REF, ALT, QUAL, FILTER):
        super(Variant, self).__init__(CHROM=CHROM, POS=POS, ID=ID, REF=REF,
                                      ALT=ALT, QUAL=QUAL, FILTER=FILTER)

        self._set_variant_id()
        self['index'] = None

        self['thousand_g'] = None  # float
        self['max_freq'] = None  # float
        self['cadd_score'] = None  # float
        self['consequences'] = []
        self['most_severe_consequence'] = None  # str
        self['impact_severities'] = []  # List of severities
        self['rank_score'] = None  # float

        self['frequencies'] = []
        self['severities'] = []
        self['transcripts'] = []  # List of Transcripts
        self['individuals'] = []  # List of Genotypes
        self['genes'] = []  # List of Genes
        self['gene_symbols'] = []  # List of gene symbols
        self['compounds'] = []  # List of Compounds
        self['genetic_models'] = []  # List of genetic models followed
        #SV specific fields:
        self['sv_type'] = None
        self['sv_len'] = None
        self['stop_chrom'] = None
        self['stop'] = None
        self['cytoband_start'] = None
        self['cytoband_stop'] = None
        self['consequences'] = []

    @property
    def nr_genes(self):
        """Return the number of genes"""
        if self['genes']:
            nr_genes = len(self['genes'])
        else:
            nr_genes = len(self['gene_symbols'])
        return nr_genes

    @property
    def is_snv(self):
        """Check if variant is SNV or SV."""
        return self.get('cytoband_start') is None

    @property
    def display_name(self):
        """Readable name for the variant."""
        if self.is_snv:
            gene_ids = self.gene_symbols[:2]
            return ', '.join(gene_ids)
        else:
            return "{this.cytoband_start} ({this.sv_len})".format(this=self)

    @property
    def md5(self):
        """Return a md5 key string based on position, ref and alt"""
        return hashlib.md5('_'.join([self.CHROM, str(self.POS), self.REF,
                                     self.ALT])).hexdigest()

    @property
    def is_intrachromosomal(self):
        """Check if variant is intrachromosomal

            If stop_chrom == CHROM return True
            else return False
        """
        return self.get('stop_chrom', self['CHROM']) == self['CHROM']

    def add_frequency(self, name, value):
        """Add a frequency that will be displayed on the variant level

            Args:
                name (str): The name of the frequency field
        """
        logger.debug("Adding frequency {0} with value {1} to variant {2}".format(
            name, value, self['variant_id']))
        self['frequencies'].append({'label': name, 'value': value})

    def set_max_freq(self, max_freq=None):
        """Set the max frequency for the variant

            If max_freq use this, otherwise go through all frequencies and
            set the highest as self['max_freq']

            Args:
                max_freq (float): The max frequency
        """
        if max_freq:
            self['max_freq'] = max_freq
        else:
            for frequency in self['frequencies']:
                if self['max_freq']:
                    if frequency['value'] > self['max_freq']:
                        self['max_freq'] = frequency['value']
                else:
                    self['max_freq'] = frequency['value']
        return

    def add_severity(self, name, value):
        """Add a severity to the variant

            Args:
                name (str): The name of the severity
                value : The value of the severity
        """
        logger.debug("Adding severity {0} with value {1} to variant {2}".format(
            name, value, self['variant_id']))
        self['severities'].append({name: value})

    def add_individual(self, genotype):
        """Add the information for a individual

            This adds a genotype dict to variant['individuals']

            Args:
                genotype (dict): A genotype dictionary
        """
        logger.debug("Adding genotype {0} to variant {1}".format(
            genotype, self['variant_id']))
        self['individuals'].append(genotype)

    def add_transcript(self, transcript):
        """Add the information transcript

            This adds a transcript dict to variant['transcripts']

            Args:
                transcript (dict): A transcript dictionary
        """
        logger.debug("Adding transcript {0} to variant {1}".format(
            transcript, self['variant_id']))
        self['transcripts'].append(transcript)

    def add_gene(self, gene):
        """Add the information of a gene

            This adds a gene dict to variant['genes']

            Args:
                gene (dict): A gene dictionary

        """
        logger.debug("Adding gene {0} to variant {1}".format(
            gene, self['variant_id']))
        self['genes'].append(gene)

    def add_compound(self, compound):
        """Add the information of a compound variant

            This adds a compound dict to variant['compounds']

            Args:
                compound (dict): A compound dictionary

        """
        logger.debug("Adding compound {0} to variant {1}".format(
            compound, self['variant_id']))
        self['compounds'].append(compound)

    def update_variant_id(self, variant_id):
        """Update the variant id for an individual

            Args:
                variant_id (str): A variant id
        """

        self._set_variant_id(variant_id=variant_id)

    def _set_variant_id(self, variant_id=None):
        """Set the variant id for this variant"""
        if not variant_id:
            variant_id = '_'.join([
                self.CHROM,
                str(self.POS),
                self.REF,
                self.ALT
                ])

        logger.debug("Updating variant id to {0}".format(
            variant_id))

        self['variant_id'] = variant_id

    def __repr__(self):
        return ("Variant(CHROM={this.CHROM},POS={this.POS},REF={this.REF},ALT={this.ALT})"
                        .format(this=self))
