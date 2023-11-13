# Run this by calling
#     python setup.py sdist bdist_wheel # old way to build a package
#     or
#     python -m build                   # new way to build a package

import os
from setuptools import setup, find_packages

install_deps = ['pip', 'numba', 'pandas', 'numpy', 'scikit-image']

version = None
with open(os.path.join('merfish_python_pons', '_version.py'), 'r') as fid:
    for line in (line.strip() for line in fid):
        if line.startswith('__version__'):
            version = line.split('=')[1].strip().strip('\'')
            break
if version is None:
    raise RuntimeError('Could not determine version')

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="merfish_pons",
    version=version,
    license="BSD",
    author="Dimitris Nicoloutsopoulos",
    author_email="dimitris.nicoloutsopoulos@gmail.com",
    description="Merfish python pons",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/acycliq/cell_by_gene",
    packages=find_packages(),
    install_requires=install_deps,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
)