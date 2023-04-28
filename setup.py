from setuptools import setup, find_packages
from setuptools.command.build_py import build_py
from setuptools.command.build_ext import build_ext
from distutils.cmd import Command
import subprocess

"""
By doing this, we ensure that the documentation is built before the Python source files are copied to the build directory. 
This way, the documentation is included in the final package along with the Python source files.
"""

class BuildDocs(Command):
    description = 'Build the documentation using Sphinx'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        subprocess.call(['sphinx-build', '-b', 'html', 'docs/source', 'docs/build'])

class CustomBuild(build_py):
    """
    Override the build_py command to also build the documentation.
    """
    def run(self):
        self.run_command('build_ext')
        self.run_command('build_docs')
        build_py.run(self)

setup(
    name="src",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "beautifulsoup4",
        "spacy",
        "google-api-python-client",
        "simple_graph_sqlite",
        "sphinx",
        "selenium",
        "webdriver-manager"
    ],
    extras_require={
        "dev": [
            "pytest",
        ]
    },
    entry_points={
        'console_scripts': [
            'oppcli=src.cli_client:run',
            'oppapi=src.rest_api:run'
        ]
    },
    cmdclass={
        'build_docs': BuildDocs,
        'build_py': CustomBuild,
    },
)
