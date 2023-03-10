# https://www.sphinx-doc.org/en/master/usage/configuration.html

project = "Runcrate"
author = "CRS4"
copyright = f"2022-2023 {author}"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx_click",
]

exclude_patterns = [
    "Thumbs.db",
    ".DS_Store"
]

html_theme = "sphinx_rtd_theme"
autoclass_content = "both"
