# -*- coding: utf8 -*- 

from ckan.lib.celery_app import celery
from logging import getLogger

from celery.schedules import crontab
from celery.task import periodic_task

import time
import json
import urlparse
import requests

from datetime import timedelta, datetime
from pmanager import get_task_status_value, createUpdatedInfo, createExtraProperty
from celery.signals import beat_init
from swanalyzer.sparql_analyzer import SPARQLAnalyzer, check_sparql_endpoint


SITE_URL = 'http://127.0.0.1:5000/'
API_URL = urlparse.urljoin(SITE_URL, 'api/action')

API_KEY = '5386a00d-d027-4233-8919-8c68e0ec1d04'

DB_USER = 'ckanuser'
DB_PASS = 'pass'

DB_HOST = 'localhost'
DB_NAME = 'rdfstore'

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
        API_URL + '/task_status_update', json.dumps(task_info),
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
        API_URL + '/task_status_delete', json.dumps({'id': task_id}),
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
        API_URL + '/task_status_show', json.dumps({'entity_id': package_id, 'task_type': u'metadata', 'key': u'celery_task_status'}),
        headers = {'Authorization': API_KEY,
                   'Content-Type': 'application/json'}
    )

    if res.status_code == 200:
        return json.loads(res.content)['result']
    else:
        print 'ckan failed to update task_status, status_code (%s), error %s' % (res.status_code, res.content)
        return {}

def updatePackage(package_info):
    updated_info = createUpdatedInfo(package_info)

    res = requests.post(
        API_URL + '/package_update', json.dumps(updated_info),
        headers = {'Authorization': API_KEY,
                   'Content-Type': 'application/json'}
    )

    if res.status_code == 200:
        return True
    else:
        print 'ckan failed to update package info, status_code (%s), error %s' % (res.status_code, res.content)
        return False

def analyze_metadata(url):
    results = {}

    print 'Analyzing SPARQL endpoint on URL %s' % url

    if check_sparql_endpoint(url):
        sparql_analyzer = SPARQLAnalyzer(url, 'turismo', 'user=ckanuser password=pass host=localhost dbname=rdfstore', None, False)
        sparql_analyzer.open()

        sparql_analyzer.load_graph()

        results['accesible'] = str(True)

        properties = sparql_analyzer.get_properties()

        results['classes'] = len(sparql_analyzer.get_classes())
        results['properties'] = len(properties)
        results['subjects'] = len(sparql_analyzer.get_subjects())
        results['objects'] = len(sparql_analyzer.get_objects())
        results['instances'] = len(sparql_analyzer.get_all_links())
        results['entities'] = len(sparql_analyzer.get_entities())
        # results['linksets'] = sparql_analyzer.get_linksets()

        class_dict = {}
        for c in sparql_analyzer.get_classes():
            c = c[0]
            class_dict[c] = len(sparql_analyzer.get_class_instances(c))
        results['class_instances'] = str(class_dict)

        property_dict = {}
        for p in sparql_analyzer.get_properties():
            p = p[0]
            property_dict[p] = len(sparql_analyzer.get_property_count(p))
        results['property_count'] = str(property_dict)

        results['triples'] = len(sparql_analyzer.get_triples())
        results['all_links'] = len(sparql_analyzer.get_all_links())
        results['ingoing_links'] = len(sparql_analyzer.get_inner_links())
        results['outgoing_links'] = len(sparql_analyzer.get_inner_links())
        results['inner_links'] = len(sparql_analyzer.get_inner_links())

        property_list = [str(p[0].encode('utf-8')) for p in properties]
        results['vocabularies'] = str(sparql_analyzer.get_patterns(property_list))

        sparql_analyzer.close()
    else:
        results['accesible'] = str(False)

    return results

def update_metadata(package_info, metadata):
    metadata_keys = []
    for key, value in metadata.items():
        createExtraProperty(package_info, key, value)
        metadata_keys.append(key)

    createExtraProperty(package_info, 'metadata_keys', str(metadata_keys))

    return updatePackage(package_info)

def obtain_metadata(package_info):
    print 'Updating metadata for package %s' % package_info['id']

    sparql_endpoints = []
    for resource in package_info['resources']:
        if resource['resource_type'] == 'api' and resource['format'] == 'API/SPARQL':
            sparql_endpoints.append(resource['url'])

    if len(sparql_endpoints) > 0:
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

        results = analyze_metadata(sparql_endpoints[0])

        error = update_metadata(package_info, results)

        print 'Metadata task finished for package %s' % package_info['id']

        time.sleep(5)

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

        results['sparql_endpoints'] = len(sparql_endpoints)

def get_package_list():
    res = requests.post(
        API_URL + '/package_list', json.dumps({}),
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
        API_URL + '/package_show', json.dumps({'id': package_name}),
        headers = {'Authorization': API_KEY,
                   'Content-Type': 'application/json'}
    )

    if res.status_code == 200:
        return json.loads(res.content)['result']
    else:
        print 'ckan failed to show package information, status_code (%s), error %s' % (res.status_code, res.content)
        return {}

#@periodic_task(run_every=crontab(hour=9, minute=35))
@periodic_task(run_every=timedelta(seconds=30))
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
            print 'Ignoring package %s because it was in status %s' % (package_info['id'], task_status_value)

def clear_pending_tasks():
    print 'Clearing pending tasks'

    tasks_status = get_tasks_status()

    for _, (task_id, status) in tasks_status.items():
        if status == 'launched':
            print 'Deleting task %s with status %s' % (task_id, status)
            delete_task_status(task_id)

clear_pending_tasks()