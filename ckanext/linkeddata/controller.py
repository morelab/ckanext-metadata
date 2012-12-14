# -*- coding: utf8 -*- 

from ckan.lib.base import render, c, model
from logging import getLogger
from ckan.controllers.package import PackageController
from ckan.lib.base import BaseController
from ckan.logic import get_action, NotFound
from pmanager import getExtraProperty, updateExtraProperty, createExtraProperty, updatePackage, getTaskStatus

from ckan.model.types import make_uuid
from ckan.lib.celery_app import celery

from datetime import datetime

log = getLogger(__name__)

class MetadataController(PackageController):
        
    def show_metadata(self, id):
        log.info('Showing metadata for id: %s' % id)         

        # using default functionality
        template = self.read(id)

        #check if metadada info exists and add it otherwise
        context = {'model': model, 'session': model.Session, 'user': c.user or c.author}
        package_info = get_action('package_show')(context, {'id': c.pkg.id})

        task_status = getTaskStatus(context, package_info['id'])

        c.metadata_task_status = task_status[0]

        c.extra_metadata = {}

        #rendering using default template
        return render('metadata/read.html')

class AdminController(BaseController):

    def metadata_tasks(self):
        log.info('Showing metadata tasks')

        context = {'model': model, 'session': model.Session,'user': c.user}
        packages = get_action('package_list')(context, ())

        for package in packages:
            print 'Checking package %s status' % package
            package_info = get_action('package_show')(context, {'id': package})

            task_status = getTaskStatus(context, package_info['id'])
            if task_status[0] == 'disabled':
                #launch task and change status to waiting

                task_id = make_uuid()
                task_status = {
                    'entity_id': package_info['id'],
                    'entity_type': u'package',
                    'task_type': u'metadata',
                    'key': u'celery_task_id',
                    'value': task_id,
                    'error': u'',
                    'last_updated': datetime.now().isoformat()
                }

                get_action('task_status_update')(context, task_status)
                celery.send_task("linkeddata.update_metadata", args=[package_info['id']], task_id=task_id)
                log.info('Task sent to celery for package %s' % package_info['id'])

        return render('tasks/index.html')

