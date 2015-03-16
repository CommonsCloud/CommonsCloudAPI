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


"""
Import CommonsCloud Dependencies
"""
from CommonsCloudAPI.extensions import db


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
