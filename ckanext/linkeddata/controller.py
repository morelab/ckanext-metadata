# -*- coding: utf8 -*- 

from ckan.lib.base import render, c, model, config
from logging import getLogger
from ckan.controllers.package import PackageController
from ckan.lib.base import BaseController
from ckan.logic import get_action, NotFound
from pmanager import getExtraProperty, updateExtraProperty, createExtraProperty, updatePackage, getTaskStatusValue, getTaskStatus

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

        #create table showing metadata tasks
        c.task_status = {}
        for package in packages:
            package_info = get_action('package_show')(context, {'id': package})
            task_status = getTaskStatus(context, package_info['id'])
            task_status_value = getTaskStatusValue(task_status)
            if not task_status_value == 'disabled':
                c.task_status[package_info['name']] = task_status_value

        return render('tasks/index.html')

