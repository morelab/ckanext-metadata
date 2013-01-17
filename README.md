ckanext-metadata
================

SPARQL endpoint analyzer and metadata generator for CKAN.

Tested with CKAN 1.8.

 Installation
--------------

**Install plugin**

    python setup.py install
    
**Update CKAN development.ini file to load the plugin**

    ckan.plugins = stats metadata

**Install dependencies**

    pip install -e git+https://github.com/memaldi/SWAnalyzer.git#egg=swanalyzer
    
**Initialize new tables on CKAN database**

    python ckanext/metadata/model/initDB.py
    
**Apply patch to CKAN code for adding periodic task support to paster launcher**

Copy patch content from https://gist.github.com/4547407 to a file named *beat_support.patch*
and execute next line on CKAN source directory

    git apply beat_support.patch
    
**Celery task queue initialization**
This plugin uses Celery (http://celeryproject.org/) for task queueing. 

First start the CKAN instance

    paster serve development.ini
    
Next, start the Celery server with

    paster celeryd run beat
