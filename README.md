ckanext-metadata
================

SPARQL endpoint analyzer and metadata generator for CKAN

 Installation
--------------

**Install plugin**

    python setup.py install
    
**Update CKAN development.ini file to load the plugin**

    ckan.plugins = stats metadata

**Install dependencies**

    pip install -e git+https://github.com/RDFLib/rdflib-postgresql.git#egg=rdflib_posgresql

    pip install -e git+https://github.com/memaldi/SWAnalyzer.git#egg=swanalyzer
    
**Initialize new tables on CKAN database**

    python ckanext/metadata/model/initDB.py
    
**Celery task queue initialization**
This plugin uses Celery (http://celeryproject.org/) for task queueing. 

First start the CKAN instance

    paster serve development.ini
    
Next, start the Celery server with

    paster celeryd
