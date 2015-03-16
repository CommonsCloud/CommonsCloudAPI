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
from datetime import datetime


"""
Import CommonsCloudAPI Dependencies
"""
from CommonsCloudAPI.extensions import db


"""
Relationship Lookup Tables

These tables are necessary to perform our many to many relationships

@see https://pythonhosted.org/Flask-SQLAlchemy/models.html\
      #many-to-many-relationships
   This documentation is specific to Flask using sqlalchemy

@see http://docs.sqlalchemy.org/en/rel_0_9/orm/relationships.html\
      #relationships-many-to-many
   This documentation covers SQLAlchemy
"""
template_fields = db.Table('template_fields',
  db.Column('template', db.Integer(), db.ForeignKey('template.id')),
  db.Column('field', db.Integer(), db.ForeignKey('field.id')),
  extend_existing = True
)

# template_activity = db.Table('template_activity',
#   db.Column('template', db.Integer(), db.ForeignKey('template.id')),
#   db.Column('activity', db.Integer(), db.ForeignKey('activity.id')),
#   extend_existing = True
# )

"""
Template Model

@arg (object) db.Model
   This model is subclassed from the Flask-SQLAlchemy db.Model provided by
   using the Flask-SQLAlchemy package. db.Model is actually just a Declarative
   Base that is pre-defined when you use Flask-SQLAlchemy.

@see http://docs.sqlalchemy.org/en/rel_0_9/orm/extensions/declarative.html\
      #sqlalchemy.ext.declarative.declarative_base
   For more information on using Declarative Base

@see https://pythonhosted.org/Flask-SQLAlchemy/models.html
   For more information about declaring models within Flask-SQLAlchemy

"""
class Template(db.Model):

  """
  Name of the database table that holds `template` data

  @see http://docs.sqlalchemy.org/en/rel_0_9/orm/extensions/declarative.html\
        #table-configuration
  """
  __tablename__ = 'template'
  __table_args_ = {
    'extend_existing': True
  }

  """
  Fields within the data model 
  """
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(60))
  help = db.Column(db.String(255))
  storage = db.Column(db.String(255))
  created = db.Column(db.DateTime)
  status = db.Column(db.Boolean)

  has_acl = db.Column(db.Boolean)
  is_public = db.Column(db.Boolean)
  is_crowdsourced = db.Column(db.Boolean)
  is_moderated = db.Column(db.Boolean)
  is_listed = db.Column(db.Boolean)
  is_geospatial = db.Column(db.Boolean)
  is_community = db.Column(db.Boolean)

  """
  Back References from other models

  Relationships that are many-to-many need to contain a `secondary`keyword
  argument within the db.relationship method in order to function properly.

  @see https://pythonhosted.org/Flask-SQLAlchemy/models.html\
        #many-to-many-relationships
      This documentation is specific to Flask using sqlalchemy

  @see http://docs.sqlalchemy.org/en/rel_0_9/orm/relationships.html\
        #relationships-many-to-many
      This documentation covers SQLAlchemy
  """
  fields = db.relationship('Field', **{
    'secondary': template_fields, 
    'backref': db.backref('template')
  })

  # activities = db.relationship('Activity', **{
  #   'secondary': template_activity, 
  #   'backref': db.backref('template')
  # })

  """
  Initialize the data model and let the system know how each field should be
  handled by default 
  """
  def __init__(self, name="", help="", storage="", has_acl=True,
                is_public=True, is_crowdsourced=False, is_moderated=True,
                is_listed=True, is_geospatial=True, is_community=True,
                created=datetime.now(), status=True, fields=[], activities=[]):
    self.name = name
    self.help = help
    self.storage = storage
    self.created = created
    self.status = status

    self.fields = fields
    self.activities = activities

    self.has_acl = has_acl
    self.is_public = is_public
    self.is_crowdsourced = is_crowdsourced
    self.is_moderated = is_moderated
    self.is_listed = is_listed
    self.is_geospatial = is_geospatial
    self.is_community = is_community

