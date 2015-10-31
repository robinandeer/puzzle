# -*- coding: utf-8 -*-
from flask import (abort, current_app as app, Blueprint, render_template,
                   request)

from puzzle.constants import INHERITANCE_MODELS_SHORT, SO_TERMS

BP_NAME = __name__.split('.')[-2]
blueprint = Blueprint(BP_NAME, __name__, url_prefix='/variants',
                      template_folder='templates', static_folder='static',
                      static_url_path="/{}/static".format(BP_NAME))


@blueprint.route('/<case_id>')
def variants(case_id):
    """Show all variants for a case."""
    filters = parse_filters()
    variants = app.db.variants(case_id, skip=filters['skip'],
                               frequency=filters.get('frequency'),
                               gene_list=filters['gene_symbols'],
                               cadd=filters.get('cadd'))

    return render_template('variants.html', variants=variants, case_id=case_id,
                           filters=filters, consequences=SO_TERMS,
                           inheritance_models=INHERITANCE_MODELS_SHORT)


@blueprint.route('/<case_id>/<variant_id>')
def variant(case_id, variant_id):
    """Show a single variant."""
    variant = app.db.variant(case_id, variant_id)
    if variant is None:
        return abort(404, "variant not found")

    # sort compounds by score
    sorted_compounds = sorted(variant['compounds'],
                              key=lambda compound: compound['combined_score'])
    return render_template('variant.html', variant=variant,
                           compounds=sorted_compounds, case_id=case_id)


def parse_filters():
    """Parse variant filters from the request object."""
    genes_str = request.args.get('gene_symbol')
    filters = {}
    for key in ('frequency', 'cadd'):
        try:
            filters[key] = float(request.args.get(key))
        except (ValueError, TypeError):
            pass

    filters['gene_symbols'] = genes_str.split(',') if genes_str else None
    filters['selected_models'] = request.args.getlist('inheritance_models')
    filters['selected_consequences'] = request.args.getlist('consequences')
    filters['skip'] = int(request.args.get('skip', 0))
    filters['query_dict'] = {key: request.args.getlist(key) for key
                             in request.args.keys()}
    filters['query_dict'].update({'skip': (filters['skip'] + 30)})
    return filters
