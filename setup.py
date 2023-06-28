from setuptools import setup, find_packages
from setuptools.command.install import install
import importlib


setup(
    name="opp",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "beautifulsoup4",
        "google-api-python-client",
        "simple_graph_sqlite",
        "sphinx",
        "selenium",
        "chromedriver_binary",
        "httpx",
        "holehe",
        "ignorant",
        "jinja2",
        "flask",
        "flask_cors",
        "marshmallow",
        "asciitree",
        "pyinstaller"
    ],
    entry_points={
        'console_scripts': [
            'oppcli=opp.cli_client:run',
            'oppapi=opp.rest_api:app.run'
        ]
    },
)
