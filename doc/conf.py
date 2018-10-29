import sys
import os
import os.path

# sys.path.append( "@sphinx_breathe_path@")

extensions = [
    "sphinx.ext.todo",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon", # Markdown autodoc like in Numpy docu.
    "sphinx.ext.mathjax",
    "sphinxcontrib.bibtex",
    # "sphinx.ext.autosectionlabel"
]

# The suffix(es) of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'tutorial'

# General information about the project.
project = 'visr-code-tutorial'
copyright = '2018, S3A'
author = 'S3A'

# Add Python packages for documentation, for example visr_bst
# <af> Document __init__ method
autoclass_content = 'both'
autodoc_default_options = {
    'special-members': '__init__'
}

# Add the VISR Python modules to the module search path.
# We insert them to the front of the list to have precedence over other VISR paths 
# that might already be in the path, e.g., through PYTHONHOME)
# TODO: insert path to the built C++ Python externals (this requires a generator expression)
sys.path.insert( 0, "/usr/share/visr/python" )

# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'classic'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = []

def setup(app):
  app.add_stylesheet('css/custom.css')

# .. doxygenclass:: PointSource
#    :project: visr

# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    'papersize': 'a4paper',
    'author': 'The S3A team',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'visr.tex', u'VISR User documentation',
     u'The S3A project team', 'manual'),
]
