# -*- coding: utf8 -*- 

from ckan.lib.base import render, c, model
from logging import getLogger
from ckan.controllers.package import PackageController
from ckan.lib.base import BaseController
from ckan.logic import get_action
from pmanager import getExtraProperty, updateExtraProperty, createExtraProperty

import uuid
from ckan.lib.celery_app import celery

log = getLogger(__name__)

class MetadataController(PackageController):
        
    def show_metadata(self, id):
        log.info('Showing metadata for id: %s' % id)         

        # using default functionality
        template = self.read(id)

        #check if metadada info exists and add it otherwise
        context = {'model': model, 'session': model.Session, 'user': c.user or c.author}
        package_info = get_action('package_show')(context, {'id': c.pkg.id})
        metadata_task_status = getExtraProperty(package_info, 'metadata_task_status')
        if metadata_task_status is None:
            adapta_property = createExtraProperty(c.pkg.id, 'metadata_task_status', 'changed')
            updateExtraProperty(package_info, adapta_property)
            metadata_task_status = getExtraProperty(package_info, 'metadata_task_status')
            updatePackage(context, package_info)

        c.metadata_task_status = metadata_task_status
        c.extra_metadata = {}

        #rendering using default template
        return render('metadata/read.html')

class AdminController(BaseController):

    def metadata_tasks(self):
        log.info('Showing metadata tasks')

        context = {'model': model, 'session': model.Session,'user': c.user}
        packages = get_action('package_list')(context, ())

        log.info('Executing task using celery')
        celery.send_task("linkeddata.echofunction", args=["Hello World"], task_id=str(uuid.uuid4()))

        return render('tasks/index.html')

