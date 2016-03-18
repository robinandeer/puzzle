# -*- coding: utf-8 -*-
from .phenotype import PhenotypeActions
from .gemini import GeminiActions
from .genelist import GeneListActions
from .resource import ResourceActions
from .comment import CommentActions
from .suspect import SuspectActions

class ActionsMixin(PhenotypeActions, GeminiActions, GeneListActions,
                   ResourceActions, CommentActions, SuspectActions):
    pass
