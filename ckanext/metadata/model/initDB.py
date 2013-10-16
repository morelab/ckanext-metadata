import property_model
from sqlalchemy import create_engine

USER = 'ckanuser'
PASS = '4d4pt4'

print 'Creating table for metadata property storage'
engine = create_engine('postgresql://%s:%s@localhost/ckantest' % (USER, PASS), echo=True)
property_model.metadata.drop_all(engine)
property_model.metadata.create_all(engine)
