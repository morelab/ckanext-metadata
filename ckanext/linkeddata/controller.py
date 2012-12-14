# -*- coding: utf8 -*- 

from ckan.lib.base import render, c, model, config
from logging import getLogger
from ckan.controllers.package import PackageController
from ckan.lib.base import BaseController
from ckan.logic import get_action, NotFound
from pmanager import getExtraProperty, updateExtraProperty, createExtraProperty, updatePackage, getTaskStatusValue

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

        c.metadata_task_status = getTaskStatusValue(context, package_info['id'])

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

            task_status = getTaskStatusValue(context, package_info['id'])
            if task_status == 'disabled':
                #launch task and change status to waiting

                task_status = {
                    'entity_id': package_info['id'],
                    'entity_type': u'package',
                    'task_type': u'metadata',
                    'key': u'celery_task_status',
                    'value': str((package_info['id'], 'waiting', None)),
                    'error': u'',
                    'last_updated': datetime.now().isoformat()
                }

                #TODO: remove fixed user key
                task_status = get_action('task_status_update')(context, task_status)

                task_context = {'task_id': task_status['id'], 'site_url': config.get('ckan.site_url'), 'apikey': 'b1d895d3-5187-491c-8826-4c7f63fe84ab'}
                celery.send_task("linkeddata.update_metadata", args=[task_context, package_info['id']], task_id=task_status['id'])
                log.info('Task sent to celery for package %s' % package_info['id'])

        return render('tasks/index.html')

