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


import hashlib


"""
Import Flask Dependencies
"""
from flask.ext.security import current_user
from flask.ext.security import UserMixin
from flask.ext.security import RoleMixin

from werkzeug import generate_password_hash
from werkzeug import check_password_hash


"""
Import Commons Cloud Dependencies
"""
from CommonsCloudAPI.extensions import db

from CommonsCloudAPI.models.address import Address
from CommonsCloudAPI.models.organization import Organization
from CommonsCloudAPI.models.role import Role
from CommonsCloudAPI.models.telephone import Telephone
from CommonsCloudAPI.models.territory import Territory


"""
Relationship Lookup Tables

These tables are necessary to perform our many to many relationships

@see https://pythonhosted.org/Flask-SQLAlchemy/models.html#many-to-many-relationships
   This documentation is specific to Flask using sqlalchemy

@see http://docs.sqlalchemy.org/en/rel_0_9/orm/relationships.html#relationships-many-to-many
   This documentation covers SQLAlchemy
"""
user_roles = db.Table('user_roles',
  db.Column('user', db.Integer(), db.ForeignKey('user.id')),
  db.Column('role', db.Integer(), db.ForeignKey('role.id')),
  extend_existing = True
)

user_organizations = db.Table('user_organizations',
  db.Column('user', db.Integer(), db.ForeignKey('user.id')),
  db.Column('organization', db.Integer(), db.ForeignKey('organization.id')),
  extend_existing = True
)

user_addresses = db.Table('user_addresses',
  db.Column('user', db.Integer(), db.ForeignKey('user.id')),
  db.Column('address', db.Integer(), db.ForeignKey('address.id')),
  extend_existing = True
)

user_territories = db.Table('user_territories',
  db.Column('user', db.Integer(), db.ForeignKey('user.id')),
  db.Column('territory', db.Integer(), db.ForeignKey('territory.id')),
  extend_existing = True
)

user_telephone = db.Table('user_telephone',
  db.Column('user', db.Integer(), db.ForeignKey('user.id')),
  db.Column('telephone', db.Integer(), db.ForeignKey('telephone.id')),
  extend_existing = True
)


