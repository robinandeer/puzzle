# -*- coding: utf-8 -*-
from flask import abort, Blueprint, jsonify, render_template, request
from puzzle.ext import db

BP_NAME = __name__.split('.')[-2]
blueprint = Blueprint(BP_NAME, __name__, url_prefix='/variants',
                      template_folder='templates', static_folder='static',
                      static_url_path="/{}/static".format(BP_NAME))


@blueprint.route('/')
def variants():
    """Show the landing page."""
    vcf_file = request.args.get('vcf_file')
    if vcf_file:
        db.load_vcf(vcf_file)
    gene_list = request.args.get('gene_list')

    skip = int(request.args.get('skip', 0))
    next_skip = skip + 30
    variants = db.variants(skip=skip, gene_list=gene_list)
    return render_template('variants.html', variants=variants,
                           next_skip=next_skip)


@blueprint.route('/<variant_id>')
def variant(variant_id):
    """Show a single variant."""
    variant = db.variant(variant_id)
    if variant is None:
        return abort(404, "variant not found")
    return render_template('variant.html', variant=variant)


@blueprint.route('/api/v1/variants/<variant_id>')
def api_variant(variant_id):
    """Show a single variant."""
    variant = db.variant(variant_id)
    return jsonify(variant)
