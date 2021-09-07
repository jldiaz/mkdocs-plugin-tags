# --------------------------------------------
# Setup file for the package
#
# JL Diaz (c) 2019
# --------------------------------------------

import os
from setuptools import setup, find_packages


def read_file(fname):
    "Read a local file"
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='mkdocs-plugin-tags',
    version='0.4.0',
    description="Processes tags in yaml metadata",
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    keywords='mkdocs python markdown tags',
    url='',
    author='JL Diaz',
    author_email='jldiaz@gmail.com',
    license='MIT',
    python_requires='>=3.6',
    install_requires=[
        'mkdocs>=1.1',
        'jinja2',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(exclude=['*.tests']),
    package_data={'tags': ['templates/*.md.template']},
    entry_points={
        'mkdocs.plugins': [
            'tags = tags.plugin:TagsPlugin'
        ]
    }
)
