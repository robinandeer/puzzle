# -*- coding: utf-8 -*-
"""
puzzle.plugins.sql.store
~~~~~~~~~~~~~~~~~~
"""
import itertools
import logging
import os

import phizz
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from puzzle.models import Case as BaseCase
from puzzle.models import Individual as BaseIndividual
from puzzle.models.sql import (BASE, Case, Individual, PhenotypeTerm, GeneList,
                               CaseGenelistLink, Resource, GeminiQuery)
from puzzle.plugins import VcfPlugin, Plugin

try:
    from puzzle.plugins import GeminiPlugin
except ImportError as e:
    pass
from puzzle.utils import hpo_genes

logger = logging.getLogger(__name__)


class Store(Plugin):

    """SQLAlchemy-based database object.

    .. note::
        For testing pourposes use ``:memory:`` as the ``path`` argument to
        set up in-memory (temporary) database.

    Args:
        uri (Optional[str]): path/URI to the database to connect to
        debug (Optional[bool]): whether to output logging information
        phenomizer_auth (Optional[tuple]): username and password

    Attributes:
        uri (str): path/URI to the database to connect to
        engine (class): SQLAlchemy engine, defines what database to use
        session (class): SQLAlchemy ORM session, manages persistance
        query (method): SQLAlchemy ORM query builder method
        classes (dict): bound ORM classes
    """

    def __init__(self, uri=None, debug=False, vtype='snv',
                 phenomizer_auth=None):
        super(Store, self).__init__()
        self.uri = uri
        if uri:
            self.connect(uri, debug=debug)
        self.variant_type = vtype
        self.phenomizer_auth = phenomizer_auth

        # ORM class shortcuts to enable fetching models dynamically
        # self.classes = {'gene': Gene, 'transcript': Transcript,
        #                 'exon': Exon, 'sample': Sample}

    def init_app(self, app):
        pass

    def connect(self, db_uri, debug=False):
        """Configure connection to a SQL database.

        Args:
            db_uri (str): path/URI to the database to connect to
            debug (Optional[bool]): whether to output logging information
        """
        kwargs = {'echo': debug, 'convert_unicode': True}
        # connect to the SQL database
        if 'mysql' in db_uri:
            kwargs['pool_recycle'] = 3600
        elif '://' not in db_uri:
            logger.debug("detected sqlite path URI: {}".format(db_uri))
            db_path = os.path.abspath(os.path.expanduser(db_uri))
            db_uri = "sqlite:///{}".format(db_path)

        self.engine = create_engine(db_uri, **kwargs)
        logger.debug('connection established successfully')
        # make sure the same engine is propagated to the BASE classes
        BASE.metadata.bind = self.engine
        # start a session
        self.session = scoped_session(sessionmaker(bind=self.engine))
        # shortcut to query method
        self.query = self.session.query
        return self

    @property
    def dialect(self):
        """Return database dialect name used for the current connection.
        Dynamic attribute.
        Returns:
            str: name of dialect used for database connection
        """
        return self.engine.dialect.name

    def set_up(self, reset=False):
        """Initialize a new database with the default tables and columns.
        Returns:
            Store: self
        """
        if reset:
            self.tear_down()

        logger.info("Creating database")
        # create the tables
        BASE.metadata.create_all(self.engine)
        return self

    def tear_down(self):
        """Tear down a database (tables and columns).
        Returns:
            Store: self
        """
        # drop/delete the tables
        logger.info('resetting database...')
        BASE.metadata.drop_all(self.engine)
        return self

    def save(self):
        """Manually persist changes made to various elements. Chainable.

        Returns:
            Store: ``self`` for chainability
        """
        # commit/persist dirty changes to the database
        self.session.flush()
        self.session.commit()
        return self

    def add_case(self, case_obj, vtype='snv', mode='vcf', ped_svg=None):
        """Load a case with individuals.

        Args:
            case_obj (puzzle.models.Case): initialized case model
        """
        new_case = Case(case_id=case_obj.case_id,
                        name=case_obj.name,
                        variant_source=case_obj.variant_source,
                        variant_type=vtype,
                        variant_mode=mode,
                        pedigree=ped_svg)

        # build individuals
        inds = [Individual(
            ind_id=ind.ind_id,
            name=ind.name,
            mother=ind.mother,
            father=ind.father,
            sex=ind.sex,
            phenotype=ind.phenotype,
            ind_index=ind.ind_index,
            variant_source=ind.variant_source,
            bam_path=ind.bam_path,
        ) for ind in case_obj.individuals]

        new_case.individuals = inds
        self.session.add(new_case)
        self.save()
        return new_case

    def delete_case(self, case_obj):
        """Delete a case from the database

        Args:
            case_obj (puzzle.models.Case): initialized case model
        """
        for ind_obj in case_obj.individuals:
            self.delete_individual(ind_obj)
        logger.info("Deleting case {0} from database".format(case_obj.case_id))
        self.session.delete(case_obj)
        self.save()
        return case_obj

    def delete_individual(self, ind_obj):
        """Delete a case from the database

        Args:
            ind_obj (puzzle.models.Individual): initialized individual model
        """
        logger.info("Deleting individual {0} from database".format(ind_obj.ind_id))
        self.session.delete(ind_obj)
        self.save()
        return ind_obj

    def case(self, case_id):
        """Fetch a case from the database."""
        case_obj = self.query(Case).filter_by(case_id=case_id).first()
        if case_obj is None:
            case_obj = BaseCase(case_id='unknown')
        return case_obj

    def individual(self, ind_id):
        """Fetch a case from the database."""
        ind_obj = self.query(Individual).filter_by(ind_id=ind_id).first()
        if ind_obj is None:
            ind_obj = BaseIndividual(ind_id='unknown')
        return ind_obj

    def cases(self):
        """Fetch all cases from the database."""
        return self.query(Case)

    def get_individuals(self, ind_ids=None):
        """Fetch all individuals from the database."""
        query = self.query(Individual)
        if ind_ids:
            query = query.filter(Individual.ind_id.in_(ind_ids))
        return query

    def variants(self, case_id, skip=0, count=30, filters=None):
        """Fetch variants for a case."""
        filters = filters or {}
        logger.debug("Fetching case with case_id:{0}".format(case_id))
        case_obj = self.case(case_id)
        plugin, case_id = self.select_plugin(case_obj)
        self.filters = plugin.filters

        gene_lists = (self.gene_list(list_id) for list_id
                      in filters.get('gene_lists', []))
        nested_geneids = (gene_list.gene_ids for gene_list in gene_lists)
        gene_ids = set(itertools.chain.from_iterable(nested_geneids))

        if filters.get('gene_ids'):
            filters['gene_ids'].extend(gene_ids)
        else:
            filters['gene_ids'] = gene_ids
        variants = plugin.variants(case_id, skip, count, filters)
        return variants

    def variant(self, case_id, variant_id):
        """Fetch a single variant from variant source."""
        case_obj = self.case(case_id)
        plugin, case_id = self.select_plugin(case_obj)
        variant = plugin.variant(case_id, variant_id)
        return variant

    def add_phenotype(self, ind_obj, phenotype_id):
        """Add a phenotype term to the case."""
        if phenotype_id.startswith('HP:') or len(phenotype_id) == 7:
            logger.debug('querying on HPO term')
            hpo_results = phizz.query_hpo([phenotype_id])
        else:
            logger.debug('querying on OMIM term')
            hpo_results = phizz.query_disease([phenotype_id])

        added_terms = []
        existing_ids = set(term.phenotype_id for term in ind_obj.phenotypes)
        for result in hpo_results:
            if result['hpo_term'] not in existing_ids:
                term = PhenotypeTerm(phenotype_id=result['hpo_term'],
                                     description=result['description'])
                logger.info('adding new HPO term: %s', term.phenotype_id)
                ind_obj.phenotypes.append(term)
                added_terms.append(term)

        logger.debug('storing new HPO terms')
        self.save()

        if len(added_terms) > 0:
            self.update_hpolist(ind_obj.ind_id)

        return added_terms

    def update_hpolist(self, ind_id):
        """Update the HPO gene list for a case based on current terms."""
        ind_obj = self.individual(ind_id)
        # update the HPO gene list for the case
        hpo_list = self.case_genelist(ind_obj.case)
        hpo_results = hpo_genes(ind_obj.case.phenotype_ids(),
                                *self.phenomizer_auth)

        if hpo_results is None:
            pass
            # Why raise here?
            # raise RuntimeError("couldn't link to genes, try again")
        else:
            gene_ids = [result['gene_id'] for result in hpo_results
                        if result['gene_id']]
            hpo_list.gene_ids = gene_ids
            self.save()

    def remove_phenotype(self, ind_obj, phenotypes=None):
        """Remove multiple phenotypes from an individual."""
        if phenotypes is None:
            logger.info("delete all phenotypes related to %s", ind_obj.ind_id)
            self.query(PhenotypeTerm).filter_by(ind_id=ind_obj.id).delete()
        else:
            for term in ind_obj.phenotypes:
                if term.phenotype_id in phenotypes:
                    logger.info("delete phenotype: %s from %s",
                                term.phenotype_id, ind_obj.ind_id)
                    self.session.delete(term)
        logger.debug('persist removals')
        self.save()
        self.update_hpolist(ind_obj.ind_id)

    def gene_list(self, list_id):
        """Get a gene list from the database."""
        return self.query(GeneList).filter_by(list_id=list_id).first()

    def gene_lists(self):
        """Return all gene lists from the database."""
        return self.query(GeneList)

    def add_genelist(self, list_id, gene_ids, case_obj=None):
        """Create a new gene list and optionally link to cases."""
        new_genelist = GeneList(list_id=list_id)
        new_genelist.gene_ids = gene_ids
        if case_obj:
            new_genelist.cases.append(case_obj)

        self.session.add(new_genelist)
        self.save()
        return new_genelist

    def remove_genelist(self, list_id, case_obj=None):
        """Remove a gene list and links to cases."""
        gene_list = self.gene_list(list_id)

        if case_obj:
            # remove a single link between case and gene list
            case_ids = [case_obj.id]
        else:
            # remove all links and the list itself
            case_ids = [case.id for case in gene_list.cases]
            self.session.delete(gene_list)

        case_links = self.query(CaseGenelistLink).filter(
            CaseGenelistLink.case_id.in_(case_ids),
            CaseGenelistLink.genelist_id == gene_list.id
        )
        for case_link in case_links:
            self.session.delete(case_link)

        self.save()

    def case_genelist(self, case_obj):
        """Get or create a new case specific gene list record."""
        list_id = "{}-HPO".format(case_obj.case_id)
        gene_list = self.gene_list(list_id)

        if gene_list is None:
            gene_list = GeneList(list_id=list_id)
            case_obj.gene_lists.append(gene_list)
            self.session.add(gene_list)

        return gene_list

    def select_plugin(self, case_obj):
        """Select and initialize the correct plugin for the case."""
        if case_obj.variant_mode == 'vcf':
            logger.debug("Using vcf plugin")
            plugin = VcfPlugin(vtype=case_obj.variant_type)
        elif case_obj.variant_mode == 'gemini':
            logger.debug("Using gemini plugin")
            plugin = GeminiPlugin(vtype=case_obj.variant_type)
            plugin.db = case_obj.variant_source

        plugin.case_objs = [case_obj]

        self.variant_type = case_obj.variant_type

        case_id = case_obj.case_id
        return plugin, case_id

    def add_resource(self, name, file_path, ind_obj):
        """Link a resource to an individual."""
        new_resource = Resource(name=name, individual=ind_obj, path=file_path)
        self.session.add(new_resource)
        self.save()
        return new_resource

    def resource(self, resource_id):
        """Fetch a resource."""
        return self.query(Resource).get(resource_id)

    def delete_resource(self, resource_id):
        """Link a resource to an individual."""
        resource_obj = self.resource(resource_id)
        logger.debug("Deleting resource {0}".format(resource_obj.name))
        self.session.delete(resource_obj)
        self.save()
    
    def gemini_query(self, name):
        """Return a gemini query
        
        Args:
            name (str)
        """
        logger.debug("Looking for query with name {0}".format(name))
        return self.query(GeminiQuery).get(name=name)

    def gemini_queries(self):
        """Return all gemini queries
        
        """
        return self.query(GeminiQuery)

    def add_gemini_query(self, name, query):
        """Add a user defined gemini query
        
        Args:
            name (str)
            query (str)
        """
        logger.info("Adding query {0} with text {1}".format(name, query))
        new_query = GeminiQuery(name=name, query=query)
        self.session.add(new_query)
        self.save()
    
    def delete_gemini_query(self, name):
        """Delete a gemini query
        
        Args:
            name (str)
        """
        query_obj = self.gemini_query(name)
        logger.debug("Delete query with name {0}".format(name))
        self.session.delete(query_obj)
        self.save()
