# -*- coding: utf-8 -*-
import logging

from .mixins import PedigreeHumanMixin

logger = logging.getLogger(__name__)


class Transcript(dict):
    """Class that holds information about a transcript"""
    def __init__(self, hgnc_symbol, transcript_id, consequence, ensembl_id=None, biotype=None, 
                strand=None, sift=None, polyphen=None, exon=None, HGVSc=None, 
                HGVSp=None):
        super(Transcript, self).__init__(
            hgnc_symbol=hgnc_symbol, transcript_id=transcript_id, biotype=biotype,
            consequence=consequence, ensembl_id=ensembl_id, strand=strand, sift=sift,
            polyphen=polyphen, exon=exon, HGVSc=HGVSc, HGVSp=HGVSp)


class Gene(dict):
    """Class that holds information about a Gene"""
    def __init__(self, symbol, omim_number=None, ensembl_id=None, 
                description=None, chrom=None, start=None, stop=None,
                location=None, hi_score=None, constraint_score=None,
                hgnc_id=None):
        super(Gene, self).__init__(symbol=symbol, omim_number=omim_number,
        ensembl_id=ensembl_id, description=description, chrom=chrom, 
        start=start, stop=stop, location=location, hi_score=hi_score, 
        constraint_score=constraint_score, hgnc_id=hgnc_id)
        
        self['morbid'] = None

class Compound(dict):
    """Class that holds information about a compound variant"""
    def __init__(self, variant_id, combined_score=None):
        super(Compound, self).__init__(variant_id=variant_id,
                                       combined_score=combined_score)


class Genotype(dict, PedigreeHumanMixin):
    """Class that holds information about a genotype call"""
    def __init__(self, sample_id, genotype, case_id=None, phenotype=None,
                ref_depth='.', alt_depth='.', genotype_quality='.', depth='.',
                supporting_evidence='0', pe_support='0', sr_support='0'):
        super(Genotype, self).__init__(sample_id=sample_id, genotype=genotype,
            case_id=case_id, phenotype=phenotype, ref_depth=ref_depth, 
            alt_depth=alt_depth, depth=depth, genotype_quality=genotype_quality,
            supporting_evidence=supporting_evidence, pe_support=pe_support, 
            sr_support=sr_support)


class Variant(dict):
    """docstring for Variant"""
    def __init__(self, CHROM, POS, ID, REF, ALT, QUAL, FILTER):
        super(Variant, self).__init__(CHROM=CHROM, POS=POS, ID=ID, REF=REF,
                                      ALT=ALT, QUAL=QUAL, FILTER=FILTER)

        self._set_variant_id()
        self['index'] = None

        self['thousand_g'] = None  # float
        self['max_freq'] = None  # float
        self['cadd_score'] = None  # float
        self['most_severe_consequence'] = None  # str
        self['rank_score'] = None  # float

        self['frequencies'] = []
        self['severities'] = []
        self['transcripts'] = []  # List of Transcripts
        self['individuals'] = []  # List of Genotypes
        self['genes'] = []  # List of Genes
        self['compounds'] = []  # List of Compounds
        self['genetic_models'] = []  # List of genetic models followed
        #SV specific fields:
        self['sv_type'] = None
        self['sv_len'] = None
        self['stop_chrom'] = None
        self['stop'] = None
        self['cytoband_start'] = None
        self['cytoband_stop'] = None
    
    @property
    def nr_genes(self):
        """Return the number of genes"""
        return len(self['genes'])

    @property
    def is_intrachromosomal(self):
        """Check if variant is intrachromosomal
            
            If stop_chrom != CHROM return True
            else return False
        """
        return self.get('stop_chrom', self['CHROM']) != self['CHROM']

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
                self['CHROM'],
                self['POS'],
                self['REF'],
                self['ALT']
                ])

        logger.debug("Updating variant id to {0}".format(
            variant_id))

        self['variant_id'] = variant_id

