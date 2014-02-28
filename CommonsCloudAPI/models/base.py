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


"""
Import Flask Dependencies
"""
from flask import request


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


