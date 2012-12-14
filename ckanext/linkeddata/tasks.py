from ckan.lib.celery_app import celery
from logging import getLogger

from pmanager import updateExtraProperty

import time
import json
import urlparse
import requests

from datetime import datetime

log = getLogger(__name__)

def update_task_status(context, data):
    api_url = urlparse.urljoin(context['site_url'], 'api/action')
    res = requests.post(
        api_url + '/task_status_update', json.dumps(data),
        headers = {'Authorization': context['apikey'],
                   'Content-Type': 'application/json'}
    )

    if res.status_code == 200:
        return res.content
    else:
        print 'ckan failed to update task_status, status_code (%s), error %s' % (res.status_code, res.content)

@celery.task(name = "linkeddata.update_metadata")
def update_metadata(context, id):
    print 'Updating metadata for package %s' % id

    #package_info = get_action('package_show')(context, {'id': id})

    time.sleep(5)

    log.info('Metadata task finished for package %s' % id)
    #update package status
    #updateExtraProperty(package_info, 'metadata_task_status', 'updated')

    task_status = {
        'id': context['task_id'],
        'entity_id': id,
        'entity_type': u'package',
        'task_type': u'metadata',
        'key': u'celery_task_status',
        'value': str((None, 'updated', "Hello world")),
        'error': u'',
        'last_updated': datetime.now().isoformat()       
    }

    update_task_status(context, task_status)