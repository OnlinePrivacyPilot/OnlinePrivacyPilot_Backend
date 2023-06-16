from setuptools import setup, find_packages

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
        "flask",
        "flask_cors",
        "marshmallow",
        "asciitree",
        "pyinstaller"
    ],
    extras_require={
        "dev": [
            "pytest",
        ]
    },
    entry_points={
        'console_scripts': [
            'oppcli=opp.cli_client:run',
            'oppapi=opp.rest_api:run'
        ]
    }
)
