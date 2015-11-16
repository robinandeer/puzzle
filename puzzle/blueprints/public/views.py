# -*- coding: utf-8 -*-
from flask import Blueprint, current_app as app, render_template

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
    return render_template('case.html', case=app.db.case(), case_id=case_id)
