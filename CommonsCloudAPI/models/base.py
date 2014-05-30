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
Import Python Dependencies
"""
import re
import uuid
from datetime import datetime

from collections import OrderedDict

from migrate.changeset import *


"""
Import Flask Dependencies
"""
from flask import abort
from flask import request

import json

from geoalchemy2.types import Geometry

from sqlalchemy.orm import ColumnProperty

from flask.ext.restless.helpers import to_dict

"""
Import Commons Cloud Dependencies
"""
from CommonsCloudAPI.extensions import db
from CommonsCloudAPI.extensions import logger
from CommonsCloudAPI.extensions import status as status_

from CommonsCloudAPI.format.format_csv import CSV
from CommonsCloudAPI.format.format_geojson import GeoJSON
from CommonsCloudAPI.format.format_json import JSON

from geoalchemy2.elements import WKBElement
import geoalchemy2.functions as func


class CommonsModel(object):

  __public__ = ['id', 'name', 'created', 'status']
  __public_relationships__ = None

  def __init__(self):
    pass

  """
  In order to be able to work with an object it needs to be serialized,
  otherwise we can turn it into any type of file

  @requires
      from collections import OrderedDict

  @param (object) self
      The object we are acting on behalf of

  @return (dict) result
      A dictionary of the contents of our objects

  """
  def serialize_object(self, _content):

      result = OrderedDict()

      to_geojson = func.ST_AsGeoJSON
      to_json = json.loads
      use_scalar = db.session.scalar

      for key in _content.__mapper__.c.keys():
        value = getattr(_content, key)
        if key in self.__public__ and value is not None:
          if isinstance(value, WKBElement):
            if db.session is not None:
              geojson = str(use_scalar(to_geojson(value, 4)))
              result[key] = to_json(geojson)
            else:
              result[key] = str(value)
          else:
            result[key] = str(getattr(_content, key))

      return result



  """
  In order to be able to work with an object it needs to be serialized,
  otherwise we can turn it into any type of file

  @requires
      from collections import OrderedDict

  @param (object) self
      The object we are acting on behalf of

  @return (dict) result
      A dictionary of the contents of our objects

  """
  def serialize_list(self, _content):

      list_ = []

      for object_ in _content:

        result = OrderedDict()

        if hasattr(object_, '__mapper__'):
          for key in object_.__mapper__.c.keys():
            if key in self.__public__:
              result[key] = getattr(object_, key)
        else:
          logger.warning('object_.keys() %s', object_.keys())
          logger.warning('object_ %s', object_)
          logger.warning('public keys %s', self.__public__)
          for key in object_.keys():
            value = object_.get(key, None)
            logger.warning('value %s', value)
            if key in self.__public__:
              logger.warning('value type %s for key %s', type(value), key)
              if key == 'geometry':
                logger.warning('process that geometry')
                if isinstance(value, WKBElement) and db.session is not None:
                  geojson = str(db.session.scalar(func.ST_AsGeoJSON(value, 4)))
                else:
                  geojson = value

                result[key] = json.loads(geojson)
              elif isinstance(value, (int, long, float, complex)):
                result[key] = value
              else:
                result[key] = str(value)

        list_.append(result)

      return list_


  """
  Remove all characters except for spaces and alpha-numeric characters,
  replace all spaces in a string with underscores, change all uppercase
  letters to lowercase letters, and return the updated string.
  """
  def generate_machine_name(self, human_name):
    return re.sub('[^0-9a-zA-Z ] +', '', human_name).replace(' ','_').lower()


  """
  This function simply creates a machine readable name with an optional
  prefix and/or suffix
  """
  def generate_template_hash(self, _prefix='type_', _suffix=''):

    unique_collection = str(uuid.uuid4()).replace('-', '')
    collection_string = _prefix + unique_collection + _suffix

    return collection_string


  """
  Generate a PostgreSQL data type based off of a list of known strings. The
  reason we do this is to abstract away some details from the user making it
  easier for them to create new fields

  @param (object) field
      A fully qualified Field object
  """
  def generate_field_type(self, field, template):

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
      "time": db.Time()
    }

    if field.data_type == 'relationship':
      return self.generate_relationship_field(field, template)
    elif field.data_type == 'file':
      return self.generate_attachment_field(field, template)

    return fields[field.data_type]

  def generate_relationship_field(self, field, template):

    """
    Make sure that the table we need to use for creating the relationship is loaded
    into our db.metadata, otherwise the whole process will fail
    """
    exisitng_table = db.Table(field.relationship, db.metadata, autoload=True, autoload_with=db.engine)

    """
    Create a name for our new field relationship table
    """
    table_name = self.generate_template_hash(_prefix='ref_')

    """
    Create a new Association Table in our database, based up the two existing Tables
    we've previously created
    """
    parent_foreign_key_id = ('%s.%s') % (template.storage,'id')
    child_foreign_key_id = ('%s.%s') % (field.relationship,'id')

    new_table = db.Table(table_name, db.metadata,
      db.Column('parent_id', db.Integer, db.ForeignKey(parent_foreign_key_id), primary_key=True),
      db.Column('child_id', db.Integer, db.ForeignKey(child_foreign_key_id), primary_key=True)
    )

    db.metadata.bind = db.engine

    """
    Make sure everything commits to the database
    """
    db.create_all()

    return {
      'type': 'relationship',
      'association': table_name,
      'relationship': field.relationship
    }

  def generate_attachment_field(self, field, template):

    """
    Before we can create a relationship between Attachments and a Template
    we need to create a Table in the database to retain our attachments
    """
    attachment_table_name = self.generate_template_hash(_prefix='attachment_')

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
    relationship_ = self.generate_relationship_field(field, template)

    return {
      'type': 'file',
      'association': relationship_['association'],
      'relationship': attachment_table_name
    }

  """
  Storage name
  """
  def validate_storage(self, storage_name):

    if not storage_name.startswith('type_'):
      storage_name = str('type_' + storage_name)

    return storage_name


  """
  Create a table in the database that contains a base line of defaults
  """
  def create_storage(self, table_name=""):

    if not table_name:
      table_name = self.generate_template_hash()


    """
    Why are we closing the session, what gives?

    http://docs.sqlalchemy.org/en/rel_0_9/faq.html#my-program-is-hanging-when-i-say-table-drop-metadata-drop-all

    """
    # db.session.close()


    """
    Create a new custom table for a Feature Type
    """
    new_table = db.Table(table_name, db.metadata,
      db.Column('id', db.Integer(), primary_key=True),
      db.Column('created', db.DateTime(), default=datetime.now()),
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
      https://sqlalchemy-migrate.readthedocs.org/en/latest/changeset.html#column-create
  """
  def create_storage_field(self, template, field):

    if not template.storage or not hasattr(field, 'data_type'):
      return abort(404)

    """
    Create a new custom table for a Feature Type
    """
    exisitng_table = db.Table(template.storage, db.metadata, autoload=True, autoload_with=db.engine)

    """
    We must bind the engine to the metadata here in order for our fields to
    recognize the existing Table we have loaded in the following steps
    """
    db.metadata.bind = db.engine

    """
    Retrieve the appropriate field data type that we'll be using to create the
    field in our database table
    """
    field_type = self.generate_field_type(field, template)

    if field.data_type == 'relationship':
      return field_type

    if field.data_type == 'file':
      return field_type

    """
    Create the new column just like we would if we were hard coding the model
    """
    new_column = db.Column(field.name, field_type)
    new_column.create(exisitng_table)

    """
    Finally we need to make sure that the existing table knows that we've have
    just added a new column, otherwise we won't be able to use it until we
    restart the application, which would be very bad
    """
    assert new_column is exisitng_table.c[field.name]

    return new_column


  def create_owner_field(self, template):

    if not template.storage:
      return abort(404)

    """
    Create a new custom table for a Feature Type
    """
    exisitng_table = db.Table(template.storage, db.metadata, autoload=True, autoload_with=db.engine)

    """
    We must bind the engine to the metadata here in order for our fields to
    recognize the existing Table we have loaded in the following steps
    """
    db.metadata.bind = db.engine

    """
    Create the new column just like we would if we were hard coding the model
    """
    new_column = db.Column('owner', db.Integer, db.ForeignKey('user.id'))
    new_column.create(exisitng_table)

    """
    Finally we need to make sure that the existing table knows that we've have
    just added a new column, otherwise we won't be able to use it until we
    restart the application, which would be very bad
    """
    assert new_column is exisitng_table.c['owner']

    return new_column

  def get_storage(self, template, fields=[]):

    if type(template) is str:
      class_name = str(template)
      relationships = []
    else:
      class_name = str(template.storage)
      relationships = self.get_relationship_fields(template.fields)


    arguments = {
      "class_name": class_name,
      "relationships": relationships
    }

    class_arguments = self.get_class_arguments(**arguments)

    Model = type(class_name, (db.Model,), class_arguments)


    """
    For the API to return items properly, we should check to see if the fields
    we are attempting to call are marked as listed or not.
    """
    if fields or hasattr(template, 'fields'):

      public_fields = self.__public__

      for field in fields:
        if field.is_listed:
          public_fields.append(field.name)

      self.__public__ = public_fields


    return Model


  """
  Create a dictionary of Class Arguments to assist
  us in building reliable SQLAlchemy models capable
  of handling many-to-many relationships.
  """
  def get_class_arguments(self, class_name, relationships):

    """
    Start an empty object to store all of our Class Arguments
    """
    class_arguments = {}


    """
    Automatically load all of our basic table fields and other
    meta information
    """
    class_arguments['__table__'] = db.Table(class_name, db.metadata, autoload=True, autoload_with=db.engine)
    class_arguments['__tablename__'] = class_name
    class_arguments['__table_args__'] = {
      "extend_existing": True
    }


    """
    Unfortunately we have to manually load the relationships that
    our models need to work properly.

    To build relationships out properly we need a few things:

    'type_5740f6daa55f4fc790e7eeacb96d726e' : db.relationship('type_5740f6daa55f4fc790e7eeacb96d726e', secondary=our_reference_table, backref=db.backref(class_name))

    1. We need the name of the association table (e.g., ref_XXXXXXXXXXXXXXXXXXXXX)
    2. We need the name of the other table that actually contains the content to
       be referenced (e.g., type_XXXXXXXXXXXXXXXXXXX)
    3. We should have a model class for the association table
    4. We need the name of the class or 'storage' of the Class being acted on

    """
    for relationship in relationships:

      table_name = str(relationship.relationship)

      RelationshipModel = self.get_storage(table_name)


      """
      Setup our association table for each relationship that we have
      in our fields list
      """
      parent_id_key = str(class_name) + '.id'
      child_id_key = table_name + '.id'

      association_table = db.Table(str(relationship.association), db.metadata,
          db.Column('parent_id', db.Integer, db.ForeignKey(parent_id_key), primary_key=True),
          db.Column('child_id', db.Integer, db.ForeignKey(child_id_key), primary_key=True),
          extend_existing = True,
          autoload = True,
          autoload_with = db.engine
      )

      class_arguments[table_name] = db.relationship(RelationshipModel, secondary=association_table, backref=class_name)

    return class_arguments


  """
  Create a list of fields that need to have relationships loaded
  for them to operate properly
  """
  def get_relationship_fields(self, fields):

    relationships = []

    for field in fields:
      if 'relationship' in field.data_type or 'file' in field.data_type:
        relationships.append(field)

    return relationships


  """
  Delete a column from a table in the database

  @param (object) field
      A fully qualfied Field object

  @see Documentation on the db.Column.drop() functionality
      https://sqlalchemy-migrate.readthedocs.org/en/latest/api.html \
          #migrate.changeset.schema.ChangesetColumn.drop

      Documentation on selecting the existing column
      http://docs.sqlalchemy.org/en/rel_0_8/orm/mapper_config.html \
          #naming-columns-distinctly-from-attribute-names
  """
  def delete_storage_field(self, template, field):

    """
    Create a new custom table for a Feature Type
    """
    exisitng_table = db.Table(template.storage, db.metadata, autoload=True, autoload_with=db.engine)

    """
    We must bind the engine to the metadata here in order for our fields to
    recognize the existing Table we have loaded in the following steps
    """
    db.metadata.bind = db.engine

    """
    Delete the new column just like we would if we were hard coding the model
    """
    if not field.data_type is 'relationship' or not field.data_type is 'file':
      exisitng_table.c[field.name].drop()

    return True


  """
  Create a valid response to be served to the user

  @param (object) self

  @param (object)/(list) the_content
      A list of templates or a single template object to be delivered

  @param (str) list_name
      If the `the_content` is really a list then we should give int
      a name for the list to be keyed as in the returned JSON object

  @return (object)
      An JSON object either contianing the formatted content or an error
      message describing why the content couldn't be delivered

  """
  def endpoint_response(self, the_content, extension='json', list_name='', exclude_fields=[], code=200, **extras):

    """
    Make sure the content is ready to be served
    """
    if type(the_content) is list and extension == 'json':
      the_content = {
        list_name: self.serialize_list(the_content)
      }
    elif type(the_content) is list:
      the_content = self.serialize_list(the_content)
    else:
      the_content = self.serialize_object(the_content)

    """
    If the user is properly authenticated, then proceed to see if they
    have requests a type of content we serve
    """
    if (extension == 'json'):

      this_data = JSON(the_content, list_name=list_name, exclude_fields=exclude_fields, **extras)
      return this_data.create(), code

    elif (extension == 'geojson'):

      this_data = GeoJSON(the_content, list_name=list_name, exclude_fields=exclude_fields, **extras)
      return this_data.create(), code

    elif (extension == 'csv'):

      this_data = CSV(the_content, exclude_fields=exclude_fields)
      return this_data.create(), code

    """
    If the user hasn't requested a specific content type then we should
    tell them that, by directing them to an "Unsupported Media Type"
    """
    return status_.status_415(), 415
