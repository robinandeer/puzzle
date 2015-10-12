# -*- coding: utf-8 -*-
from flask import abort, Blueprint, jsonify, render_template, request
from puzzle.ext import db

BP_NAME = __name__.split('.')[-2]
blueprint = Blueprint(BP_NAME, __name__, url_prefix='/variants',
                      template_folder='templates', static_folder='static',
                      static_url_path="/{}/static".format(BP_NAME))


@blueprint.route('/<case_id>')
def variants(case_id):
    """Show the landing page."""
    gene_list = request.args.get('gene_list')

    skip = int(request.args.get('skip', 0))
    next_skip = skip + 30
    variants = db.variants(case_id, skip=skip, gene_list=gene_list)
    return render_template('variants.html', variants=variants,
                           next_skip=next_skip, case_id=case_id)


@blueprint.route('/<case_id>/<variant_id>')
def variant(case_id, variant_id):
    """Show a single variant."""
    variant = db.variant(case_id, variant_id)
    if variant is None:
        return abort(404, "variant not found")

    # sort compounds by score
    sorted_compounds = sorted(variant['compounds'],
                              key=lambda compound: compound['combined_score'])
    return render_template('variant.html', variant=variant,
                           compounds=sorted_compounds, ase_id=case_id)
