import os
import sys
sys.path.insert(0, os.path.abspath('../../'))

project = 'carnival contrib'
copyright = '2020, a1fred'
author = 'a1fred'

html_theme_options = {
    "page_width": "1024px",
}

extensions = [
    'sphinx.ext.autodoc',
]
autodoc_mock_imports = [
]

master_doc = 'index'
autodoc_default_flags = ['members', ]
templates_path = ['_templates']
language = 'ru'
exclude_patterns = []
html_theme = 'alabaster'
html_static_path = ['_static']
