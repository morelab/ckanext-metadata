from ckan.plugins import SingletonPlugin, IGenshiStreamFilter, implements, IConfigurer
from logging import getLogger
from pylons import request
from genshi.input import HTML
from genshi.filters.transform import Transformer
import os

log = getLogger(__name__)

class MetadataExtension(SingletonPlugin):
    
    implements(IConfigurer, inherit=True)
    implements(IGenshiStreamFilter, inherit=True)
    
    def update_config(self, config):
        here = os.path.dirname(__file__)
        rootdir = os.path.dirname(os.path.dirname(here))
        our_public_dir = os.path.join(rootdir, 'ckanext', 
				'linkeddata', 'theme', 'public')
                                      
        # set resource overrides
        config['extra_public_paths'] = ','.join([our_public_dir,
                config.get('extra_public_paths', '')])
    
    def filter(self, stream):
        routes = request.environ.get('pylons.routes_dict')
        log.info(routes)
        if routes.get('controller') in ('package', 'related') :
               stream = stream | Transformer('//ul[@class="nav nav-pills"]').append(HTML(
                    
                    '''<li class>
                        <a class href="/prueba/test">
                            <img src="/icons/rdf_flyer.24" height="16px" width="16px" alt="None" class="inline-icon ">
                            Extra
                        </a>
                    </li>'''
                    
                ))

        return stream
    
