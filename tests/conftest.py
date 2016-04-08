# -*- coding: utf-8 -*-
import os
import shutil
import pytest
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# from puzzle.factory import create_app
from puzzle.models import (Variant, DotDict, Individual)
from puzzle.models.sql import BASE
from puzzle.models.sql import Case as SqlCase
from puzzle.plugins import VcfPlugin, SqlStore
from puzzle.utils import (get_cases, get_header)
# from puzzle.settings import TestConfig

from puzzle.log import configure_stream

root_logger = configure_stream()
logger = logging.getLogger(__name__)


@pytest.fixture
def vcf():
    db = VcfPlugin()
    return db

@pytest.fixture(scope='function')
def puzzle_dir(request, dir_path):
    """Return a puzzle dir with a database initialized"""
    db_path = os.path.join(dir_path, 'puzzle_db.sqlite3')
    logger.debug("db path is: {}".format(db_path))

    resource_dir = os.path.join(dir_path, 'resources')
    logger.debug("resource dir is: {}".format(resource_dir))

    logger.debug("Create directory: {0}".format(resource_dir))
    os.makedirs(resource_dir)
    logger.debug('Directory created')

    logger.debug('Connect to database and create tables')
    store = SqlStore(db_path)
    store.set_up(reset=False)

    # It's getting tear downed by dir_path()...

    return dir_path

@pytest.fixture(scope='function')
def gemini_path(request):
    """Return the path of a gemini database"""
    gemini_db = "tests/fixtures/HapMapFew.db"
    return gemini_db


@pytest.fixture(scope='function')
def vcf_file(request):
    "Return the path to the hapmap vcf"
    hapmap = "tests/fixtures/hapmap.vcf"
    return hapmap

@pytest.fixture(scope='function')
def vcf_file_no_ind(request):
    "Return the path to the hapmap vcf"
    hapmap = "tests/fixtures/no_ind.vcf"
    return hapmap

@pytest.fixture(scope='function')
def vcf_file_sv(request):
    "Return the path to the hapmap vcf with sv variants"
    hapmap = "tests/fixtures/hapmap.sv.vep.vcf.gz"
    return hapmap

@pytest.fixture(scope='function')
def compressed_vcf_file(request):
    "Return the path to the compressed hapmap vcf"
    hapmap = "tests/fixtures/hapmap.vcf.gz"
    return hapmap

@pytest.fixture(scope='function')
def indexed_vcf_file(request):
    "Return the path to a hapmap vcf with tabix index"
    hapmap = "tests/fixtures/hapmap_pos.vcf.gz"
    return hapmap

@pytest.fixture(scope='function')
def root_path(request):
    "Return the path to the test root dir"
    root = "tests/fixtures/"
    return root


@pytest.fixture(scope='function')
def ped_file(request):
    "Return the path to the hapmap vcf"
    hapmap = "tests/fixtures/hapmap.ped"
    return hapmap


@pytest.fixture(scope='function')
def gemini_db_path(request):
    "Return the path to the hapmap gemini db"
    hapmap = "tests/fixtures/HapMapFew.db"
    return hapmap

@pytest.fixture(scope='function')
def gemini_sv_db_path(request):
    "Return the path to the hapmap gemini db"
    hapmap = "tests/fixtures/HapMapSv.db"
    return hapmap

@pytest.fixture(scope='function')
def populated_puzzle_db(request, dir_path, case_obj):
    """Return a puzzle dir with a populated database"""
    db_path = os.path.join(dir_path, 'puzzle_db.sqlite3')
    logger.debug("db path is: {}".format(db_path))

    resource_dir = os.path.join(dir_path, 'resources')
    logger.debug("resource dir is: {}".format(resource_dir))

    logger.debug("Create directory: {0}".format(resource_dir))
    os.makedirs(resource_dir)
    logger.debug('Directory created')

    logger.debug('Connect to database and create tables')
    store = SqlStore(db_path)
    store.set_up(reset=False)

    store.add_case(case_obj, vtype='sv', mode='vcf')

    #It's getting tear downed by dir_path()...

    return dir_path


@pytest.fixture(scope='function')
def dir_path(request):
    """Return the path to a dir. Delete afterwards"""
    path_to_dir = "tests/fixtures/test_dir"

    def teardown():
        print('\n')
        logger.info("Teardown directory")
        if os.path.exists(path_to_dir):
            shutil.rmtree(path_to_dir)
    request.addfinalizer(teardown)

    return path_to_dir


