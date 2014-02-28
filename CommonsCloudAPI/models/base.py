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

from migrate.changeset import *


"""
Import Flask Dependencies
"""
from flask import abort
from flask import request

from geoalchemy2.types import Geometry

"""
Import Commons Cloud Dependencies
"""
from CommonsCloudAPI.extensions import db
from CommonsCloudAPI.extensions import status as status_

from CommonsCloudAPI.utilities.format_csv import CSV
from CommonsCloudAPI.utilities.format_json import JSON


class CommonsModel(object):

  def __init__(self):
    pass

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

    this_field_type = field.data_type

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
      "geometry": Geometry('GEOMETRY'),
      "relationship": self.generate_relationship_field(field, template)
    }


    if this_field_type == 'file':
      data_type = generate_file_field(field)
    else:
      data_type = fields[field.data_type]

    return data_type

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
      'name': field.relationship,
      'relationship': template.storage
    }

  """
  Create a table in the database that contains a base line of defaults
  """
  def create_storage(self, table_name=""):

    if not table_name:
      table_name = self.generate_template_hash()
    
    """
    Create a new custom table for a Feature Type
    """
    new_table = db.Table(table_name, db.metadata,
      db.Column('id', db.Integer, primary_key=True),
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
  def endpoint_response(self, the_content, list_name='', code=200):

    """
    If the user is properly authenticated, then proceed to see if they
    have requests a type of content we serve
    """
    if request.headers['Content-Type'] == 'application/json' or \
        ('format' in request.args and request.args['format'] == 'json'):

      this_data = JSON(the_content, serialize=True, list_name=list_name)
      return this_data.create(), code

    elif request.headers['Content-Type'] == 'text/csv' or \
        ('format' in request.args and request.args['format'] == 'csv'):

      this_data = CSV(the_content, serialize=True)
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


