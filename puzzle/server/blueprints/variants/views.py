# -*- coding: utf-8 -*-
from flask import (abort, current_app as app, Blueprint, render_template,
                   request)

from puzzle.constants import (INHERITANCE_MODELS_SHORT, SO_TERMS, SV_TYPES,
                              IMPACT_LEVELS)

BP_NAME = __name__.split('.')[-2]
blueprint = Blueprint(BP_NAME, __name__, url_prefix='/variants',
                      template_folder='templates', static_folder='static',
                      static_url_path="/{}/static".format(BP_NAME))


@blueprint.route('/<case_id>')
def variants(case_id):
    """Show all variants for a case."""
    filters = parse_filters()
    is_active = any(value for value in filters.values()
                    if not isinstance(value, dict))
    variants = app.db.variants(
        case_id,
        skip=filters['skip'],
        filters={
            'gene_ids': filters['gene_symbols'],
            'frequency': filters.get('frequency'),
            'cadd': filters.get('cadd'),
            'sv_len': filters.get('sv_len'),
            'consequence': filters['selected_consequences'],
            'genetic_models': filters['selected_models'],
            'sv_types': filters['selected_sv_types'],
            'gene_lists': filters['gene_lists'],
            'impact_severities': filters['impact_severities'],
            'gemini_query': filters['gemini_query'],
        }
    )
    gene_lists = ([gene_list.list_id for gene_list in app.db.gene_lists()]
                  if app.config['STORE_ENABLED'] else [])
    kwargs = dict(variants=variants, case_id=case_id, db=app.db,
                  filters=filters, consequences=SO_TERMS,
                  inheritance_models=INHERITANCE_MODELS_SHORT,
                  gene_lists=gene_lists, impact_severities=IMPACT_LEVELS,
                  is_active=is_active)

    if app.db.variant_type == 'sv':
        return render_template('sv_variants.html', sv_types=SV_TYPES, **kwargs)
    else:
        return render_template('variants.html', **kwargs)


@blueprint.route('/<case_id>/<variant_id>')
def variant(case_id, variant_id):
    """Show a single variant."""
    variant = app.db.variant(case_id, variant_id)
    if variant is None:
        return abort(404, "variant not found")

    # sort compounds by score
    sorted_compounds = sorted(variant['compounds'],
                              key=lambda compound: compound['combined_score'])

    template = 'sv_variant.html' if app.db.variant_type == 'sv' else 'variant.html'
    return render_template(template, variant=variant,
                           compounds=sorted_compounds, case_id=case_id)


def parse_filters():
    """Parse variant filters from the request object."""
    genes_str = request.args.get('gene_symbol')
    filters = {}
    for key in ('frequency', 'cadd', 'sv_len'):
        try:
            filters[key] = float(request.args.get(key))
        except (ValueError, TypeError):
            pass

    filters['gene_symbols'] = genes_str.split(',') if genes_str else None
    filters['selected_models'] = request.args.getlist('inheritance_models')
    filters['selected_consequences'] = request.args.getlist('consequences')
    filters['selected_sv_types'] = request.args.getlist('sv_types')
    filters['skip'] = int(request.args.get('skip', 0))
    filters['gene_lists'] = request.args.getlist('gene_lists')
    filters['gemini_query'] = request.args.get('gemini_query')
    filters['impact_severities'] = request.args.getlist('impact_severities')

    filters['query_dict'] = {key: request.args.getlist(key) for key
                             in request.args.keys()}
    filters['query_dict'].update({'skip': (filters['skip'] + 30)})

    return filters
