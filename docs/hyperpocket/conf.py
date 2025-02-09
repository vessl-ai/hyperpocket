# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
from pathlib import Path

import jinja2
from sphinx.application import Sphinx

sys.path.insert(0, os.path.abspath("../../libs/"))

project = "Hyperpocket"
copyright = "2025, VESSL AI Inc."
author = "hyperpocket@vessl.ai"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "autoapi.extension",
    "sphinx.ext.githubpages",
    # "sphinx_mdinclude",
    "myst_parser",
]

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# autoapi config
autoapi_type = "python"
autoapi_dirs = ["../../libs/"]
# 제외 규칙 설정
autoapi_ignore = [
    "**/test/**",
    "**/tests/**",
    "**/.venv/**",
]
autoapi_add_toctree_entry = True
autoapi_options = [
    "members",
    "undoc-members",
    "show-inheritance",
    "show-module-summary",
    "imported-members",
]
autodoc_typehints = "signature"
autoapi_template_dir = "./_templates/autoapi"
autoapi_keep_files = False

# napoleon config
napoleon_google_docstring = True
napoleon_numpy_docstring = True

html_context = {
    "display_github": True,  # Integrate GitHub
    "github_user": "vessl-ai",  # Username
    "github_repo": "hyperpocket",  # Repo name
    "github_version": "main",  # Version
    "conf_py_path": "/docs/hyperpocket/",  # Path in the checkout to the docs root
}


# set jinja custom filter
def autoapi_prepare_jinja_env(jinja_env: jinja2.Environment):
    def file_exists(path, filename):
        current_path = Path(".").resolve()
        package_path = Path(path[1:])  # remove /
        package_path = Path(*package_path.parts[:-1])  # remove /index
        file_path = current_path / package_path / filename

        is_exists = file_path.exists()
        if is_exists:
            print(f"autoapi file exists : {str(file_path)}")
        return is_exists

    jinja_env.filters["file_exists"] = file_exists


# set event
def copy_readme(app: Sphinx, config):
    autoapi_root = Path("./autoapi").resolve()
    package_dirs = Path("../../libs/").rglob("**/readme.md")

    for readme_path in package_dirs:
        readme_path = readme_path.resolve()

        if ".venv" in str(readme_path) or ".pytest_cache" in str(readme_path):
            continue

        parts: list = readme_path.parts

        base_index = -1

        for i in range(len(parts)):
            if parts[i] == "libs":
                base_index = i
                break

        if base_index == -1:
            continue

        package_path = Path(*parts[base_index:])
        target_readme = autoapi_root / package_path
        print("make readme in ", target_readme)

        if not os.path.exists(target_readme.parent):
            os.makedirs(target_readme.parent)

        with open(readme_path, "r", encoding="utf-8") as f_md:
            readme_content = f_md.read()
        with open(target_readme, "w", encoding="utf-8") as f_target_readme:
            f_target_readme.write(readme_content)


def remove_default_docstring(app, what, name, obj, skip, options):
    if what == "class" and obj is not None:
        if "A base class for creating Pydantic models." in obj._docstring:
            obj._docstring = ""

        elif obj._docstring.startswith("Create a collection of name/value pairs."):
            obj._docstring = ""

    return skip


def setup(sphinx: Sphinx):
    sphinx.connect("config-inited", copy_readme)
    sphinx.connect("autoapi-skip-member", remove_default_docstring)


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_permalinks_icon = '<span>#</span>'
html_theme = 'sphinxawesome_theme'
html_static_path = ["_static"]
