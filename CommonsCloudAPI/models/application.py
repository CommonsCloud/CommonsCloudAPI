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

from datetime import datetime


"""
Import Flask Dependencies
"""
from flask import abort
from flask import request


"""
Import Commons Cloud Dependencies
"""
from CommonsCloudAPI.models.base import CommonsModel

from CommonsCloudAPI.extensions import db
from CommonsCloudAPI.extensions import logger
from CommonsCloudAPI.extensions import sanitize
from CommonsCloudAPI.extensions import status as status_


class UserApplications(db.Model, CommonsModel):

  __tablename__ = 'user_applications'
  __table_args__ = {
    'extend_existing': True
  }

  user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), primary_key=True)
  application_id = db.Column(db.Integer(), db.ForeignKey('application.id'), primary_key=True)
  view = db.Column(db.Boolean())
  edit = db.Column(db.Boolean())
  delete = db.Column(db.Boolean())
  is_moderator = db.Column(db.Boolean())
  is_admin = db.Column(db.Boolean())
  applications = db.relationship('Application', backref=db.backref("user_applications", cascade="all,delete"))


"""
Define our individual models
"""
class Application(db.Model, CommonsModel):

  __public__ = ['id', 'name', 'description', 'url', 'created', 'status']

  __tablename__ = 'application'
  __table_args__ = {
    'extend_existing': True
  }

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(60))
  description = db.Column(db.String(255))
  url = db.Column(db.String(255))
  created = db.Column(db.DateTime)
  status = db.Column(db.Boolean)
  templates = db.relationship('ApplicationTemplates', backref=db.backref('application'), cascade="all,delete")


  def __init__(self, name="", url="", description=None, created=datetime.utcnow(), status=True, templates=[], current_user_={}):
    self.name = name
    self.description = description
    self.url = url
    self.created = created
    self.status = status
    self.templates = templates
    self.current_user = current_user_


  """
  Create a new application in the API
  """
  def application_create(self, request_object):

    """
    Make sure that some data was submitted before proceeding
    """
    if not request_object.data:
      logger.error('User %d new Application request failed because they didn\'t submit any `data` with their request', \
          self.current_user.id)
      return status_.status_400('You didn\'t include any `data` with your request.'), 400

    """
    Prepare the data for use
    """
    application_content = json.loads(request_object.data)

    """
    Make sure we have at least a name for our Application
    """
    if not application_content.get('name', ''):
      logger.error('User %d new Application request failed because the did not include a `name` in the `data`', \
          self.current_user.id)
      return status_.status_400('You didn\'t include a `name` in the `data` of your request. You have to do that with Applications.'), 400

    """
    Add the new application to the database
    """
    new_application = {
      'name': sanitize.sanitize_string(application_content.get('name', '')),
      'description': sanitize.sanitize_string(application_content.get('description', '')),
      'url': application_content.get('url', '')
    }

    application_ = Application(**new_application)

    db.session.add(application_)
    db.session.commit()

    """
    Tell the system what user should have permission to
    access the newly created application
    """
    permission = {
      'view': True,
      'edit': True,
      'delete': True
    }

    self.set_user_application_permissions(application_, permission, self.current_user)

    """
    Return the newly created Application
    """
    return application_


  """
  Get a single, existing Application from the API
  """
  def application_get(self, application_id):

    allowed_applications = self.allowed_applications()

    if not application_id in allowed_applications:
      logger.warning('User %d with Applications %s tried to access Application %d', \
          self.current_user.id, allowed_applications, application_id)
      return abort(404)

    return Application.query.get(application_id)


  """
  Get a list of existing Applications from the API
  """
  def application_list(self):

    """
    Get a list of the applications the current user has access to
    and load their information from the database
    """
    allowed_applications = self.allowed_applications()

    """
    No further check is needed here because we're only return the ID's of the
    applications that we already know the user has access to. If the list is
    empty then we don't need to perform a database query and can just return
    an empty list
    """
    if len(allowed_applications) >= 1:
      return Application.query.filter(Application.id.in_(allowed_applications)).all()

    return []


  """
  Create a new application in the CommonsCloudAPI

  @param (object) self

  @param (dictionary) application_content
      The content that is being submitted by the user
  """
  def application_update(self, application_id, request_object):

    allowed_applications = self.allowed_applications('edit')
    
    if not application_id in allowed_applications:
      logger.warning('User %d with Applications %s tried to update Application %d', \
          self.current_user.id, allowed_applications, application_id)
      return abort(401)

    application_ = Application.query.get(application_id)

    application_content = json.loads(request_object.data)

    """
    Part 2: Update the fields that we have data for
    """
    if hasattr(application_, 'name'):
      application_.name = sanitize.sanitize_string(application_content.get('name', application_.name))

    if hasattr(application_, 'description'):
      application_.description = sanitize.sanitize_string(application_content.get('description', application_.description))

    if hasattr(application_, 'url'):
      application_.url = sanitize.sanitize_string(application_content.get('url', application_.url))

    db.session.commit()

    return application_


  """
  Get an existing Applications from the CommonsCloudAPI

  @param (object) self

  @param (int) application_id
      The unique ID of the Application to be retrieved from the system

  @return (object) application_
      A fully qualified Application object

  """
  def application_delete(self, application_id):

    allowed_applications = self.allowed_applications('delete')

    if not application_id in allowed_applications:
      logger.warning('User %d with Applications %s tried to delete Application %d', \
          self.current_user.id, allowed_applications, application_id)
      return abort(401)

    application_ = Application.query.get(application_id)

    db.session.delete(application_)
    db.session.commit()



  """
  Associate a user with a specific application

  @param (object) self

  @param (object) application
      A fully qualified Application object to act on

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
  def set_user_application_permissions(self, application, permission, user):

    """
    Start a new Permission object
    """
    new_permission = UserApplications(**permission)

    """
    Set the ID of the Application to act upon
    """
    new_permission.application_id = application.id

    """
    Add the new permissions defined with the user defined
    """
    user.applications.append(new_permission)
    db.session.commit()

    return new_permission


  """
  Get a list of application ids from the current user and convert
  them into a list of numbers so that our SQLAlchemy query can
  understand what's going on

  @param (object) self

  @return (list) applications_
      A list of applciations the current user has access to
  """
  def allowed_applications(self, permission_type='view'):

    applications_ = []

    if not hasattr(self.current_user, 'id'):
      return abort(401)

    for application in self.current_user.applications:
      if permission_type and getattr(application, permission_type):
        applications_.append(application.application_id)

    return applications_
