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
from pmanager import get_task_status_value
from celery.signals import beat_init
from swanalyzer.sparql_analyzer import SPARQLAnalyzer


SITE_URL = 'http://127.0.0.1:5000/'
API_URL = urlparse.urljoin(SITE_URL, 'api/action')

API_KEY = 'b1d895d3-5187-491c-8826-4c7f63fe84ab'

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

def analyze_metadata(url):
    results = {}

    print 'Analyzing SPARQL endpoint on URL %s' % url
    sparql_analyzer = SPARQLAnalyzer(url, 'data', 'user=ckanuser password=pass host=localhost dbname=rdfstore')
    sparql_analyzer.open()

    sparql_analyzer.load_graph()

    results['classes'] = len(sparql_analyzer.get_classes())
    results['properties'] = len(sparql_analyzer.get_properties())
    results['subjects'] = len(sparql_analyzer.get_subjects())
    results['objects'] = len(sparql_analyzer.get_objects())
    results['instances'] len(sparql_analyzer.get_all_links())
    results['entities'] = len(sparql_analyzer.get_entities())
    results['outgoing_links'] = len(sparql_analyzer.get_outgoing_links())
    results['linksets'] = sparql_analyzer.get_linksets()

    results['class_instances'] = {}
    for c in sparql_analyzer.get_classes():
        results['class_instances'][c] = sparql_analyzer.get_class_instances(c)

    results['property_count'] = {}
    for p in sparql_analyzer.get_properties():
        results['property_count'][p] = sparql_analyzer.get_property_count(p)

    sparql_analyzer.close()

    return results

def obtain_metadata(package_info):
    print 'Updating metadata for package %s' % package_info['id']

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

    for resource in package_info['resources']:
        if resource['resource_type'] == 'api' and resource['format'] == 'API/SPARQL':
            analyze_metadata(resource['url'])

    print 'Metadata task finished for package %s' % package_info['id']

    task_info = {
        'id': task_status['id'],
        'entity_id': package_info['id'],
        'entity_type': u'package',
        'task_type': u'metadata',
        'key': u'celery_task_status',
        'value': str((package_info['id'], "Hello world")),
        'error': u'',
        'last_updated': datetime.now().isoformat()       
    }

    update_task_status(task_info)

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
            print 'Ignoring package %s because it was in status %s' % (package_name, task_status_value)

def clear_pending_tasks():
    print 'Clearing pending tasks'

    task_status = get_tasks_status()

    for _, (task_id, status) in task_status.items():
        if status == 'launched':
            print 'Deleting task %s with status %s' % (task_id, status)
            delete_task_status(task_id)

clear_pending_tasks()