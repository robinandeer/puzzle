# -*- coding: utf-8 -*-
import os

from flask import (abort, Blueprint, current_app as app, render_template,
                   redirect, request, url_for, make_response,
                   send_from_directory, flash)
from werkzeug import secure_filename

from puzzle.models.sql import Case

BP_NAME = __name__.split('.')[-2]
blueprint = Blueprint(BP_NAME, __name__, template_folder='templates',
                      static_folder='static',
                      static_url_path="/{}/static".format(BP_NAME))


@blueprint.route('/')
def index():
    """Show the landing page."""
    gene_lists = app.db.gene_lists() if app.config['STORE_ENABLED'] else []
    queries = app.db.gemini_queries() if app.config['STORE_ENABLED'] else []

    case_groups = {}
    for case in app.db.cases():
        key = (case.variant_source, case.variant_type, case.variant_mode)
        if key not in case_groups:
            case_groups[key] = []
        case_groups[key].append(case)

    return render_template('index.html', case_groups=case_groups,
                           gene_lists=gene_lists, queries=queries)


@blueprint.route('/cases/<case_id>')
def case(case_id):
    """Show the overview for a case."""
    case_obj = app.db.case(case_id)
    return render_template('case.html', case=case_obj, case_id=case_id)


@blueprint.route('/phenotypes', methods=['POST'])
def phenotypes():
    """Add phenotype(s) to the case model."""
    ind_id = request.form['ind_id']
    phenotype_id = request.form['phenotype_id']

    if not phenotype_id:
        return abort(500, 'no phenotype_id submitted')

    ind_obj = app.db.individual(ind_id)
    try:
        added_terms = app.db.add_phenotype(ind_obj, phenotype_id)
        if added_terms is None:
            flash("Term with id {} was not found".format(phenotype_id),
                  'danger')
        elif added_terms == []:
            flash("Term with id {} was already added".format(phenotype_id),
                  'warning')
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


@blueprint.route('/<case_id>/comments', methods=['POST'])
def comments(case_id):
    """Upload a new comment."""
    text = request.form['text']
    variant_id = request.form.get('variant_id')
    username = request.form.get('username')
    case_obj = app.db.case(case_id)
    app.db.add_comment(case_obj, text, variant_id=variant_id, username=username)
    return redirect(request.referrer)


@blueprint.route('/comments/<comment_id>', methods=['POST'])
def delete_comment(comment_id):
    """Delete a comment."""
    app.db.delete_comment(comment_id)
    return redirect(request.referrer)


@blueprint.route('/individuals')
def individuals():
    """Show an overview of all individuals."""
    individual_objs = app.db.individuals()
    return render_template('individuals.html', individuals=individual_objs)


@blueprint.route('/individuals/<ind_id>')
def individual(ind_id):
    """Show details for a specific individual."""
    individual_obj = app.db.individual(ind_id)
    return render_template('individual.html', individual=individual_obj)


@blueprint.route('/<case_id>/synopsis', methods=['POST'])
def synopsis(case_id):
    """Update the case synopsis."""
    text = request.form['text']
    case_obj = app.db.case(case_id)
    app.db.update_synopsis(case_obj, text)
    return redirect(request.referrer)


@blueprint.route('/cases', methods=['POST'])
def add_case():
    """Make a new case out of a list of individuals."""
    ind_ids = request.form.getlist('ind_id')
    case_id = request.form['case_id']
    source = request.form['source']
    variant_type = request.form['type']

    if len(ind_ids) == 0:
        return abort(400, "must add at least one member of case")

    # only GEMINI supported
    new_case = Case(case_id=case_id, name=case_id, variant_source=source,
                    variant_type=variant_type, variant_mode='gemini')

    # Add individuals to the correct case
    for ind_id in ind_ids:
        ind_obj = app.db.individual(ind_id)
        new_case.individuals.append(ind_obj)

    app.db.session.add(new_case)
    app.db.save()

    return redirect(url_for('.case', case_id=new_case.name))
