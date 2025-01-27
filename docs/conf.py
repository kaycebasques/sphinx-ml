import json
import os


def get_version():
    cwd = os.path.abspath(os.path.dirname(__file__))
    with open(f'{cwd}/../sphinx-ml/version.json', 'r') as f:
        return json.load(f)['version']


# Metadata
project = 'sphinx-ml'
copyright = '2025, Kayce Basques'
author = 'Kayce Basques'
version = get_version()
release = version


# General
templates_path = ['_templates']
exclude_patterns = ['_build']


# Extensions
extensions = ['sphinx-ml']
# sphinx-ml
sphinx_ml_gemini_api_key = os.environ.get('GEMINI_API_KEY')

# HTML theme
html_theme = 'alabaster'
