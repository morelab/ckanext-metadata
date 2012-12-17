# -*- coding: utf8 -*- 

from ckan.lib.celery_app import celery
from logging import getLogger

from celery.schedules import crontab
from celery.task import periodic_task

from pmanager import updateExtraProperty

import time
import json
import urlparse
import requests

from datetime import timedelta, datetime

SITE_URL = 'http://127.0.0.1:5000/'
API_URL = urlparse.urljoin(SITE_URL, 'api/action')

API_KEY = 'b1d895d3-5187-491c-8826-4c7f63fe84ab'

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
        return ()

def update_metadata(package_info):
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

    time.sleep(5)

    print 'Metadata task finished for package %s' % package_info['id']
    #update package status
    #updateExtraProperty(package_info, 'metadata_task_status', 'updated')

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
        return ()

#@periodic_task(run_every=crontab(hour=9, minute=35))
@periodic_task(run_every=timedelta(seconds=30))
def launch_metadata_calculation():
    print 'Launching metadata periodic task'

    package_list = get_package_list()
    for package_name in package_list:
        package_info = get_package_info(package_name)
        update_metadata(package_info)