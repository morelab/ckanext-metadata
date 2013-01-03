import property_model
from sqlalchemy import create_engine

engine = create_engine('postgresql://ckanuser:pass@localhost/ckantest')
property_model.metadata.drop_all(engine)
property_model.metadata.create_all(engine)
