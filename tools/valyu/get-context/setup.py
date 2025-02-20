from setuptools import setup, find_packages

setup(
    name="get-context",
    description="Connect your AI agents to proprietary data sources and the web using the Valyu API.",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic",
        "valyu",
    ],
)