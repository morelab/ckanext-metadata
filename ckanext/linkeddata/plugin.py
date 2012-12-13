from ckan.plugins import SingletonPlugin, IGenshiStreamFilter, implements, IConfigurer, IRoutes
from logging import getLogger
from pylons import request
from genshi.input import HTML
from genshi.filters.transform import Transformer
import os

log = getLogger(__name__)

class MetadataExtension(SingletonPlugin):
    
    implements(IConfigurer, inherit=True)
    implements(IGenshiStreamFilter, inherit=True)
    implements(IRoutes, inherit=True)
    
    def update_config(self, config):
        here = os.path.dirname(__file__)
        rootdir = os.path.dirname(os.path.dirname(here))
        our_public_dir = os.path.join(rootdir, 'ckanext', 
				'linkeddata', 'theme', 'public')
                                      
        template_dir = os.path.join(rootdir, 'ckanext',
				'linkeddata', 'theme', 'templates')
				
        # set resource and template overrides
        config['extra_public_paths'] = ','.join([our_public_dir,
                config.get('extra_public_paths', '')])
                
        config['extra_template_paths'] = ','.join([template_dir,
				config.get('extra_template_paths', '')])
    
    def filter(self, stream):
        routes = request.environ.get('pylons.routes_dict')
        log.info(routes)
        if routes.get('controller') in ('package', 'related',
			'ckanext.linkeddata.controller:MetadataController') :
               stream = stream | Transformer('//ul[@class="nav nav-pills"]').append(HTML(
                    
                    '''<li class>
                        <a class href="/dataset/metadata/%s">
                            <img src="/icons/rdf_flyer.24" height="16px" width="16px" alt="None" class="inline-icon ">
                            Extra
                        </a>
                    </li>''' % routes.get('id')
                    
                ))
                
        if routes.get('controller') in ('admin', 'ckanext.linkeddata.controller:AdminController'):
			 stream = stream | Transformer('//ul[@class="nav nav-pills"]').append(HTML(
                    
                    '''<li class>
                        <a class href="/ckan-admin/metadata-tasks">
                            <img src="/icons/rdf_flyer.24" height="16px" width="16px" alt="None" class="inline-icon ">
                            Metadata Tasks Status
                        </a>
                    </li>'''
                    
                ))

        return stream
       
    def before_map(self, map):
        map.connect('/dataset/metadata/{id}', controller='ckanext.linkeddata.controller:MetadataController', action='show_metadata')
        map.connect('/ckan-admin/metadata-tasks', controller='ckanext.linkeddata.controller:AdminController', action='metadata_tasks')

        return map
    
