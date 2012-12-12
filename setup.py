from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(
	name='ckanext-linkeddata',
	version=version,
	description="Metadata generator and visualization for ADAPTA",
	long_description="""\
	""",
	classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
	keywords='',
	author='Unai Aguilera',
	author_email='unai.aguilera@deusto.es',
	url='http://www.morelab.deusto.es',
	license='GPL',
	packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
	namespace_packages=['ckanext', 'ckanext.linkeddata'],
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		# -*- Extra requirements: -*-
	],
	entry_points=\
	"""
    [ckan.plugins]
		# Add plugins here, eg
		metadata=ckanext.linkeddata.plugin:MetadataExtension
		
	[ckan.celery_task]
		tasks = ckanext.linkeddata.celery_import:task_imports
	""",
)
