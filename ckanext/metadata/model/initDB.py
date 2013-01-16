import property_model
from sqlalchemy import create_engine

print 'Creating table for metadata property storage'
engine = create_engine('postgresql://ckanuser:pass@localhost/ckantest', echo=True)
property_model.metadata.drop_all(engine)
property_model.metadata.create_all(engine)
