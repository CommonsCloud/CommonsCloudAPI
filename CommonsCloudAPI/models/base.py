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

from collections import OrderedDict

from migrate.changeset import *


"""
Import Flask Dependencies
"""
from flask import abort
from flask import request

from geoalchemy2.types import Geometry

from sqlalchemy.orm import ColumnProperty

"""
Import Commons Cloud Dependencies
"""
from CommonsCloudAPI.extensions import db
from CommonsCloudAPI.extensions import status as status_

from CommonsCloudAPI.utilities.format_csv import CSV
from CommonsCloudAPI.utilities.format_json import JSON

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

      for key in _content.__mapper__.c.keys():
        if key in self.__public__:
          result[key] = getattr(_content, key)

      #
      # @todo This needs some work, it's really close, but not quite there
      #       `result[key].append(item.template_id)` is the only thing that
      #       needs to be wrapped to make this thing complete.
      #
      
      # for key in _content.__mapper__.relationships.keys():
      #   if key in self.__public_relationships__ and _content.__mapper__.relationships[key].uselist:
      #     result[key] = []
      #     for item in getattr(_content, key):
      #       result[key].append(item.template_id)
            
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
        for key in object_.__mapper__.c.keys():
          if key in self.__public__:
            result[key] = getattr(object_, key)

        list_.append(result)

      return list_


  """
  Remove all characters except for spaces and alpha-numeric characters,
  replace all spaces in a string with underscores, change all uppercase
  letters to lowercase letters, and return the updated string.
  """
  def generate_machine_name(self, human_name):
    return re.sub('[^0-9a-zA-Z ]+', '', human_name).replace(' ','_').lower()


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
      "time": db.Time(),
      "point": Geometry('POINT'),
      "polygon": Geometry('POLYGON'),
      "linestring": Geometry('LINESTRING'),
      "geometry": Geometry('GEOMETRY')
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
      'storage': table_name
    }

  def generate_attachment_field(self, field, template):

    """
    Before we can create a relationship between Attachments and a Template
    we need to create a Table in the database to retain our attachments
    """
    attachment_table_name = self.generate_template_hash(_prefix='attachment_')

    new_table = db.Table(attachment_table_name, db.metadata,
      db.Column('id', db.Integer, primary_key=True),
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
    self.generate_relationship_field(field, template)

    return {
      'type': 'file',
      'storage': attachment_table_name
    }


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
      db.Column('created', db.DateTime()),
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
      return

    if field.data_type == 'file':
      return

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

    """
    Load an existing table into our metadata
    """
    Table_ = db.Table(template.storage, db.metadata, autoload=True, autoload_with=db.engine)

    """
    We must bind the engine to the metadata here in order for our fields to
    recognize the existing Table we have loaded in the following steps
    """
    db.metadata.bind = db.engine

    class_name = str(template.storage)

    arguments = {
        "__table__": Table_,
        "__tablename__": class_name,
        "__table_args__": {
            "extend_existing": True
        }
    }


    Model = type(class_name, (db.Model,), arguments)

    """
    For the API to return items properly, we should check to see if the fields
    we are attempting to call are marked as listed or not.
    """
    if fields:
        
      public_fields = self.__public__

      for field in fields:
        if field.is_listed:
          public_fields.append(field.name)

      self.__public__ = public_fields

    return Model


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
  def endpoint_response(self, the_content, list_name='', exclude_fields=[], code=200):

    """
    Make sure the content is ready to be served
    """
    if type(the_content) is list:
      the_content = {
        list_name: self.serialize_list(the_content)
      }
    else:
      the_content = self.serialize_object(the_content)

    """
    If the user is properly authenticated, then proceed to see if they
    have requests a type of content we serve
    """
    if request.headers['Content-Type'] == 'application/json' or \
        ('format' in request.args and request.args['format'] == 'json'):

      this_data = JSON(the_content, list_name=list_name, exclude_fields=exclude_fields)
      return this_data.create(), code

    elif request.headers['Content-Type'] == 'text/csv' or \
        ('format' in request.args and request.args['format'] == 'csv'):

      this_data = CSV(the_content_, exclude_fields=exclude_fields)
      return this_data.create(), code

    """
    If the user hasn't requested a specific content type then we should
    tell them that, by directing them to an "Unsupported Media Type"
    """
    return status_.status_415(), 415




# """
# Define our individual models
# """
# class Statistic(db.Model):

#   id = db.Column(db.Integer, primary_key=True)
#   template = db.Column(db.Integer, db.ForeignKey('template.id'))
#   field = db.Column(db.Integer, db.ForeignKey('field.id'))
#   name = db.Column(db.String(255))
#   units = db.Column(db.String(24))
#   math_type = db.Column(db.String(24))
#   created = db.Column(db.DateTime)
#   status = db.Column(db.Boolean)

#   def __init__(self, name, units, math_type, template=[], field=[]):
#       self.template = template
#       self.field = field
#       self.name = name
#       self.units = units
#       self.math_type = math_type
#       self.created = datetime.utcnow()
#       self.status = True


