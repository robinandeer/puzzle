from puzzle.utils import get_cytoband_coord

def test_get_cytoband_coord():
    chrom = '1'
    pos = 3
    
    assert get_cytoband_coord(chrom, pos) == '1.p36.33'

def test_get_cytoband_coord_chr():
    chrom = 'chr1'
    pos = 3
    
    assert get_cytoband_coord(chrom, pos) == '1.p36.33'

def test_get_cytoband_coord_str_pos():
    chrom = 'chr1'
    pos = '3'
    
    assert get_cytoband_coord(chrom, pos) == '1.p36.33'

def test_get_cytoband_coord_non_existing_chr():
    chrom = 'chrMT'
    pos = '3'
    
    assert get_cytoband_coord(chrom, pos) == None

def test_get_cytoband_coord_non_existing_pos():
    chrom = 'chrX'
    pos = '155270600'
    
    assert get_cytoband_coord(chrom, pos) == None
