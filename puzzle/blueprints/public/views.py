# -*- coding: utf-8 -*-
from flask import (abort, Blueprint, current_app as app, render_template,
                   redirect, request)

from puzzle.utils import hpo_genes

BP_NAME = __name__.split('.')[-2]
blueprint = Blueprint(BP_NAME, __name__, template_folder='templates',
                      static_folder='static',
                      static_url_path="/{}/static".format(BP_NAME))


@blueprint.route('/')
def index():
    """Show the landing page."""
    return render_template('index.html', cases=app.db.cases())


@blueprint.route('/cases/<case_id>')
def case(case_id):
    """Show the overview for a case."""
    return render_template('case.html', case=app.db.case(case_id), case_id=case_id)


@blueprint.route('/phenotypes', methods=['POST'])
def phenotypes():
    """Add phenotype(s) to the case model."""
    ind_id = request.form['ind_id']
    phenotype_id = request.form['phenotype_id']

    if not phenotype_id:
        return abort(500, 'no phenotype_id submitted')

    ind_obj = app.db.individual(ind_id)
    terms_added = app.db.add_phenotype(ind_obj, phenotype_id)

    if len(terms_added) > 0:
        # update the HPO gene list for the case
        hpo_list = app.db.case_genelist(ind_obj.case)
        hpo_results = hpo_genes(ind_obj.case.phenotype_ids())
        gene_ids = [result['gene_id'] for result in hpo_results
                    if result['gene_id']]
        hpo_list.gene_ids = gene_ids
        app.db.save()

    return redirect(request.referrer)


@blueprint.route('/phenotypes/<phenotype_id>/delete', methods=['POST'])
def delete_phenotype(phenotype_id):
    """Delete phenotype from an individual."""
    ind_id = request.form['ind_id']
    ind_obj = app.db.individual(ind_id)
    app.db.remove_phenotype(ind_obj, phenotype_id)
    return redirect(request.referrer)


@blueprint.route('/genelists/<list_id>')
def gene_list(list_id):
    """Display details on a gene list."""
    genelist_obj = app.db.gene_list(list_id)
    if genelist_obj is None:
        return abort(404, "gene list not found: {}".format(list_id))

    return render_template('gene_list.html', gene_list=genelist_obj)
