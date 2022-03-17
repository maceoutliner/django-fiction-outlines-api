#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def get_version(*file_paths):
    """Retrieves the version from fiction_outlines_api/__init__.py"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


version = get_version("fiction_outlines_api", "__init__.py")


if sys.argv[-1] == 'publish':
    try:
        import wheel
        print("Wheel version: ", wheel.__version__)
    except ImportError:
        print('Wheel library missing. Please run "pip install wheel"')
        sys.exit()
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()

if sys.argv[-1] == 'tag':
    print("Tagging the version on git:")
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags")
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='django-fiction-outlines-api',
    version=version,
    description="""A RESTful JSON API for django-fiction-outlines. Part of the broader maceoutliner project.""",
    long_description=readme + '\n\n' + history,
    author='Daniel Andrlik',
    author_email='daniel@andrlik.org',
    url='https://github.com/andrlik/django-fiction-outlines-api',
    packages=[
        'fiction_outlines_api',
    ],
    include_package_data=True,
    install_requires=[
        'django-fiction-outlines>=0.4',
        'django-rest-framework-rules',
        'djangorestframework',
        'coreapi',
        'django-filter',
        'Markdown',
    ],
    license="BSD",
    zip_safe=False,
    keywords='django-fiction-outlines-api',
    project_urls={
        'Documenation': 'http://django-fiction-outlines-api.readthedocs.io/en/latest/index.html',
        'Source': 'https://github.com/maceoutliner/django-fiction-outlines-api/',
        'Issue Tracker': 'https://github.com/maceoutliner/django-fiction-outlines-api/issues',
    },
    python_requires='~=3.9',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
