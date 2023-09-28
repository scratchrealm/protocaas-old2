from setuptools import setup, find_packages, Command
from setuptools.command.install import install
from setuptools.command.develop import develop
import os
import subprocess

# read the contents of README.md
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

__version__ = '0.1.3'

setup(
    name='protocaas',
    version=__version__,
    author="Jeremy Magland",
    author_email="jmagland@flatironinstitute.org",
    url="https://github.com/scratchrealm/protocaas",
    description="Create, run, and share neuroscience analyses in the browser",
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(include=['protocaas', 'protocaas_sdk']),
    include_package_data=True,
    install_requires=[
        'click',
        'simplejson',
        'numpy',
        'PyYAML',
        'remfile',
        'pubnub>=7.2.0'
    ],
    entry_points={
        "console_scripts": [
            "protocaas=protocaas.cli:main",
        ],
    }
)