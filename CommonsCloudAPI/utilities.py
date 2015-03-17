"""
For CommonsCloud copyright information please see the LICENSE document
(the "License") included with this software package. This file may not
be used in any manner except in compliance with the License

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


"""
Import System Dependencies
"""
import uuid

from datetime import datetime


"""
Import Flask Dependencies
"""
from geoalchemy2.types import Geometry

from migrate.changeset import *


"""
Import CommonsCloud Dependencies
"""
from CommonsCloudAPI.extensions import db
from CommonsCloudAPI.extensions import logger


"""
Process a nested object
"""
def process_nested_object(nested_object):

  processed_objects = []

  if not nested_object:
    return processed_objects

  if len(nested_object):
    
    for index, object_ in enumerate(nested_object):
      new_object = {}
      
      for key, value in object_.__dict__.iteritems():
        if key != "_sa_instance_state":
          new_object[key] = value

      processed_objects.append(new_object)

  return processed_objects


"""
This function simply creates a machine readable name with an optional
prefix and/or suffix
"""
def generate_template_hash(_prefix='type_', _suffix=''):

  unique_collection = str(uuid.uuid4()).replace('-', '')
  collection_string = _prefix + unique_collection + _suffix

  return collection_string


"""
Create a table in the database that contains a base line of defaults
"""
def create_storage():

  table_name = generate_template_hash()

  """
  Create a new custom table for a Feature Type
  """
  new_table = db.Table(table_name, db.metadata,
    db.Column('id', db.Integer(), primary_key=True),
    db.Column('name', db.String(255)),
    db.Column('created', db.DateTime(), default=datetime.now()),
    db.Column('updated', db.DateTime(), default=datetime.now()),
    db.Column('geometry', Geometry('GEOMETRY'), nullable=True),
    db.Column('status', db.String(24), nullable=False)
  )

  """
  Make sure everything commits to the database
  """
  db.create_all()

  return table_name


"""
Create a table in the database that contains a base line of defaults

@param (object) template
    A fully qualified Template object

@param (object) field
    A fully qualfied Field object

@see Documentation on the db.Column.create() functionality
    https://sqlalchemy-migrate.readthedocs.org/en/latest/changeset.html\
        #column-create
"""
def create_storage_field(field):

  templates = field.get('template')
  storage = templates[0].get('storage')

  """
  Create a new custom table for a Feature Type
  """
  existing_table = db.Table(storage, db.metadata, **{
    'autoload': True,
    'autoload_with': db.engine
  })

  """
  We must bind the engine to the metadata here in order for our fields to
  recognize the existing Table we have loaded in the following steps
  """
  db.metadata.bind = db.engine

  """
  Retrieve the appropriate field data type that we'll be using to create the
  field in our database table
  """
  field_type = generate_field_type(field)

  if field.get('data_type') == 'relationship':
    return field_type

  if field.get('data_type') == 'file':
    return field_type

  """
  Create the new column just like we would if we were hard coding the model
  """
  new_column = db.Column(field.get('name'), field_type)
  new_column.create(existing_table)

  """
  Finally we need to make sure that the existing table knows that we've have
  just added a new column, otherwise we won't be able to use it until we
  restart the application, which would be very bad
  """
  assert new_column is existing_table.c[field.get('name')]

  return new_column


"""
Generate a PostgreSQL data type based off of a list of known strings. The
reason we do this is to abstract away some details from the user making it
easier for them to create new fields

@param (object) field
    A fully qualified Field object
"""
def generate_field_type(field):

  """
  If we are creating a `relationship` or an `attachment`/`file` field we can
  simply generate those right away and skip the rest of the field building
  behaviour for now.
  """
  if field.get('data_type') == 'relationship':
    return generate_relationship_field(field)
  elif field.get('data_type') == 'file':
    return generate_attachment_field(field)

  """
  Define all of teh column types that our system currently allows the user to
  create with the API
  """
  fields = {
    "float": db.Float(),
    "whole_number": db.Integer(),
    "text": db.String(255),
    "email": db.String(255),
    "phone": db.String(255),
    "url": db.String(255),
    "textarea": db.Text(),
    "boolean": db.Boolean(),
    "date": db.Date(),
    "time": db.Time(),
    "list": db.String(255)
  }

  return fields[field.get('data_type')]


"""
Create a new many-to-many relationship table using the information provided
in the API Request

  @return (object)
    @key (string) type
    @key (string) association
    @key (string) relationship

"""
def generate_relationship_field(field):

  templates = field.get('template')
  storage = templates[0].get('storage')

  """
  Make sure that the table we need to use for creating the relationship is loaded
  into our db.metadata, otherwise the whole process will fail
  """
  existing_table = db.Table(field.get('relationship'), db.metadata, **{
    'autoload': True,
    'autoload_with': db.engine
  })

  """
  Create a name for our new field relationship table
  """
  table_name = generate_template_hash(_prefix='ref_')

  """
  Create a new Association Table in our database, based up the two existing Tables
  we've previously created
  """
  parent_foreign_key_id = ('%s.%s') % (storage,'id')
  child_foreign_key_id = ('%s.%s') % (field.get('relationship'),'id')

  new_table = db.Table(table_name, db.metadata,
    db.Column('parent_id', db.Integer, db.ForeignKey(parent_foreign_key_id), **{
      'primary_key': True
    }),
    db.Column('child_id', db.Integer, db.ForeignKey(child_foreign_key_id), **{
      'primary_key': True
    })
  )

  db.metadata.bind = db.engine

  """
  Make sure everything commits to the database
  """
  db.create_all()

  return {
    'type': 'relationship',
    'association': table_name,
    'relationship': field.get('relationship')
  }


"""
Create a new many-to-many relationship table using the information provided
in the API Request

  @return (object)
    @key (string) type
    @key (string) association
    @key (string) relationship

"""
def generate_attachment_field(field):

  """
  Before we can create a relationship between Attachments and a Template
  we need to create a Table in the database to retain our attachments
  """
  attachment_table_name = generate_template_hash(_prefix='attachment_')

  new_table = db.Table(attachment_table_name, db.metadata,
    db.Column('id', db.Integer, primary_key=True),
    db.Column('caption', db.String(255)),
    db.Column('credit', db.String(255)),
    db.Column('credit_link', db.String(255)),
    db.Column('filename', db.String(255)),
    db.Column('filepath', db.String(255)),
    db.Column('filetype', db.String(255)),
    db.Column('filesize', db.Integer()),
    db.Column('created', db.DateTime()),
    db.Column('status', db.String(24), nullable=False)
  )

  db.metadata.bind = db.engine

  db.create_all()

  """
  Next we update the relationship field
  """
  field.relationship = attachment_table_name

  """
  Finally we can create the actual relationship
  """
  relationship_ = generate_relationship_field(field)

  return {
    'type': 'file',
    'association': relationship_['association'],
    'relationship': attachment_table_name
  }