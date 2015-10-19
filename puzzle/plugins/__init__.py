# -*- coding: utf-8 -*-
from .base import Plugin
from .vcf import VcfPlugin
try:
    from .gemini_plugin import GeminiPlugin
except ImportError as e:
    pass