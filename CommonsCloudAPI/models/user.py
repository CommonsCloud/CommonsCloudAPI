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
from flask.ext.security import SQLAlchemyUserDatastore

from werkzeug import generate_password_hash
from werkzeug import check_password_hash


"""
Import Commons Cloud Dependencies
"""
from CommonsCloudAPI.extensions import db
from CommonsCloudAPI.extensions import logger
from CommonsCloudAPI.extensions import sanitize
from CommonsCloudAPI.extensions import status as status_

from CommonsCloudAPI.models.base import CommonsModel
from CommonsCloudAPI.models.template import UserTemplates
from CommonsCloudAPI.models.application import UserApplications


user_roles = db.Table('user_roles',
  db.Column('user', db.Integer(), db.ForeignKey('user.id')),
  db.Column('role', db.Integer(), db.ForeignKey('role.id')),
  extend_existing = True
)


"""
This defines our basic Role model, we have to have this becasue of the
Flask-Security module. If you remove it Flask-Security gets fussy.
"""
class Role(db.Model, RoleMixin):

  __tablename__ = 'role'
  __table_args__ = {
    'extend_existing': True
  }

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(80), unique=True)
  description = db.Column(db.String(255))


"""
This defines our basic User model, we have to have this becasue of the
Flask-Security module. If you remove it Flask-Security gets fussy.
"""
class User(db.Model, UserMixin, CommonsModel):

  __public__ = {'default': ['id', 'name', 'email', 'active', 'confirmed_at']}

  __tablename__ = 'user'
  __table_args__ = {
    'extend_existing': True
  }

  """
  Define the fields that we will use to create the User table in our
  database for use with our SQLAlchemy model
  """
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(255))
  email = db.Column(db.String(255))
  password = db.Column(db.String(255))
  active = db.Column(db.Boolean())
  confirmed_at = db.Column(db.DateTime())
  roles = db.relationship('Role', secondary=user_roles, backref=db.backref('users'))
  applications = db.relationship('UserApplications', backref=db.backref('users'))
  templates = db.relationship('UserTemplates', backref=db.backref('users'))
  fields = db.relationship('UserFields', backref=db.backref('users'))

  def __init__(self, name="", email="", password="", active=True, roles=[], permissions=[]):
    self.name = name
    self.email = email
    self.password = password
    self.active = active
    self.roles = roles
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
    return user_


  """
  Get the a list of User objects for the entire system

  @return (array) users_
      The array of objects for all users in system

  """
  def user_list(self):
    users_ = User.query.all()
    return users_


  """
  Get the a list of User objects limited to a specific Application

  @return (array) users_
      The array of objects for all Application Users in system

  """
  def application_user_list(self, application_id):

    user_list = []

    ApplicationUsers = UserApplications.query.filter_by(application_id=application_id).all()

    for user in ApplicationUsers:
      user_list.append(user.user_id)

    return User.query.filter(User.id.in_(user_list)).all()


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

    picture_url = '//www.gravatar.com/avatar/' + user_hash + '?s=172'

    return picture_url


  """
  Get a list of Users that have access to the Application requested by
  the user, but make sure the User requesting this information is logged
  in already and has `is_admin` permission to the requested Applciation
  """
  def application_users(self, application_id):

    allowed_applications = self.allowed_applications('is_admin')

    if not application_id in allowed_applications:
      logger.warning('User %d with Applications %s tried to access Users for Application %d', \
          self.current_user.id, allowed_applications, application_id)
      return status_.status_401('You are not allowed to view the Users of this Application because you do not have the permission to do so'), 401

    return self.application_user_list(application_id)



"""
The last thing we need to do is actually hook these things up to the
User Datastore provided by SQLAlchemy's Engine's datastore that provides
Flask-Security with User/Role information so we can lock down access
to the system and it's resources.
"""
user_datastore = SQLAlchemyUserDatastore(db, User, Role)

