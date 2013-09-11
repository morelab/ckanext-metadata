# -*- coding: utf8 -*- 

from ckan.lib.base import render, c, model, config, request, response
from logging import getLogger
from ckan.controllers.package import PackageController
from ckan.controllers.api import ApiController as BaseApiController 
from ckan.lib.base import BaseController, abort
from ckan.logic import get_action, NotFound
from tasks import get_task_status_value
from genshi.template import MarkupTemplate

from ckan.model.types import make_uuid

from datetime import datetime

from model.property_model import Property

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

        c.metadata_task_status = get_task_status_value(package_info['id'])

        c.extra_metadata = {}
        
        if 'clear' in request.params:
            print 'Clearing metadata for package %s' % c.pkg.id
            properties = model.Session.query(Property).filter_by(package_id=c.pkg.id).delete()
            model.Session.commit()

        properties = model.Session.query(Property).filter_by(package_id=c.pkg.id)

        for property in properties:
            c.extra_metadata[property.key] = property.value

        #rendering using default template
        return render('metadata/read.html')
        
    def get_void_desc(self, id):
        log.info('Generating VOID description for package: %s' % id)

        # using default functionality
        self.read(id, 'rdf')

        #check if metadada info exists and add it otherwise
        context = {'model': model, 'session': model.Session, 'user': c.user or c.author}
        package_info = get_action('package_show')(context, {'id': c.pkg.id})

        c.metadata_task_status = get_task_status_value(package_info['id'])

        c.extra_metadata = {}
        
        if 'clear' in request.params:
            properties = model.Session.query(Property).filter_by(package_id=c.pkg.id).delete()

        properties = model.Session.query(Property).filter_by(package_id=c.pkg.id)

        for property in properties:
            c.extra_metadata[property.key] = property.value

        #rendering using void template
        return render('package/void.rdf', loader_class=MarkupTemplate)

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

    def clear_finished_tasks(self, context, all_tasks=False):
        log.info('Clearing finished tasks')

        task_status = self.get_tasks_status(context)

        for _, (task_id, status) in task_status.items():
            if all_tasks or status in ('error', 'finished'):
                log.info('Deleting task %s with status %s' % (task_id, status))
                get_action('task_status_delete')(context, {'id': task_id})

    def metadata_tasks(self):
        log.info('Showing metadata tasks')

        context = {'model': model, 'session': model.Session,'user': c.user}

        if 'clear' in request.params:
            self.clear_finished_tasks(context)
        if 'clear_all' in request.params:
            self.clear_finished_tasks(context, all_tasks=True)

        c.task_status = self.get_tasks_status(context)        

        return render('tasks/index.html')

class ApiController(BaseApiController):

    def update_properties(self):
        error_400_msg = 'Please provide a suitable package_id parameter'

        request = self._get_request_data()

        if not 'package_id' in request:
            abort(400,error_400_msg)

        log.info("Updating properties for package %s" % request['package_id'])
        for key, value in request.items():
            if not key == 'package_id':
                property = Property(request['package_id'], key, value)
                model.Session.merge(property)

        model.Session.commit()

        return self._finish_ok({})

    def update_vocabulary_count(self):
        log.info('Updating vocabulary count')

        vocab_count = {}

        vocab_properties = model.Session.query(Property).filter_by(key='vocabularies').all()
        for property in vocab_properties:
            vocabularies = eval(property.value)
            for vocabulary in vocabularies:
                if vocabulary not in vocab_count:
                    vocab_count[vocabulary] = 0
                else:
                    vocab_count[vocabulary] += 1

        for property in vocab_properties:
            package_vocabularies = eval(property.value)
            for vocabulary in package_vocabularies:
                if vocabulary in vocab_count:
                    package_vocabularies[vocabulary] = vocab_count[vocabulary]

            property.value = str(package_vocabularies)

        model.Session.commit()

        return self._finish_ok({})
