# -*- coding: utf-8 -*-
from flask import (abort, Blueprint, current_app as app, render_template,
                   redirect, request, url_for)
from werkzeug import secure_filename

from puzzle.utils import hpo_genes

BP_NAME = __name__.split('.')[-2]
blueprint = Blueprint(BP_NAME, __name__, template_folder='templates',
                      static_folder='static',
                      static_url_path="/{}/static".format(BP_NAME))


@blueprint.route('/')
def index():
    """Show the landing page."""
    gene_lists = app.db.gene_lists() if app.config['STORE_ENABLED'] else []
    return render_template('index.html', cases=app.db.cases(),
                           gene_lists=gene_lists)


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

        if hpo_results is None:
            return abort(500, "couldn't link to genes, try again"
                              .format(phenotype_id))

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


@blueprint.route('/genelists', methods=['POST'])
@blueprint.route('/genelists/<list_id>', methods=['GET', 'POST'])
def gene_list(list_id=None):
    """Display or add a gene list."""
    if list_id:
        genelist_obj = app.db.gene_list(list_id)
        case_ids = [case.case_id for case in app.db.cases()
                    if case not in genelist_obj.cases]
        if genelist_obj is None:
            return abort(404, "gene list not found: {}".format(list_id))

    if request.method == 'POST':
        if list_id:
            # link a case to the gene list
            case_ids = request.form.getlist('case_id')
            for case_id in case_ids:
                case_obj = app.db.case(case_id)
                if case_obj not in genelist_obj.cases:
                    genelist_obj.cases.append(case_obj)
                    app.db.save()
        else:
            # upload a new gene list
            req_file = request.files['file']
            list_id = (request.form['list_id'] or
                       secure_filename(req_file.filename))

            if not req_file:
                return abort(500, 'Please provide a file for upload')

            gene_ids = [line for line in req_file.stream
                        if not line.startswith('#')]
            genelist_obj = app.db.add_genelist(list_id, gene_ids)

    return render_template('gene_list.html', gene_list=genelist_obj,
                           case_ids=case_ids)


@blueprint.route('/genelists/delete/<list_id>', methods=['POST'])
@blueprint.route('/genelists/delete/<list_id>/<case_id>', methods=['POST'])
def delete_genelist(list_id, case_id=None):
    """Delete a whole gene list with links to cases or a link."""
    if case_id:
        # unlink a case from a gene list
        case_obj = app.db.case(case_id)
        app.db.remove_genelist(list_id, case_obj=case_obj)
        return redirect(request.referrer)
    else:
        # remove the whole gene list
        app.db.remove_genelist(list_id)
        return redirect(url_for('.index'))
