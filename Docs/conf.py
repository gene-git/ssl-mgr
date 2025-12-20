# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
latex_engine = 'xelatex'

project = "ssl-mgr"
copyright = '2023-%Y, Gene C'
author = 'Gene C'
release = '7.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
suppress_warnings = ['toc.not_included']
exclude_patterns = ['**/Changelog.rst', 'Misc/*.rst']

#extensions = ['myst_parser']
#latex_engine = "xelatex"
latex_engine = "lualatex"
latex_elements = {
        'preamble': r'''
        \usepackage{polyglossia}
        \setdefaultlanguage{english}
        \usepackage[utf8]{inputenc}
        \usepackage{newunicodechar}''',
}
extensions = []

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
