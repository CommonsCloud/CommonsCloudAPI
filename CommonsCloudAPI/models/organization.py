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
Import Commons Cloud Dependencies
"""
from CommonsCloudAPI.extensions import db


"""
Relationship Lookup Tables

These tables are necessary to perform our many to many relationships

@see https://pythonhosted.org/Flask-SQLAlchemy/models.html#many-to-many-relationships
   This documentation is specific to Flask using sqlalchemy

@see http://docs.sqlalchemy.org/en/rel_0_9/orm/relationships.html#relationships-many-to-many
   This documentation covers SQLAlchemy
"""
organization_addresses = db.Table('organization_addresses',
  db.Column('organization', db.Integer(), db.ForeignKey('organization.id')),
  db.Column('address', db.Integer(), db.ForeignKey('address.id')),
  extend_existing = True
)

organization_territories = db.Table('organization_territories',
  db.Column('organization', db.Integer(), db.ForeignKey('organization.id')),
  db.Column('territory', db.Integer(), db.ForeignKey('territory.id')),
  extend_existing = True
)

organization_telephone = db.Table('organization_telephone',
  db.Column('organization', db.Integer(), db.ForeignKey('organization.id')),
  db.Column('telephone', db.Integer(), db.ForeignKey('telephone.id')),
  extend_existing = True
)

class Organization(db.Model):

  """
  Name of the database table that holds `organization` data

  @see http://docs.sqlalchemy.org/en/rel_0_9/orm/extensions/declarative.html#table-configuration
  """
  __tablename__ = 'organization'
  __table_args__ = {
    'extend_existing': True
  }

  """
  Fields within the data model 
  """
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(255), unique=True)
  description = db.Column(db.String(255))

  """
  Back References from other models

  Relationships that are many-to-many need to contain a `secondary` keyword argument within the
  db.relationship method in order to function properly.

  @see https://pythonhosted.org/Flask-SQLAlchemy/models.html#many-to-many-relationships
   This documentation is specific to Flask using sqlalchemy

  @see http://docs.sqlalchemy.org/en/rel_0_9/orm/relationships.html#relationships-many-to-many
   This documentation covers SQLAlchemy
  """
  addresses = db.relationship('Address', secondary=organization_addresses, backref=db.backref('organization'))
  territories = db.relationship('Territory', secondary=organization_territories, backref=db.backref('organization'))
  telephone = db.relationship('Telephone', secondary=organization_telephone, backref=db.backref('organization'))
