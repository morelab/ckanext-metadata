from ckan.lib.base import render
from logging import getLogger
from ckan.controllers.package import PackageController

log = getLogger(__name__)

class MetadataController(PackageController):
        
    def show_metadata(self, id):
		log.info('Showing metadata for id: %s' % id)         
		
		# using default functionality
		template = self.read(id)
		
		#rendering using default template
		return render('metadata/read.html')		
