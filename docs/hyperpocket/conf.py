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

sys.path.insert(0, os.path.abspath('../../libs/hyperpocket/'))

project = 'hyperpocket'
copyright = '2025, vessl-ai'
author = 'vessl-ai'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'autoapi.extension',
    "sphinx.ext.githubpages",
    'sphinx_mdinclude',

]

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# autoapi config
autoapi_type = 'python'
autoapi_dirs = ['../../libs/hyperpocket/hyperpocket']
autoapi_ignore = ["**/tests/*"]
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
    autoapi_root = Path("./autoapi/hyperpocket").resolve()
    package_dirs = Path("../../libs/hyperpocket").rglob("**/readme.md")

    for readme_path in package_dirs:
        readme_path = readme_path.resolve()
        parts: list = readme_path.parts
        base_index = len(parts) - 1 - parts[::-1].index("hyperpocket")
        package_path = Path(*parts[base_index + 1:-1])

        if package_path.name.startswith("."):
            continue

        target_readme_dir = autoapi_root / package_path
        target_readme = target_readme_dir / "README.md"

        if not os.path.exists(target_readme_dir):
            os.makedirs(target_readme_dir)

        with open(readme_path, "r", encoding="utf-8") as f_md:
            readme_content = f_md.read()
        with open(target_readme, "w", encoding="utf-8") as f_target_readme:
            f_target_readme.write(readme_content)


def copy_managed_md(app: Sphinx, config):
    autoapi_root = Path("./autoapi").resolve()
    package_dirs = Path("./managed").rglob("**/*.md")

    for file_path in package_dirs:
        target_readme = autoapi_root / file_path

        if not os.path.exists(target_readme.parent):
            os.makedirs(target_readme.parent)

        with open(file_path, "r", encoding="utf-8") as f_md:
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
    sphinx.connect("config-inited", copy_managed_md)
    sphinx.connect("autoapi-skip-member", remove_default_docstring)


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
