from sqlalchemy import types, Column, Table, MetaData, UnicodeText
from sqlalchemy import create_engine, Integer, ForeignKey, DateTime
import vdm.sqlalchemy
from sqlalchemy.orm import mapper, relationship
import sqlalchemy
from datetime import datetime

metadata = MetaData()
property_table = Table('property_table', metadata,
		Column('package_id', UnicodeText, primary_key=True),
        Column('key', UnicodeText, primary_key=True),
        Column('value', UnicodeText, nullable=False),
)

class Property(object):

    def __init__(self, package_id, key, value):
    	self.package_id = package_id
        self.key = key
        self.value = value

    def __repr__(self):
    	return '<Property package_id: %s key: %s value: %s>' % (self.package_id, self.key, self.value)
      
timestamp_table = Table('timestamp_table', metadata,
        Column('package_id', UnicodeText, primary_key=True),
        Column('updated', DateTime, nullable=False),
)
        
class Timestamp(object):
    
    def __init__(self, package_id):
        self.package_id = package_id
        self.updated = datetime.now()
        
    def __repr__(self):
        return '<Timestamp package_id: %s updated on: %s >' % (self.package_id, self.updated)

mapper(Property, property_table)
mapper(Timestamp, timestamp_table)
