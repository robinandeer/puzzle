from puzzle.plugins import VcfPlugin

def test_add_consequences(variant):
    plugin = VcfPlugin()
    # The raw variant line is treated like a string so it does not matter
    # if it is malformed
    raw_variant_line = "7\t98994144\t.\tA\tC\t51.68\tPASS\tAC=1;AF=0.167;AN=6"\
    ";BaseQRankSum=-1.965;CADD=13.51;CSQ=C|downstream_gene_variant|MODIFIER|"\
    "ARPC1B|ENSG00000130429|Transcript|ENST00000491294|retained_intron|||||||"\
    "||||1724|1|HGNC|704||||||||||||||,C|downstream_gene_variant|MODIFIER|"\
    "ARPC1B|ENSG00000130429|Transcript|ENST00000451682|protein_coding||||||||"\
    "|||1745|1|HGNC|704||CCDS5661.1|ENSP00000389631|ARC1B_HUMAN|F8VXW2_HUMAN"\
    "&C9K057_HUMAN&C9JTT6_HUMAN&C9JQM8_HUMAN&C9JM51_HUMAN&C9JFG9_HUMAN&C9JEY1"\
    "_HUMAN&C9JBJ7_HUMAN&C9J6C8_HUMAN&C9J4Z7_HUMAN&A4D275_HUMAN|UPI0000125D33|"
    
    plugin._add_consequences(variant, raw_variant_line)
    
    assert variant.consequences == ["downstream_gene_variant"]

def test_add_most_severe_no_info(variant):
    plugin = VcfPlugin()
    plugin._add_most_severe_consequence(variant)
    
    assert variant.most_severe_consequence == None

def test_add_most_severe(variant):
    plugin = VcfPlugin()
    
    variant.consequences = ['downstream_gene_variant', 'stop_gained']
    plugin._add_most_severe_consequence(variant)
    
    assert variant.most_severe_consequence == 'stop_gained'

def test_add_impact_severity(variant):
    plugin = VcfPlugin()
    
    variant.most_severe_consequence = 'stop_gained'
    plugin._add_impact_severity(variant)
    
    assert variant.impact_severity == 'HIGH'