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
import json
import requests
from datetime import datetime


"""
Import Flask Dependencies
"""
from flask import abort
from flask import request
from flask import url_for

from flask.ext.security import current_user


"""
Import Commons Cloud Dependencies
"""
from CommonsCloudAPI.models.base import CommonsModel

from CommonsCloudAPI.extensions import db
from CommonsCloudAPI.extensions import sanitize
from CommonsCloudAPI.extensions import status as status_

from CommonsCloudAPI.utilities.format_csv import CSV
from CommonsCloudAPI.utilities.format_json import JSON


"""
Application to Template Association

Each template belongs to a specific application, even if the template is
shared across multiple applications ... each instance will need to have a 
one to one relationship (application <=> templates)

While we don't technically need to have an association table at this time,
they are working quite well for our other instances that need to have extra
attributes

Since it is very possible that we'll have more attributes than just the ID for
the Application and associated Template, we're going with AssociationTables by
default
"""
class ApplicationTemplates(db.Model):

  __tablename__ = 'application_templates'
  __table_args__ = {
    'extend_existing': True
  }

  application_id = db.Column(db.Integer(), db.ForeignKey('application.id'), primary_key=True)
  template_id = db.Column(db.Integer(), db.ForeignKey('template.id'), primary_key=True)
  templates = db.relationship('Template', backref=db.backref("application_templates", cascade="all,delete"))


"""
User to Template Association
"""
class UserTemplates(db.Model):

  __tablename__ = 'user_templates'
  __table_args__ = {
    'extend_existing': True
  }

  user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), primary_key=True)
  template_id = db.Column(db.Integer(), db.ForeignKey('template.id'), primary_key=True)
  view = db.Column(db.Boolean())
  edit = db.Column(db.Boolean())
  delete = db.Column(db.Boolean())
  templates = db.relationship('Template', backref=db.backref("user_templates", cascade="all,delete"))


"""
Template

A template within CommonsCloudAPI is backbone of the system, allowing for
organizations to collection data, a template defines the data model within
the system.

@param (object) db.Model
    The model is the Base we use to define our database structure
"""
class Template(db.Model, CommonsModel):
  
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(60))
  help = db.Column(db.String(255))
  storage = db.Column(db.String(255))
  is_public = db.Column(db.Boolean)
  is_crowdsourced = db.Column(db.Boolean)
  is_moderated = db.Column(db.Boolean)
  is_listed = db.Column(db.Boolean)
  created = db.Column(db.DateTime)
  status = db.Column(db.Boolean)
  # fields = db.relationship("Field", secondary=template_fields, backref=db.backref('templates'))
  # statistics = db.relationship("Statistic", backref=db.backref('statistics'))

  def __init__(self, name="", help="", storage="", is_public=True, is_crowdsourced=False, is_moderated=True, is_listed=True, created=datetime.now(), status=True):
    self.name = name
    self.help = help
    self.storage = storage
    self.is_public = is_public
    self.is_crowdsourced = is_crowdsourced
    self.is_moderated = is_moderated
    self.is_listed = is_listed
    self.created = created
    self.status = status


  """
  Create a new Template in the CommonsCloudAPI

  @param (object) self

  @param (dictionary) application_content
      The content that is being submitted by the user
  """
  def template_create(self, request_object):

    """
    Part 1: Make sure we can use the request data as json
    """
    content_ = json.loads(request_object.data)

    """
    Part 2: Make sure that we have everything we need to created the
    template successfully, including things like a Name, an associated
    Application, and a Storage mechanism
    """
    if not content_.get('application_id', 0):
      return abort(400)

    application_id = int(content_.get('application_id', 0))

    """
    Part 3: Make sure we have a table that has been created in the database
    to associate our Template features with
    """
    storage_name = self.create_storage()

    """
    Part X: Add the new application to the database
    """
    new_template = {
      'name': sanitize.sanitize_string(content_.get('name', 'Untitled Template from %s' % (datetime.today()) )),
      'help': sanitize.sanitize_string(content_.get('help', '')),
      'storage': storage_name,
      'is_public': content_.get('is_public', True),
      'is_crowdsourced': content_.get('is_crowdsourced', False),
      'is_moderated': content_.get('is_moderated', True),
      'is_listed': content_.get('is_listed', True),
      'created': content_.get('created', datetime.now()),
      'status': content_.get('status', True)
    }

    template_ = Template(**new_template)

    db.session.add(template_)
    db.session.commit()

    """
    Part X: Tell the system what user should have permission to
    access the newly created application
    """
    permission = {
      'view': True,
      'edit': True,
      'delete': True
    }

    self.set_user_template_permissions(template_, permission, current_user)


    """
    """
    from CommonsCloudAPI.modules.application.models import Application

    Application_ = Application()
    this_application = Application_.query.get(application_id)

    print this_application
    print this_application.id
    # self.set_user_template_permissions(template_, application_)

    return template_


  """
  Get an existing Templates from the CommonsCloudAPI

  @param (object) self

  @param (int) template_id
      The unique ID of the Template to be retrieved from the system

  @return (object) template_
      A fully qualified Template object

  """
  def template_get(self, template_id):

    template_ = Template.query.get(template_id)

    return template_


  """
  Associate a user with a specific template

  @param (object) self

  @param (object) template
      A fully qualified Template object to act on

  @param (dict) permission
      A dictionary containing boolean values for the `view`, `edit`, and `delete` properties

      Example: 

        permission = {
          'view': True,
          'edit': True,
          'delete': True
        }

  @param (object) user
      A fully qualified User object that we can act on

  @return (object) new_permission
      The permission object that was saved to the database

  """
  def set_user_template_permissions(self, template, permission, user):

    """
    Start a new Permission object
    """
    new_permission = UserTemplates(**permission)

    """
    Set the ID of the Template to act upon
    """
    new_permission.template_id = template.id

    """
    Add the new permissions defined with the user defined
    """
    user.templates.append(new_permission)
    db.session.commit()

    return new_permission

  """
  Associate a user with a specific template

  @param (object) self

  @param (object) template
      A fully qualified Template object to act on

  @param (object) application
      A fully qualified Application object that we can act on

  @return (object) new_template
      The permission object that was saved to the database

  """
  def set_application_template_relationship(self, template, application):

    """
    Start a new Permission object
    """
    new_template = ApplicationTemplates()

    """
    Set the ID of the Template to act upon
    """
    new_template.template_id = template.id

    """
    Add the new permissions defined with the user defined
    """
    application.templates.append(new_template)
    db.session.commit()

    return new_permission

    pass


  """
  Get a list of existing Templates from the CommonsCloudAPI

  @param (object) self

  @return (list) templates
      A list of templates and their given permissions for the current user

  """
  def application_list(self):

    """
    Get a list of the templates the current user has access to
    and load their information from the database
    """
    template_id_list_ = self._template_id_list()
    templates_ = Template.query.filter(Template.id.in_(template_id_list_)).all()

    return templates_


  """
  Get a list of template ids from the current user and convert
  them into a list of numbers so that our SQLAlchemy query can
  understand what's going on

  @param (object) self

  @return (list) templates_
      A list of templates the current user has access to
  """
  def _template_id_list(self):

    templates_ = []

    if not hasattr(current_user, 'id'):
      return abort(401)

    for template in current_user.templates:
      templates_.append(template.template_id)

    return templates_