import os
import sys
sys.path.insert(0, os.path.abspath('.'))

project = 'carnival contrib'
copyright = '2020, a1fred'
author = 'a1fred'

extensions = [
    'sphinx.ext.autodoc',
]
autodoc_mock_imports = [
    'carnival',
]
templates_path = ['_templates']
language = 'ru'
exclude_patterns = []
html_theme = 'alabaster'
html_static_path = ['_static']
