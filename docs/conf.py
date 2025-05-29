import os
import sys

sys.path.insert(0, os.path.abspath("../src"))

project = "Climate Compare"
author = "Auto-Generated"
release = "0.1"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinxcontrib.plantuml",
]

templates_path = ["_templates"]
exclude_patterns = []

html_theme = "sphinx_rtd_theme"

plantuml = "java -jar ./plantuml.jar"
