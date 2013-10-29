# -*- coding: utf8 -*- 

from ckan.lib.celery_app import celery
from logging import getLogger

from celery.schedules import crontab
from celery.task import periodic_task

from celery.signals import beat_init

import time
import json
import urlparse
import requests
import dateutil.parser

from datetime import timedelta, datetime
from celery.signals import beat_init
from swanalyzer.sparql_analyzer import SPARQLAnalyzer, check_sparql_endpoint
from requests.exceptions import ConnectionError

import os
import ConfigParser

#Configuration load
config = ConfigParser.ConfigParser()
config.read(os.environ['CKAN_CONFIG'])

MAIN_SECTION = 'app:main'
PLUGIN_SECTION = 'plugin:metadata'

DB_URL = config.get(MAIN_SECTION, 'sqlalchemy.url')
SITE_URL = config.get(MAIN_SECTION, 'ckan.site_url')
API_URL = urlparse.urljoin(SITE_URL, 'api/')
API_KEY = config.get(PLUGIN_SECTION, 'api_key')
CRON_HOUR = config.get(PLUGIN_SECTION, 'cron_hour')
CRON_MINUTE = config.get(PLUGIN_SECTION, 'cron_minute')

try:
    RUN_EVERY = config.get('plugin:metadata', 'run_every')
except ConfigParser.NoOptionError:
    RUN_EVERY = None

if RUN_EVERY is not None:
    print 'Launching periodic tasks every %s seconds' % RUN_EVERY
    periodicity = timedelta(seconds=int(RUN_EVERY))
else:
    print 'Launching periodic task at %s:%s' % (CRON_HOUR, CRON_MINUTE)
    periodicity = crontab(hour=CRON_HOUR, minute=CRON_MINUTE)
    
def get_task_status_value(task_status):
    if task_status[1] is None:
        return 'launched'
    elif task_status[1] is 'error':
        return 'error'
    else:
        return 'finished'

def get_tasks_status():
    tasks_status = {}

    packages = get_package_list()

    for package in packages:
        package_info = get_package_info(package)

        task_status = get_task_status(package_info['id'])
        if len(task_status) > 0:
            task_status_value = get_task_status_value(eval(task_status['value']))
            tasks_status[package_info['name']] = (task_status['id'], task_status_value)

    return tasks_status
    
def update_task_status(task_info):
    print "Updating task status for entity_id %s" % task_info['entity_id']
    res = requests.post(
        API_URL + 'action/task_status_update', json.dumps(task_info),
        headers = {'Authorization': API_KEY,
                   'Content-Type': 'application/json'}
    )

    if res.status_code == 200:
        return json.loads(res.content)['result']
    else:
        print 'ckan failed to update task_status, status_code (%s), error %s' % (res.status_code, res.content)
        return None

def delete_task_status(task_id):
    res = requests.post(
        API_URL + 'action/task_status_delete', json.dumps({'id': task_id}),
        headers = {'Authorization': API_KEY,
                   'Content-Type': 'application/json'}
    )

    if res.status_code == 200:
        return True
    else:
        print 'ckan failed to update task_status, status_code (%s), error %s' % (res.status_code, res.content)
	
        return False

def get_task_status(package_id):
    res = requests.post(
        API_URL + 'action/task_status_show', json.dumps({'entity_id': package_id, 'task_type': u'metadata', 'key': u'celery_task_status'}),
        headers = {'Authorization': API_KEY,
                   'Content-Type': 'application/json'}
    )

    if res.status_code == 200:
        return json.loads(res.content)['result']
    else:
	data = json.loads(res.content)
	if not data['error']['message'] == "Not found":
                print 'ckan failed to get task_status, status_code (%s), error %s' % (res.status_code, res.content)
        return {}

def updatePackage(package_info):
    updated_info = createUpdatedInfo(package_info)

    res = requests.post(
        API_URL + 'action/package_update', json.dumps(updated_info),
        headers = {'Authorization': API_KEY,
                   'Content-Type': 'application/json'}
    )

    if res.status_code == 200:
        return True
    else:
        print 'ckan failed to update package info, status_code (%s), error %s' % (res.status_code, res.content)
        return False

