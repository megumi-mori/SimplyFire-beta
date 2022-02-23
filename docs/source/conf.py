# Configuration file for the Sphinx documentation builder.
import os
# -- Project information

project = u'SimplyFire'
copyright = u'2022, Megumi Mori'
author = u'Megumi Mori'

release = '0.3'
version = '0.3.0'

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']
master_doc = 'index'
exclude_patterns = ['_build']
pygments_style = 'sphinx'
# -- Options for HTML output
# import sphinx_rtd_theme
html_theme = 'default'
# html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
# on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
#
# if not on_rtd:  # only import and set the theme if we're building docs locally
import sphinx_rtd_theme
html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

html_static_path = ['_static', 'plugin_gui/_static']

# -- Options for EPUB output
epub_show_urls = 'footnote'
