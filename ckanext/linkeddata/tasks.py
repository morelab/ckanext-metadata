from ckan.lib.celery_app import celery
from logging import getLogger

from pmanager import updateExtraProperty

import time

log = getLogger(__name__)

@celery.task(name = "linkeddata.update_metadata")
def update_metadata(id):
	print 'Updating metadata for package %s' % id

	#package_info = get_action('package_show')(context, {'id': id})

	time.sleep(5)

	log.info('Metadata task finished for package %s' % id)
	#update package status
	#updateExtraProperty(package_info, 'metadata_task_status', 'updated')

	return "Task finished in 5 seconds"
