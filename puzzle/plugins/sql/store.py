# -*- coding: utf-8 -*-
"""
puzzle.plugins.sql.store
~~~~~~~~~~~~~~~~~~
"""
import logging
import os

import phizz
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from puzzle.models import Case as BaseCase
from puzzle.models import Individual as BaseIndividual
from puzzle.models.sql import (BASE, Case, Individual, PhenotypeTerm, GeneList,
                               CaseGenelistLink, Resource)
from puzzle.plugins import VcfPlugin, Plugin

from . import VariantMixin, CaseMixin

try:
    from puzzle.plugins import GeminiPlugin
except ImportError as e:
    pass
from puzzle.utils import hpo_genes

logger = logging.getLogger(__name__)


class Store(VariantMixin, CaseMixin, Plugin):

    """SQLAlchemy-based database object.
    .. note::
        For testing pourposes use ``:memory:`` as the ``path`` argument to
        set up in-memory (temporary) database.
    Args:
        uri (Optional[str]): path/URI to the database to connect to
        debug (Optional[bool]): whether to output logging information
    Attributes:
        uri (str): path/URI to the database to connect to
        engine (class): SQLAlchemy engine, defines what database to use
        session (class): SQLAlchemy ORM session, manages persistance
        query (method): SQLAlchemy ORM query builder method
        classes (dict): bound ORM classes
    """

    def __init__(self, uri=None, debug=False, vtype='snv'):
        super(Store, self).__init__()
        self.uri = uri
        if uri:
            self.connect(uri, debug=debug)
        self.variant_type = vtype

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
        hpo_results = hpo_genes(ind_obj.case.phenotype_ids())

        if hpo_results is None:
            pass
            #Why raise here?
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