def updatePackageProperties(package_id, properties):
    data = {}
    data['package_id'] = package_id
    for key, value in properties.items():
        data[key] = value

    res = requests.post(
        API_URL + '2/update/package/properties', json.dumps(data),
        headers = {'Authorization': API_KEY,
                   'Content-Type': 'application/json'}
    )

    if res.status_code == 200:
        return True
    else:
        print 'ckan failed to update package properties, status_code (%s), error %s' % (res.status_code, res.content)
        return False

def update_vocab_count():
    res = requests.post(
        API_URL + '2/update/update_vocab_count', json.dumps({}),
        headers = {'Authorization': API_KEY,
                   'Content-Type': 'application/json'}
    )

    if res.status_code == 200:
        return True
    else:
        print 'ckan failed to update vocab_counting, status_code (%s), error %s' % (res.status_code, res.content)
        return False

def analyze_metadata(url):
    results = {}

    print 'Analyzing SPARQL endpoint on URL %s' % url
    
    try:
        if check_sparql_endpoint(url):
            
            sparql_analyzer = SPARQLAnalyzer(url)
            sparql_analyzer.open()

            sparql_analyzer.load_graph()

            results['accesible'] = str(True)

            try:
                results['subjects'] = sparql_analyzer.get_subjects_count()
            except:
                print 'Problem getting subjects of %s' %url
                pass

            try:
                results['objects'] = sparql_analyzer.get_objects_count()
            except:
                print 'Problem getting objects of %s' %url
                pass

            try:
                results['instances'] = sparql_analyzer.get_all_links_count()
            except:
                print 'Problem getting instances of %s' %url
                pass

            try:
                results['entities'] = sparql_analyzer.get_entities_count()
            except:
                print 'Problem getting entities of %s' %url
                pass

            try:
                results['triples'] = sparql_analyzer.get_triples_count()
            except:
                print 'Problem getting triples of %s' %url
                pass
                
            try:
                results['classes'] = str(sparql_analyzer.get_all_classes_instances())
            except:
                print 'Problem getting classes of %s' %url
                pass

            try:
                results['properties'] = str(sparql_analyzer.get_all_predicate_triples())
            except:
                print 'Problem getting properties of %s' %url
                pass

            try:
                results['all_links'] = sparql_analyzer.get_all_links_count()
            except:
                print 'Problem getting all links of %s' %url
                pass

            try:    
                results['ingoing_links'] = sparql_analyzer.get_ingoing_links_count()
            except:
                print 'Problem getting ingoing links of %s' %url
                pass

            try:
                results['outgoing_links'] = sparql_analyzer.get_outgoing_links_count()
            except:
                print 'Problem getting outgoing links of %s' %url
                pass

            try:
                results['inner_links'] = sparql_analyzer.get_inner_links_count()
            except:
                print 'Problem getting inner links of %s' %url
                pass

            try:
                vocab_count = {}
                for vocabulary in sparql_analyzer.get_vocabularies():
                    vocab_count[vocabulary] = 0

                results['vocabularies'] = str(vocab_count)
            except:
                print 'Problem getting vocabularies of %s' %url
                pass
            
            sparql_analyzer.close()
        else:
            results['accesible'] = str(False)

        print 'SPARQL endpoint analyzed'
    except:
        print 'Problem with SPARQL endpoint analysis detected'
        pass
    
    return results

