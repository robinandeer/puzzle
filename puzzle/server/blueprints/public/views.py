# -*- coding: utf-8 -*-
import os

from flask import (abort, Blueprint, current_app as app, render_template,
                   redirect, request, url_for, make_response,
                   send_from_directory)
from werkzeug import secure_filename

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
    return render_template('case.html', case=app.db.case(case_id),
                           case_id=case_id)


@blueprint.route('/phenotypes', methods=['POST'])
def phenotypes():
    """Add phenotype(s) to the case model."""
    ind_id = request.form['ind_id']
    phenotype_id = request.form['phenotype_id']

    if not phenotype_id:
        return abort(500, 'no phenotype_id submitted')

    ind_obj = app.db.individual(ind_id)
    try:
        app.db.add_phenotype(ind_obj, phenotype_id)
    except RuntimeError as error:
        return abort(500, error.message)

    return redirect(request.referrer)


@blueprint.route('/phenotypes/<phenotype_id>/delete', methods=['POST'])
def delete_phenotype(phenotype_id):
    """Delete phenotype from an individual."""
    ind_id = request.form['ind_id']
    ind_obj = app.db.individual(ind_id)
    try:
        app.db.remove_phenotype(ind_obj, phenotype_id)
    except RuntimeError as error:
        return abort(500, error.message)
    return redirect(request.referrer)


@blueprint.route('/genelists', methods=['POST'])
@blueprint.route('/genelists/<list_id>', methods=['GET', 'POST'])
def gene_list(list_id=None):
    """Display or add a gene list."""
    all_case_ids = [case.case_id for case in app.db.cases()]
    if list_id:
        genelist_obj = app.db.gene_list(list_id)
        case_ids = [case.case_id for case in app.db.cases()
                    if case not in genelist_obj.cases]
        if genelist_obj is None:
            return abort(404, "gene list not found: {}".format(list_id))

    if 'download' in request.args:
        response = make_response('\n'.join(genelist_obj.gene_ids))
        filename = secure_filename("{}.txt".format(genelist_obj.list_id))
        header = "attachment; filename={}".format(filename)
        response.headers['Content-Disposition'] = header
        return response

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
            new_listid = (request.form['list_id'] or
                          secure_filename(req_file.filename))

            if app.db.gene_list(new_listid):
                return abort(500, 'Please provide a unique list name')

            if not req_file:
                return abort(500, 'Please provide a file for upload')

            gene_ids = [line for line in req_file.stream
                        if not line.startswith('#')]
            genelist_obj = app.db.add_genelist(new_listid, gene_ids)
            case_ids = all_case_ids

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


@blueprint.route('/resources', methods=['POST'])
def resources():
    """Upload a new resource for an individual."""
    ind_id = request.form['ind_id']

    upload_dir = os.path.abspath(app.config['UPLOAD_DIR'])
    req_file = request.files['file']
    filename = secure_filename(req_file.filename)
    file_path = os.path.join(upload_dir, filename)
    name = request.form['name'] or filename
    req_file.save(file_path)

    ind_obj = app.db.individual(ind_id)
    app.db.add_resource(name, file_path, ind_obj)
    return redirect(request.referrer)


@blueprint.route('/resources/<resource_id>')
def resource(resource_id):
    """Show a resource."""
    resource_obj = app.db.resource(resource_id)

    if 'raw' in request.args:
        return send_from_directory(os.path.dirname(resource_obj.path),
                                   os.path.basename(resource_obj.path))

    return render_template('resource.html', resource=resource_obj)


@blueprint.route('/resource/delete/<resource_id>', methods=['POST'])
def delete_resource(resource_id):
    """Delete a resource."""
    resource_obj = app.db.resource(resource_id)
    try:
        os.remove(resource_obj.path)
    except OSError as err:
        app.logger.debug(err.message)

    app.db.delete_resource(resource_id)
    return redirect(request.referrer)


@blueprint.route('/individuals')
def individuals():
    """Show an overview of all individuals."""
    individual_objs = app.db.get_individuals()
    return render_template('individuals.html', individuals=individual_objs)


@blueprint.route('/individuals/<ind_id>')
def individual(ind_id):
    """Show details for a specific individual."""
    individual_obj = app.db.individual(ind_id)
    return render_template('individual.html', individual=individual_obj)
