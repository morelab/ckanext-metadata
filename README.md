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

**Add plugin configuration variables to CKAN development.ini**

Append this configuration snippet to the file. Do not forget to **change the admin API** key with yours.

	[plugin:metadata]
	#admin api key used for connection from celery
	api_key = 5386a00d-d027-4233-8919-8c68e0ec1d04 # change this API key

	#run every s seconds, for debugging purposes
	#run_every = 30

	#metadata analyzer task cron
	cron_hour = 03
	cron_minute = 00
    
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
