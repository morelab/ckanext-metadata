from sqlalchemy import types, Column, Table, MetaData, UnicodeText, create_engine, Integer, ForeignKey
import vdm.sqlalchemy
from sqlalchemy.orm import mapper, relationship
import sqlalchemy

metadata = MetaData()
property_table = Table('property_table', metadata,
		Column('package_id', UnicodeText, primary_key=True),
        Column('key', UnicodeText, nullable=False),
        Column('value', UnicodeText, nullable=False),
)

class Property(object):

    def __init__(self, package_id, key, value):
    	self.package_id = package_id
        self.key = key
        self.value = value

mapper(Property, property_table)
