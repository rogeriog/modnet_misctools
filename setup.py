import os, codecs
from setuptools import setup, find_packages
here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.1'
DESCRIPTION = '''Miscellaneous code to handle MODData, setup MODNet calculations, and other code
useful for MODNet implementation is provided.'''

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

# Setting up
setup(
    name="modnet_misctools",
    version=VERSION,
    author="Rogerio Gouvea",
    author_email="<rogeriog.em@gmail.com>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=requirements,
    include_package_data=True,
    zip_safe=False,
    long_description_content_type="text/markdown",
    long_description=long_description,
    keywords=['modnet','python', 'machine learning', 'MEGNet'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
    ]
)
