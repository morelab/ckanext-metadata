from ckan.lib.celery_app import celery

@celery.task(name = "linkeddata.echofunction")
def echo(message):
	print message
