import os
import sys
sys.path.insert(0, os.path.abspath('../../src/proofpoint_itm'))

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'proofpoint_itm'
copyright = '2023, Mike Olden'
author = 'Mike Olden'
release = '0.4.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx_rtd_theme', # Read the Docs theme
    'sphinx.ext.autodoc',  # Automatically generate documentation from docstrings
    'sphinx.ext.autosummary', # Create neat summary tables
    'sphinx.ext.napoleon',  # Support for NumPy and Google style docstrings
]

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
