# -*- coding: utf-8 -*-
from .phenotype import PhenotypeActions
from .gemini import GeminiActions
from .genelist import GeneListActions
from .resource import ResourceActions


class ActionsMixin(PhenotypeActions, GeminiActions, GeneListActions,
                   ResourceActions):
    pass
