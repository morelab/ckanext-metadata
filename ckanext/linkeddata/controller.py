# -*- coding: utf8 -*- 

from ckan.lib.base import render, c, model, config, request
from logging import getLogger
from ckan.controllers.package import PackageController
from ckan.lib.base import BaseController
from ckan.logic import get_action, NotFound
from pmanager import getExtraProperty, updateExtraProperty, createExtraProperty, updatePackage, get_task_status_value

from ckan.model.types import make_uuid
from ckan.lib.celery_app import celery

from datetime import datetime

log = getLogger(__name__)

def get_task_status(context, id):
    try:
        task_status = get_action('task_status_show')(context, {'entity_id': id, 'task_type': 'metadata', 'key': 'celery_task_status'})
        print 'Task status', task_status
        return task_status
    except NotFound:
        return None

class MetadataController(PackageController):
        
    def show_metadata(self, id):
        log.info('Showing metadata for id: %s' % id)         

        # using default functionality
        template = self.read(id)

        #check if metadada info exists and add it otherwise
        context = {'model': model, 'session': model.Session, 'user': c.user or c.author}
        package_info = get_action('package_show')(context, {'id': c.pkg.id})

        c.metadata_task_status = get_task_status_value(context, package_info['id'])

        c.extra_metadata = {}

        #rendering using default template
        return render('metadata/read.html')

class AdminController(BaseController):

    def get_tasks_status(self, context):
        tasks_status = {}

        packages = get_action('package_list')(context, ())

        for package in packages:
            package_info = get_action('package_show')(context, {'id': package})

            try:
                task_status = get_action('task_status_show')(context, {'entity_id': package_info['id'], 'task_type': 'metadata', 'key': 'celery_task_status'})
                task_status_value = get_task_status_value(eval(task_status['value']))
                tasks_status[package_info['name']] = (task_status['id'], task_status_value)
            except NotFound:
                pass

        return tasks_status

    def clear_pending_tasks(self, context):
        log.info('Clearing pending tasks')

        task_status = self.get_tasks_status(context)

        for _, (task_id, status) in task_status.items():
            if status in ('launched', 'finished'):
                log.info('Deleting task %s with status %s' % (task_id, status))
                get_action('task_status_delete')(context, {'id': task_id})

    def metadata_tasks(self):
        log.info('Showing metadata tasks')

        context = {'model': model, 'session': model.Session,'user': c.user}

        if 'clear' in request.params:
            self.clear_pending_tasks(context)

        c.task_status = self.get_tasks_status(context)        

        return render('tasks/index.html')

