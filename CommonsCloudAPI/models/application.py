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
application_templates = db.Table('application_templates',
  db.Column('application', db.Integer(), db.ForeignKey('application.id')),
  db.Column('template', db.Integer(), db.ForeignKey('template.id')),
  extend_existing = True
)


"""
Application Model

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
class Application(db.Model):

  """
  Name of the database table that holds `application` data

  @see http://docs.sqlalchemy.org/en/rel_0_9/orm/extensions/declarative.html\
        #table-configuration
  """
  __tablename__ = 'application'
  __table_args_ = {
    'extend_existing': True
  }

  """
  Fields within the data model 
  """
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(60))
  description = db.Column(db.String(255))
  url = db.Column(db.String(255))
  created = db.Column(db.DateTime)
  status = db.Column(db.Boolean)
  is_public = db.Column(db.Boolean)

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
  templates = db.relationship('Template', **{
    'secondary': application_templates, 
    'backref': db.backref('application')
  })

  """
  Initialize the data model and let the system know how each field should be
  handled by default 
  """
  def __init__(self, name="", url="", description=None, 
                created=datetime.utcnow(), status=True,
                is_public=True, templates=[]):
    self.name = name
    self.url = url
    self.description = description
    self.created = created
    self.status = status
    self.is_public = is_public