@pytest.fixture
def variant():
    """Return a variant dictionary"""
    data = dict(CHROM='1', POS='100', ID='rs01', REF='A', ALT='T', QUAL='100',
                FILTER='PASS')
    variant = Variant(**data)
    return variant


@pytest.fixture(scope='session')
def session(request):
    """Create and return a session to a sqlite database"""
    engine = create_engine("sqlite:///:memory:")
    connection = engine.connect()

    session = sessionmaker()
    session.configure(bind=engine)
    BASE.metadata.create_all(engine)

    s = session()

    def teardown():
        print('\n')
        logger.info("Teardown sqlite database")
        s.close()
        connection.close()
    request.addfinalizer(teardown)

    return s

@pytest.fixture(scope='function')
def individual():
    """Return a individual object"""
    ind_obj = (Individual('1'))
    return ind_obj


@pytest.yield_fixture(scope='session')
def ped_lines():
    """Return an unformatted list of ped lines."""
    _ped_lines = [
        "636808\tADM1059A1\t0\t0\t1\t1",
        "636808\tADM1059A2\tADM1059A1\tADM1059A3\t1\t2",
        "636808\tADM1059A3\t0\t0\t2\t1"
    ]
    yield _ped_lines


@pytest.yield_fixture(scope='function')
def case_obj(ped_lines):
    """Return a test case object with individuals."""
    _case = get_cases('tests/fixtures/hapmap.vcf', case_lines=ped_lines)[0]
    yield _case

# @pytest.yield_fixture(scope='function')
# def sql_case_obj(case_obj):
#     """Return a test case for the sql model."""
#     _sql_case = SqlCase(case_id=case_obj.case_id,
#                     name=case_obj.name,
#                     variant_source=case_obj.variant_source,
#                     variant_type=case_obj.variant_type,
#                     variant_mode=case_obj.variant_type,
#                     compressed=case_obj.compressed,
#                     tabix_index=case_obj.tabix_index)
#
#     yield _sql_case

@pytest.yield_fixture(scope='function')
def gemini_case_obj(gemini_db_path):
    """Return a case object extracted from gemini database"""
    _case = get_cases(gemini_db_path, variant_mode='gemini')[0]
    yield _case

@pytest.yield_fixture(scope='function')
def gemini_sv_case_obj(gemini_sv_db_path):
    """Return a case object extracted from gemini database"""
    _case = get_cases(gemini_sv_db_path, variant_mode='gemini')[0]
    _case['variant_type'] = 'sv'
    yield _case

@pytest.yield_fixture(scope='function')
def sql_store():
    """Setup an in-memory database."""
    _test_db = SqlStore('sqlite:///:memory:')
    _test_db.set_up()
    yield _test_db
    _test_db.tear_down()


@pytest.yield_fixture(scope='function')
def test_db(sql_store, case_obj):
    """Populate database with some sample data."""
    new_case = sql_store.add_case(case_obj)
    sql_store.add_gemini_query('Chuck Norris Query', "SELECT * FROM variants")
    sql_store.add_genelist('test-list', ['ADK', 'KRAS', 'DIABLO'],
                           case_obj=new_case)
    yield sql_store
    sql_store.tear_down()
    sql_store.set_up()

@pytest.yield_fixture(scope='session')
def phenomizer_auth():
    """Fetch phenomizer auth details from ENV variables."""
    raw_auth = os.environ['PHENOMIZER_AUTH']
    auth = raw_auth.split()
    yield auth

@pytest.fixture(scope='function')
def header(vcf_file):
    """Return a header object."""
    head = get_header(vcf_file)
    return head