def obtain_metadata(package_info):
    print 'Updating metadata for package %s' % package_info['name']

    metadata_timestamp = get_metadata_timestamp(package_info['id'])

    sparql_endpoint = (None, None)
    for resource in package_info['resources']:
        if resource['resource_type'] == 'api' and resource['format'].lower() == 'api/sparql':
            if resource['last_modified'] is None:
                last_modified = None
            else:
                last_modified = dateutil.parser.parse(resource['last_modified'])
            sparql_endpoint = (resource['url'], last_modified)
            break

    if metadata_timestamp is not None and sparql_endpoint[0] is not None and \
        sparql_endpoint[1] is not None and metadata_timestamp - sparql_endpoint[1] > 0:
        print 'Metadata was already calculated'
        return

    if sparql_endpoint[0] is not None:
        task_info = {
            'entity_id': package_info['id'],
            'entity_type': u'package',
            'task_type': u'metadata',
            'key': u'celery_task_status',
            'value': str((package_info['id'], None)),
            'error': u'',
            'last_updated': datetime.now().isoformat()
        }

        task_status = update_task_status(task_info)

        metadata = analyze_metadata(sparql_endpoint[0])

        updatePackageProperties(package_info['id'], metadata)

        print 'Metadata task finished for package %s' % package_info['name']

        update_vocab_count()

        task_info = {
            'id': task_status['id'],
            'entity_id': package_info['id'],
            'entity_type': u'package',
            'task_type': u'metadata',
            'key': u'celery_task_status',
            'value': str((package_info['id'], 'finished')),
            'error': u'',
            'last_updated': datetime.now().isoformat()       
        }

        update_task_status(task_info)

def get_package_list():
    res = requests.post(
        API_URL + 'action/package_list', json.dumps({}),
        headers = {'Authorization': API_KEY,
                   'Content-Type': 'application/json'}
    )

    if res.status_code == 200:
        return json.loads(res.content)['result']
    else:
        print 'ckan failed to get package list, status_code (%s), error %s' % (res.status_code, res.content)
        return ()

def get_package_info(package_name):
    res = requests.post(
        API_URL + 'action/package_show', json.dumps({'id': package_name}),
        headers = {'Authorization': API_KEY,
                   'Content-Type': 'application/json'}
    )

    if res.status_code == 200:
        return json.loads(res.content)['result']
    else:
        print 'ckan failed to show package information, status_code (%s), error %s' % (res.status_code, res.content)
        return {}

def get_metadata_timestamp(package_id):
    res = requests.post(
        API_URL + '2/get/get_metadata_timestamp', json.dumps({'package_id': package_id}),
        headers = {'Authorization': API_KEY,
                   'Content-Type': 'application/json'}
    )

    if res.status_code == 200:
        result = json.loads(res.content)
        if len(result) > 0:
            return dateutil.parser.parse((result['result']['timestamp']))
        else:
            return None
    else:
        print 'ckan failed to get metadata timestamp, status_code (%s), error %s' % (res.status_code, res.content)
        return None
        
def get_status_show():
    res = requests.post(
        API_URL + 'action/status_show', json.dumps({}),
        headers = {'Authorization': API_KEY,
                   'Content-Type': 'application/json'}
    )

    if res.status_code == 200:
        return json.loads(res.content)['result']
    else:
        print 'ckan failed to get status information, status_code (%s), error %s' % (res.status_code, res.content)
        return {}
        
@beat_init.connect 
def clear_broken_status_tasks(sender=None, conf=None, **kwargs):
    print 'Clearing broken status tasks'

    tasks_status = get_tasks_status()

    for _, (task_id, status) in tasks_status.items():
        if status == 'launched':
            print 'Deleting task %s with status %s' % (task_id, status)
            delete_task_status(task_id)


@periodic_task(run_every=periodicity)
def launch_metadata_calculation():  
                
    print 'Launching metadata periodic task'

    package_list = get_package_list()
    for package_name in package_list:
        package_info = get_package_info(package_name)

        task_status = get_task_status(package_info['id'])
        if len(task_status) == 0:
            task_status_value = None
        else:
            task_status_value = get_task_status_value(eval(task_status['value']))

        if task_status_value is None or task_status_value not in ('launched'):
            obtain_metadata(package_info)
        else:
            print 'Ignoring package %s because it was in status %s' % (package_info['name'], task_status_value)

