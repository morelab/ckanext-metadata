from ckan.lib.base import render, c
from logging import getLogger
from ckan.controllers.package import PackageController
from ckan.lib.base import BaseController

import uuid
from ckan.lib.celery_app import celery

log = getLogger(__name__)

class MetadataController(PackageController):
        
    def show_metadata(self, id):
        log.info('Showing metadata for id: %s' % id)         

        # using default functionality
        template = self.read(id)

        c.extra_metadata = {'keyA': 'valueA', 'keyB': 'valueB'}

        log.info('Executing task using celery')
        celery.send_task("linkeddata.echofunction", args=["Hello World"], task_id=str(uuid.uuid4()))

        #rendering using default template
        return render('metadata/read.html')

class AdminController(BaseController):

    def metadata_tasks(self):
        log.info('Showing metadata tasks')          
        
        return render('tasks/index.html')
        