@pytest.fixture(scope='function')
def cyvcf_variant(request):
    "Return dictionary to mock a cyvcf variant"
    variant = DotDict()
    variant.CHROM = 'X'
    variant.POS = 84563218
    variant.REF = 'C'
    variant.ALT = ['G']
    variant.FILTER = 'PASS'
    variant.ID ='rs1'
    variant.QUAL = 360.829986572
    variant.INFO = {
            'CADD': 25,
            'CSQ': "G|missense_variant|MODERATE|POF1B|ENSG00000124429|"\
            "Transcript|ENST00000373145|protein_coding|10/16||ENST00000373145"\
            ".3:c.962G>C|ENSP00000362238.3:p.Arg321Thr|1082|962|321|R/T|aGg/"\
            "aCg|||-1|HGNC|13711|||ENSP00000362238|POF1B_HUMAN||UPI00001AE9F1"\
            "|deleterious|possibly_damaging|hmmpanther:PTHR22546|||||,G|"\
            "missense_variant|MODERATE|POF1B|ENSG00000124429|Transcript|"\
            "ENST00000262753|protein_coding|10/17||ENST00000262753.4:c.962G"\
            ">C|ENSP00000262753.4:p.Arg321Thr|1108|962|321|R/T|aGg/aCg|||-"\
            "1|HGNC|13711||CCDS14452.1|ENSP00000262753|POF1B_HUMAN||"\
            "UPI0000212116|deleterious|probably_damaging|hmmpanther:PTHR22546|||||",
        'Compounds': '643594:X_84615532_GTA_G>12',
        'Ensembl_gene_id': 'ENSG00000124429',
        'GeneticModels': '643594:XD_dn|AR_comp_dn|XR_dn',
        'ModelScore': '643594:16.0',
        'RankScore': '643594:19',
         }
    variant.start = 84563217
    variant.end = 84563218
    variant.var_type = 'snp'
    variant.sub_vartype = 'tv'
    variant.gt_types = ['C/C', 'C/G', 'C/C']
    variant.gt_types = [0, 1, 0]
    variant.gt_depths = [20,  7, 20]
    variant.gt_ref_depths = [20,  1, 20]
    variant.gt_alt_depths = [0, 6, 0]
    variant.gt_quals = [ 57.,  16.,  54.]
    variant.aaf = 0.16666666666666666
    variant.call_rate =  1.0
    variant.gt_phases = [False, False, False]
    variant.gt_phred_ll_het = [57,0,54]
    variant.gt_phred_ll_homalt = [855,16,810]
    variant.gt_phred_ll_homref = [0,154,0]
    variant.is_deletion = False
    variant.is_indel = False
    variant.is_snp = True
    variant.is_sv = False
    variant.is_transition = False
    variant.nucl_diversity = 0.3333333333333333
    variant.num_called = 3
    variant.num_het = 1
    variant.num_hom_alt = 0
    variant.num_hom_ref = 2
    variant.num_unknown = 0
    
    return variant


@pytest.fixture(scope='function')
def gemini_variant(request):
    "Return dictionary to mock a gemini variant"
    variant = {
        'chrom': 'chr1',
        'start': 36636644,
        'end': 36636645,
        'variant_id': 1,
        'ref': 'G',
        'alt': 'A',
        'qual': 360.829986572,
        'type': 'snp',
        'sub_type': 'ts',
        'gts': ['G/A', 'G/A', './.', './.', './.'],
        'gt_types': [1, 1, 2, 2, 2],
        'gt_depths': [17, 19, -1, -1, -1],
        'gt_ref_depths': [10, 13, -1, -1, -1],
        'gt_alt_depths': [7, 6, -1, -1, -1],
        'gt_quals': [99, 99, -1, -1, -1],
        'in_dbsnp': 0,
        'rs_ids': None,
        'gene': 'MAP7D1',
        'transcript': 'ENST00000530729',
        'is_exonic': 1,
        'is_coding': 1,
        'is_lof': 1,
        'exon': 2/4,
        'codon_change': 'atG/atA',
        'aa_change': 'M/I',
        'aa_length': '1/140',
        'biotype': 'protein_coding',
        'impact': 'transcript_codon_change',
        'impact_so': 'initiator_codon_variant',
        'impact_severity': 'HIGH',
        'polyphen_pred': 'benign',
        'polyphen_score': 0.304,
        'sift_pred': 'deleterious',
        'sift_score': 0.0,
        'aaf_esp_ea': None,
        'aaf_esp_aa': None,
        'aaf_esp_all': None,
        'aaf_1kg_amr': None,
        'aaf_1kg_eas': None,
        'aaf_1kg_sas': None,
        'aaf_1kg_afr': None,
        'aaf_1kg_eur': None,
        'aaf_1kg_all': None,
        'cadd_raw': 2.49,
        'cadd_scaled': 14.3,
        'aaf_exac_all': 1.647e-05,
        'aaf_adj_exac_all': 1.67162582328e-05,
        'max_aaf_all': 3.03471716436e-05,
    }
    return variant
