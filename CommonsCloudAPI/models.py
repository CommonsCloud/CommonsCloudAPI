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
Import Flask Dependencies
"""
from flask import Module
from flask.ext.security import UserMixin
from flask.ext.security import RoleMixin
from flask.ext.security import SQLAlchemyUserDatastore
from werkzeug import generate_password_hash
from werkzeug import check_password_hash


"""
Import Commons Cloud Dependencies
"""
from .extensions import db


"""
Defines association tables to enable many to many relationships
"""
application_templates = db.Table('application_templates',
    db.Column('application', db.Integer, db.ForeignKey('application.id')),
    db.Column('template', db.Integer, db.ForeignKey('template.id'))
)

template_fields = db.Table('template_fields',
  db.Column('template', db.Integer, db.ForeignKey('template.id')),
  db.Column('field', db.Integer, db.ForeignKey('field.id'))
)

user_roles = db.Table('user_roles',
    db.Column('user', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role', db.Integer(), db.ForeignKey('role.id'))
)

user_permissions = db.Table('user_permissions',
    db.Column('user', db.Integer(), db.ForeignKey('user.id')),
    db.Column('permission', db.Integer, db.ForeignKey('permission.id'))
)


class Client(db.Model):
    client_id = db.Column(db.String(40), primary_key=True)
    client_secret = db.Column(db.String(55), nullable=False)

    user_id = db.Column(db.ForeignKey('user.id'))
    user = db.relationship('User')

    _redirect_uris = db.Column(db.Text)
    _default_scopes = db.Column(db.Text)

    @property
    def client_type(self):
        return 'public'

    @property
    def redirect_uris(self):
        if self._redirect_uris:
            return self._redirect_uris.split()
        return []

    @property
    def default_redirect_uri(self):
        return self.redirect_uris[0]

    @property
    def default_scopes(self):
        if self._default_scopes:
            return self._default_scopes.split()
        return []


class Grant(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE')
    )
    user = db.relationship('User')

    client_id = db.Column(
        db.String(40), db.ForeignKey('client.client_id'),
        nullable=False,
    )
    client = db.relationship('Client')

    code = db.Column(db.String(255), index=True, nullable=False)

    redirect_uri = db.Column(db.String(255))
    expires = db.Column(db.DateTime)

    _scopes = db.Column(db.Text)

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []


class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(
        db.String(40), db.ForeignKey('client.client_id'),
        nullable=False,
    )
    client = db.relationship('Client')

    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id')
    )
    user = db.relationship('User')

    # currently only bearer is supported
    token_type = db.Column(db.String(40))

    access_token = db.Column(db.String(255), unique=True)
    refresh_token = db.Column(db.String(255), unique=True)
    expires = db.Column(db.DateTime)
    _scopes = db.Column(db.Text)

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []


"""
Define our individual models
"""
class Application(db.Model):

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(60))
  description = db.Column(db.String(255))
  owner = db.Column(db.Integer)
  created = db.Column(db.DateTime)
  status = db.Column(db.Boolean)
  templates = db.relationship("Template", secondary=application_templates, backref=db.backref('applications'))

  def __init__(self, name, owner, description=None, templates=[]):
      self.name = name
      self.description = description
      self.owner = owner
      self.created = datetime.utcnow()
      self.status = True
      self.templates = templates


class Template(db.Model):
  
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(60))
  description = db.Column(db.String(255))
  storage = db.Column(db.String(255))
  owner = db.Column(db.Integer)
  created = db.Column(db.DateTime)
  publicly_viewable = db.Column(db.Boolean)
  crowd_sourcing = db.Column(db.Boolean)
  moderate = db.Column(db.Boolean)
  status = db.Column(db.Boolean)
  is_listed = db.Column(db.Boolean)
  fields = db.relationship("Field", secondary=template_fields, backref=db.backref('templates'))
  statistics = db.relationship("Statistic", backref=db.backref('statistics'))

  def __init__(self, name, storage, owner, description="", publicly_viewable="", crowd_sourcing="", moderate="", applications=None):
    self.name = name
    self.description = description
    self.storage = storage
    self.owner = owner
    self.publicly_viewable = publicly_viewable
    self.crowd_sourcing = crowd_sourcing
    self.moderate = moderate
    self.created = datetime.utcnow()
    self.applications = applications
    self.is_listed = True
    self.status = True


"""
Defines the Model for how Template fields are stored
"""
class Field(db.Model):

  id = db.Column(db.Integer, primary_key=True)
  label = db.Column(db.String(100))
  name = db.Column(db.String(100))
  help_text = db.Column(db.String(255))
  data_type = db.Column(db.String(100))
  field_type = db.Column(db.String(100))
  relationship = db.Column(db.String(255))
  required = db.Column(db.Boolean)
  weight = db.Column(db.Integer)
  status = db.Column(db.Boolean)
  in_list = db.Column(db.Boolean)

  def __init__(self, label, name, help_text, data_type, field_type, required, weight, in_list, templates, relationship):
    self.label = label
    self.name = name
    self.help_text = help_text
    self.data_type = data_type
    self.field_type = field_type
    self.required = required
    self.weight = weight
    self.relationship = relationship
    self.status = True
    self.in_list = in_list
    self.templates = templates


"""
Define our individual models
"""
class Statistic(db.Model):

  id = db.Column(db.Integer, primary_key=True)
  template = db.Column(db.Integer, db.ForeignKey('template.id'))
  field = db.Column(db.Integer, db.ForeignKey('field.id'))
  name = db.Column(db.String(255))
  units = db.Column(db.String(24))
  math_type = db.Column(db.String(24))
  created = db.Column(db.DateTime)
  status = db.Column(db.Boolean)

  def __init__(self, name, units, math_type, template=[], field=[]):
      self.template = template
      self.field = field
      self.name = name
      self.units = units
      self.math_type = math_type
      self.created = datetime.utcnow()
      self.status = True



"""
Define our individual models
"""
class Permission(db.Model):

  id = db.Column(db.Integer, primary_key=True)
  type = db.Column(db.String(255))
  type_id = db.Column(db.Integer)
  can_view = db.Column(db.Boolean)
  can_create = db.Column(db.Boolean)
  can_edit_own = db.Column(db.Boolean)
  can_edit_any = db.Column(db.Boolean)
  can_delete_own = db.Column(db.Boolean)
  can_delete_any = db.Column(db.Boolean)
  is_admin = db.Column(db.Boolean)
  is_moderator = db.Column(db.Boolean)

  def __init__(self, type, type_id, can_view=False, can_create=False, can_edit_own=False, can_edit_any=False, can_delete_own=False, can_delete_any=False, is_admin=False, is_moderator=False):
    self.type = type
    self.type_id = type_id
    self.can_view = can_view
    self.can_create = can_create
    self.can_edit_own = can_edit_own
    self.can_edit_any = can_edit_any
    self.can_delete_own = can_delete_own
    self.can_delete_any = can_delete_any
    self.is_admin = is_admin
    self.is_moderator = is_moderator


"""
This defines our basic Role model, we have to have this becasue of the
Flask-Security module. If you remove it Flask-Security gets fussy.
"""
class Role(db.Model, RoleMixin):

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(80), unique=True)
  description = db.Column(db.String(255))


"""
This defines our basic User model, we have to have this becasue of the
Flask-Security module. If you remove it Flask-Security gets fussy.
"""
class User(db.Model, UserMixin):

  id = db.Column(db.Integer, primary_key=True)
  firstname = db.Column(db.String(255))
  lastname = db.Column(db.String(255))
  title = db.Column(db.String(255))
  bio = db.Column(db.String(255))
  email = db.Column(db.String(255))
  password = db.Column(db.String(255))
  active = db.Column(db.Boolean())
  confirmed_at = db.Column(db.DateTime())
  roles = db.relationship('Role', secondary=user_roles, backref=db.backref('user'))
  permissions = db.relationship('Permission', secondary=user_permissions, backref=db.backref('user'))
  
  def set_password(self, password):
      self.password = generate_password_hash(password, method='pbkdf2:sha1', salt_length=64)

  def check_password(self, password):
      return check_password_hash(self.password, password)


"""
The last thing we need to do is actually hook these things up to the
User Datastore provided by Mongo Engine's datastore that provides
Flask-Security with User/Role information so we can lock down access
to the system and it's resources.
"""
user_datastore = SQLAlchemyUserDatastore(db, User, Role)