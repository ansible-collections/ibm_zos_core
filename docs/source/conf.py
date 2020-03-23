##############################################################################
# © Copyright IBM Corporation 2020                                           #
##############################################################################

# Configuration file for the Sphinx documentation builder.
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------

project = 'IBM z/OS core collection'
copyright = '2020, IBM'
author = 'IBM'

# The full version, including alpha/beta/rc tags
release = '1.0.0'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx_rtd_theme",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['../templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = 'alabaster'
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the built-in "default.css".
# html_static_path = ['_static']

html_context = {
    "display_github": "True",
    "github_user": "ansible-collections",
    "github_repo": "ibm_zos_core",
    "github_version": "master",
    "conf_py_path": "/docs/source/",
}

# Not using these now but can see the doc here for them:
# https://sphinx-rtd-theme.readthedocs.io/en/latest/configuring.html and
# https://sphinx-rtd-theme.readthedocs.io/en/stable/
# html_theme_options = {
#      'canonical_url': '',
#      'analytics_id': 'UA-XXXXXXX-1',
#      'logo_only': False,
#      'display_version': True,
#      'prev_next_buttons_location': 'bottom',
#      'style_external_links': False,
#      'vcs_pageview_mode': '',
#      'style_nav_header_background': 'white',
#      # Toc options
#      'collapse_navigation': True,
#      'sticky_navigation': True,
#      'navigation_depth': 4,
#      'includehidden': True,
#      'titles_only': False
# }
