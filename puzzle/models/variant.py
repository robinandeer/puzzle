import logging

logger = logging.getLogger(__name__)


class Transcript(dict):
    """Class that holds information about a transcript"""
    def __init__(self, SYMBOL, Feature, BIOTYPE, Consequence, STRAND, SIFT,
                 PolyPhen, EXON, HGVSc, HGVSp):
        super(Transcript, self).__init__(
            SYMBOL=SYMBOL, Feature=Feature, BIOTYPE=BIOTYPE,
            Consequence=Consequence, STRAND=STRAND, SIFT=SIFT,
            PolyPhen=PolyPhen, EXON=EXON, HGVSc=HGVSc, HGVSp=HGVSp)


class Gene(dict):
    """Class that holds information about a Gene"""
    def __init__(self, symbol, omim_number=None):
        super(Gene, self).__init__(symbol=symbol, omim_number=omim_number)


class Compound(dict):
    """Class that holds information about a compound variant"""
    def __init__(self, variant_id, combined_score=None):
        super(Compound, self).__init__(variant_id=variant_id,
                                       combined_score=combined_score)


class Genotype(dict):
    """Class that holds information about a genotype call"""
    def __init__(self, sample_id, genotype, ref_depth='.', alt_depth='.',
                 genotype_quality='.', depth='.'):
        super(Genotype, self).__init__(sample_id=sample_id, genotype=genotype,
                                       ref_depth=ref_depth, alt_depth=alt_depth,
                                       depth=depth,
                                       genotype_quality=genotype_quality)


class Variant(dict):
    """docstring for Variant"""
    def __init__(self, CHROM, POS, ID, REF, ALT, QUAL, FILTER):
        super(Variant, self).__init__(CHROM=CHROM, POS=POS, ID=ID, REF=REF,
                                      ALT=ALT, QUAL=QUAL, FILTER=FILTER)

        self._set_variant_id()
        self['index'] = None

        self['thousand_g'] = None  # float
        self['cadd_score'] = None  # float
        self['most_severe_consequence'] = None  # str
        self['rank_score'] = None  # float

        self['hgnc_symbols'] = []
        self['frequencies'] = []
        self['severities'] = []
        self['transcripts'] = []  # List of Transcripts
        self['individuals'] = []  # List of Genotypes
        self['genes'] = []  # List of Genes
        self['compounds'] = []  # List of Compounds
        self['genetic_models'] = []  # List of genetic models followed

    def add_frequency(self, name, value):
        """Add a frequency that will be displayed on the variant level

            Args:
                name (str): The name of the frequency field
        """
        self['frequencies'].append({name: value})

    def add_severities(self, name, value):
        """docstring for add_frequency"""
        self['frequencies'].append({name: value})

    def add_individual(self, genotype):
        """Add the information for a individual"""
        self['individuals'].append(genotype)

    def add_transcript(self, transcript):
        """Add the information transcript"""
        self['transcripts'].append(transcript)

    def add_gene(self, gene):
        """Add the information of a gene"""
        self['genes'].append(gene)

    def add_compound(self, compound):
        """Add the information of a compound variant"""
        self['compounds'].append(compound)

    def _set_variant_id(self, variant_id=None):
        """Set the variant id for this variant"""
        if variant_id:
            self['variant_id'] = variant_id
        else:
            self['variant_id'] = '_'.join([
                self['CHROM'],
                self['POS'],
                self['REF'],
                self['ALT']
                ])
