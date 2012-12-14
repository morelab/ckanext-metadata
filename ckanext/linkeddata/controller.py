# -*- coding: utf8 -*- 

from ckan.lib.base import render, c, model
from logging import getLogger
from ckan.controllers.package import PackageController
from ckan.lib.base import BaseController
from ckan.logic import get_action

import uuid
from ckan.lib.celery_app import celery

log = getLogger(__name__)

class MetadataController(PackageController):
        
    def show_metadata(self, id):
        log.info('Showing metadata for id: %s' % id)         

        # using default functionality
        template = self.read(id)

        #log.info('Executing task using celery')
        #celery.send_task("linkeddata.echofunction", args=["Hello World"], task_id=str(uuid.uuid4()))

        #check if metadada info exists and add it otherwise
        context = {'model': model, 'session': model.Session, 'user': c.user or c.author}
        package_info = get_action('package_show')(context, {'id': c.pkg.id})
        metadata_task_status = self.getExtraProperty(package_info, 'metadata_task_status')
        if metadata_task_status is None:
            adapta_property = self.createExtraProperty(c.pkg.id, 'metadata_task_status', 'disabled')
            self.updateExtraProperty(package_info, adapta_property)
            metadata_task_status = self.getExtraProperty(package_info, 'metadata_task_status')
            self.updatePackage(context, package_info)

        c.metadata_task_status = metadata_task_status
        c.extra_metadata = {}

        #rendering using default template
        return render('metadata/read.html')

    def getExtraProperty(self, package_info, key):
        for extra_entry in package_info['extras']:
            if extra_entry['key'] == key:
                return extra_entry['value']
        return None

    def createExtraProperty(self, package_id, key, value):
        adapta_metadata = {}
        adapta_metadata['state'] = 'deleted'
        adapta_metadata['value'] = '"' + str(value) + '"'
        adapta_metadata['revision_timestamp'] = '2012-12-13T14:27:35.654886'
        adapta_metadata['package_id'] = package_id
        adapta_metadata['key'] = key
        adapta_metadata['revision_id'] = str(uuid.uuid4())
        adapta_metadata['id'] = str(uuid.uuid4())
        return adapta_metadata

    def checkExtraProperty(self, package_info, key):
        for extra_data in package_info['extras']:
            if extra_data['key'] == key:
                return True

        return False

    def updateExtraProperty(self, package_info, extra_property):
        for extra_data in package_info['extras']:
            if extra_data['key'] == extra_property['key']:
                extra_data['value'] = extra_property['value']
                extra_data['revision_id'] = str(uuid.uuid4())
                extra_data['revision_timestamp'] = '2012-12-13T14:27:35.654886'
                return 

        package_info['extras'].append(extra_property)
        print package_info['extras']

    def deleteExtraProperty(self, package_info, key):
        for extra_data in package_info['extras']:
            if extra_data['key'] == key:
                package_info['extras'].remove(extra_data)

    def updatePackage(self, context, package_info):
        updated_info = {}

        #set log message 
        updated_info['log_message'] = 'Updating ADAPTA extra information'

        #copy other required fields
        updated_info['id'] = package_info['id']
        updated_info['extras'] = []
        updated_info['extras'] = updated_info['extras'] + package_info['extras']
        updated_info['maintainer'] = package_info['maintainer']
        updated_info['name'] = package_info['name']
        updated_info['author'] = package_info['author']
        updated_info['author_email'] = package_info['author_email']
        updated_info['tag_string'] = ''
        updated_info['title'] = package_info['title']
        updated_info['maintainer_email'] = package_info['maintainer_email']
        updated_info['url'] = package_info['url']
        updated_info['version'] = package_info['version']
        updated_info['license_id'] = package_info['license_id']
        updated_info['notes'] = package_info['notes']

        updated_package = get_action('package_update')(context, updated_info)
        print 'Updated package %s' % updated_package

class AdminController(BaseController):

    def metadata_tasks(self):
        log.info('Showing metadata tasks')

        context = {'model': model, 'session': model.Session,'user': c.user}
        packages = get_action('package_list')(context, ())

        for package in packages:
            data_dict = {'id': package}
            package_info = get_action('package_show')(context, data_dict)        

        return render('tasks/index.html')

