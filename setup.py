import os
from setuptools import setup

def local_path(fname):
    return os.path.join(os.path.dirname(__file__), fname)

def read(fname):
    with open(local_path(fname)) as f:
        return f.read()

setup(
    name = "csv_utils",
    version = "0.0.1",
    author = "Yueran Yuan, Kaimin Chang",
    author_email = "yueranyuan@gmail.com",
    description = ("csv utilities"),
    packages=['csv_utils'],
    long_description=read('README.md'),
)
