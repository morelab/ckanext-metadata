ckanext-metadata
================

SPARQL endpoint analyzer and metadata generator for CKAN

 Installation
--------------

**Install plugin**

    python setup.py install

**Install dependencies**

    pip install -e git+https://github.com/RDFLib/rdflib-postgresql.git#egg=rdflib_posgresql

    pip install -e git+https://github.com/memaldi/SWAnalyzer.git#egg=swanalyzer
    
**Create new tables on CKAN database for calculated properties storage**

    python ckanext/metadata/model/initDB.py
