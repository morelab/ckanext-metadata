from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(
    name='ckanext-metadata',
    version=version,
    description="SPARQL endpoint analyzer and metadata generator for CKAN",
    long_description="""\
    """,
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Unai Aguilera',
    author_email='unai.aguilera@deusto.es',
    url='http://www.morelab.deusto.es',
    license='AGPL',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext', 'ckanext.metadata'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'celery==2.4.2',
        'requests',
        'swanalyzer'
    ],
    dependency_links=[
        "https://github.com/memaldi/SWAnalyzer/tarball/master#egg=swanalyzer",
    ],
    entry_points=\
    """
    [ckan.plugins]
        metadata=ckanext.metadata.plugin:MetadataExtension
        
    [ckan.celery_task]
        tasks = ckanext.metadata.celery_import:task_imports
    """,
)
