# -*- coding: utf-8 -*-
import codecs
import json
import os
from pkg_resources import resource_filename
import gzip
from intervaltree import Interval, IntervalTree

import puzzle

SO_TERMS = (
  'transcript_ablation',
  'splice_donor_variant',
  'splice_acceptor_variant',
  'stop_gained',
  'frameshift_variant',
  'stop_lost',
  'start_lost',
  'initiator_codon_variant',
  'transcript_amplification',
  'inframe_insertion',
  'inframe_deletion',
  'missense_variant',
  'protein_altering_variant',
  'splice_region_variant',
  'incomplete_terminal_codon_variant',
  'stop_retained_variant',
  'synonymous_variant',
  'coding_sequence_variant',
  'mature_miRNA_variant',
  '5_prime_UTR_variant',
  '3_prime_UTR_variant',
  'non_coding_exon_variant',
  'non_coding_transcript_exon_variant',
  'non_coding_transcript_variant',
  'nc_transcript_variant',
  'intron_variant',
  'NMD_transcript_variant',
  'non_coding_transcript_variant',
  'upstream_gene_variant',
  'downstream_gene_variant',
  'TFBS_ablation',
  'TFBS_amplification',
  'TF_binding_site_variant',
  'regulatory_region_ablation',
  'regulatory_region_amplification',
  'regulatory_region_variant',
  'feature_elongation',
  'feature_truncation',
  'intergenic_variant'
)

IMPACT_SEVERITIES = {
    "transcript_ablation": "HIGH",
    "splice_acceptor_variant": "HIGH",
    "splice_donor_variant": "HIGH",
    "stop_gained": "HIGH",
    "stop_lost": "HIGH",
    "frameshift_variant": "HIGH",
    "start_lost": "HIGH",
    "exon_loss_variant": "HIGH",
    "initiator_codon_variant": "HIGH",
    "initiator_codon_variant": "HIGH",
    "chromosomal_deletion": "HIGH",
    "rare_amino_acid_variant": "HIGH",
    "missense_variant": "MEDIUM",
    "inframe_insertion": "MEDIUM",
    "inframe_deletion": "MEDIUM",
    "coding_sequence_variant": "MEDIUM",
    "disruptive_inframe_deletion": "MEDIUM",
    "disruptive_inframe_insertion": "MEDIUM",
    "5_prime_UTR_truncation": "MEDIUM",
    "exon_loss_variant": "MEDIUM",
    "3_prime_UTR_truncation": "MEDIUM",
    "exon_loss_variant": "MEDIUM",
    "splice_region_variant": "MEDIUM",
    "mature_miRNA_variant": "MEDIUM",
    "regulatory_region_variant": "MEDIUM",
    "TF_binding_site_variant": "MEDIUM",
    "regulatory_region_ablation": "MEDIUM",
    "regulatory_region_amplification": "MEDIUM",
    "TFBS_ablation": "MEDIUM",
    "TFBS_amplification": "MEDIUM",
    "stop_retained_variant": "LOW",
    "synonymous_variant": "LOW",
    "5_prime_UTR_variant": "LOW",
    "3_prime_UTR_variant": "LOW",
    "intron_variant": "LOW",
    "coding_sequence_variant": "LOW",
    "upstream_gene_variant": "LOW",
    "downstream_gene_variant": "LOW",
    "intergenic_variant": "LOW",
    "conserved_intergenic_variant": "LOW",
    "intragenic_variant": "LOW",
    "gene_variant": "LOW",
    "transcript_variant": "LOW",
    "exon_variant": "LOW",
    "5_prime_UTR_premature_start_codon_gain_variant": "LOW",
    "start_retained_variant": "LOW",
    "conserved_intron_variant": "LOW",
    "nc_transcript_variant": "LOW",
    "NMD_transcript_variant": "LOW",
    "incomplete_terminal_codon_variant": "LOW",
    "non_coding_exon_variant": "LOW",
    "transcript_amplification": "LOW",
    "feature_elongation": "LOW",
    "feature_truncation": "LOW",
}

# -*- coding: utf-8 -*-
SEVERITY_DICT = {}
for severity, term in enumerate(SO_TERMS):
    SEVERITY_DICT[term] = severity

resource_package = puzzle.__name__
hgnc_to_omim_path = os.path.join('utils', 'resources', 'hgnc_to_omim.json')
cytoband_path = os.path.join('utils', 'resources', 'cytoBand.txt.gz')

converter_path = resource_filename(resource_package, hgnc_to_omim_path)
cytoband_path = resource_filename(resource_package, cytoband_path)

with codecs.open(converter_path, 'r') as stream:
    HGNC_TO_OMIM = json.load(stream)

CYTOBANDS = {}

with gzip.open(cytoband_path, 'r') as cytobands:
    for line in cytobands:
        line = line.rstrip().split('\t')
        chrom = line[0].strip('chr')
        start = int(line[1])
        stop = int(line[2])
        cytoband = line[3]
        if chrom in CYTOBANDS:
            tree = CYTOBANDS[chrom]
            tree[start:stop] = cytoband
        else:
            CYTOBANDS[chrom] = IntervalTree([Interval(start, stop, cytoband)])
