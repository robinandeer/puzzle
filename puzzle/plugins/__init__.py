# -*- coding: utf-8 -*-
from .base import Plugin
from .vcf import VcfPlugin
try:
    from .gemini import GeminiPlugin
except ImportError as e:
    pass
from .sql import Store as SqlStore