"""
This defines our basic User model, we have to have this becasue of the
Flask-Security module. If you remove it Flask-Security gets fussy.
"""
class User(db.Model, UserMixin):

  __public__ = {'default': ['id', 'name', 'email', 'active', 'confirmed_at']}

  """
  Name of the database table that holds `user` data

  @see http://docs.sqlalchemy.org/en/rel_0_9/orm/extensions/declarative.html#table-configuration
  """
  __tablename__ = 'user'
  __table_args__ = {
    'extend_existing': True
  }

  """
  Fields within the data model 
  """
  id = db.Column(db.Integer, primary_key=True)

  """
  User Account Personal Information
  """
  first_name = db.Column(db.String(255))
  last_name = db.Column(db.String(255))
  description = db.Column(db.String(255))
  title = db.Column(db.String(255))

  """
  User Account Security Credentials
  """
  email = db.Column(db.String(255))
  password = db.Column(db.String(255))

  """
  User Account Status
  """
  active = db.Column(db.Boolean())
  confirmed_at = db.Column(db.DateTime())

  """
  User Account Login Statistics
  """
  last_login_date = db.Column(db.DateTime())
  current_login_date = db.Column(db.DateTime())
  last_login_ip_address = db.Column(db.String(16))
  current_login_ip_address = db.Column(db.String(16))
  total_login_count = db.Column(db.Integer)

  """
  Back References from other models

  Relationships that are many-to-many need to contain a `secondary` keyword argument within the
  db.relationship method in order to function properly.

  @see https://pythonhosted.org/Flask-SQLAlchemy/models.html#many-to-many-relationships
   This documentation is specific to Flask using sqlalchemy

  @see http://docs.sqlalchemy.org/en/rel_0_9/orm/relationships.html#relationships-many-to-many
   This documentation covers SQLAlchemy
  """
  roles = db.relationship('Role', secondary=user_roles, backref=db.backref('users'))
  organizations = db.relationship('Organization', secondary=user_organizations, backref=db.backref('users'))
  addresses = db.relationship('Address', secondary=user_addresses, backref=db.backref('users'))
  territories = db.relationship('Territory', secondary=user_territories, backref=db.backref('users'))
  telephone = db.relationship('Telephone', secondary=user_telephone, backref=db.backref('users'))

  # applications = db.relationship('UserApplications', backref=db.backref('users'))
  # templates = db.relationship('UserTemplates', backref=db.backref('users'))
  # fields = db.relationship('UserFields', backref=db.backref('users'))

  def __init__(self, name="", email="", password="", active=True, roles=[], \
      organizations=[], addresses=[], territories=[], telephone=[], permissions=[]):
    self.name = name
    self.email = email
    self.password = password
    self.active = active
    self.roles = roles
    self.organizations = organizations
    self.addresses = addresses
    self.territories = territories
    self.telephone = telephone
    self.permissions = permissions

  """
  Set the user password using the pbkdf2:sha1 method and a salt_length of 64
  """
  def set_password(self, password):
    self.password = generate_password_hash(password, method='pbkdf2:sha1', salt_length=64)

  """
  Check to see if the password entered by the user matches the password saved
  in the database associated with the acting user

  @param (object) self
  @param (string) password
      The password to check against the database

  @return (bool)
      The boolean of whether or not the passwords match

  """
  def check_password(self, password):
    return check_password_hash(self.password, password)

  
  def user_create(self, new_user):
    new_user_ = User(**new_user)

    db.session.add(new_user_)
    db.session.commit()

    return new_user_


  """
  Get the SQLAlchemy User object for the current_user

  @param (object) self

  @return (object) user_
      The object of the current user, not to be confused with current_user

  """
  def user_get(self, user_id):
    
    user_ = User.query.get(user_id)

    if not user_:
      return status_.status_404('We couldn\'t find the user you were looking for.'), 404

    return {
      'active': user_.active,
      'confirmed_at': user_.confirmed_at,
      'email': user_.email,
      'id': user_.id,
      'first_name': user_.first_name,
      'last_name': user_.last_name,
      # 'notifications': user_.notifications,
      # 'occurrences': user_.occurrences,
      'picture': self.user_picture(user_.email),
      'roles': user_.roles
      # 'member_since': user_.confirmed_at.strftime('%b %d, %Y'),
    }


  """
  Get the a list of User objects for the entire system

  @return (array) users_
      The array of objects for all users in system

  """
  def user_list(self):
    users_ = User.query.all()
    return users_

  def user_update(self, user_object_):

    """
    Before updating any information we first have to load the User object for the
    user we wish to act upon. To make extra sure that one user doesn't update another
    by sending an alertnative 'id' through with the post request. We only act on the
    `current_user` as defined by the security module.
    """
    user_ = User.query.get(current_user.id)

    """
    Content that needs sanitized
    """
    user_.name = sanitize.sanitize_string(user_object_.get('name', current_user.name))
    user_.email = sanitize.sanitize_string(user_object_.get('email', current_user.email))

    """
    Booleans and Arrays are not sanitized right now ... they probably should be
    """
    # user_.active = user_object_.get('active', current_user.active)
    # user_.roles = user_object_.get('roles', current_user.roles)
    # user_.permissions = user_object_.get('permissions', current_user.permissions)

    """
    Save all of our updates to the database
    """
    db.session.commit()

    return user_


  """
  Remove a user entirely from our system

  This should be a multiple step process:

  1. User arrives at the "Remove account" page
  2. Message is displayed warning the user of ramifications of account removal
  3. User must type in their current password

  """
  def user_remove(self):
    pass


  def user_picture(self, email):

    user_email = email.lower()
    user_hash = hashlib.md5(user_email).hexdigest()

    picture_url = '//www.gravatar.com/avatar/' + user_hash

    return picture_url


from flask.ext.security import SQLAlchemyUserDatastore

from .role import Role

"""
Hook the User model and the Role model up to the User Datastore provided
by SQLAlchemy's Engine's datastore that provides Flask-Security with
User/Role information so we can lock down access to the system and it's
resources.
"""
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
