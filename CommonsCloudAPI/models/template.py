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
Import Commons Cloud Dependencies
"""
from CommonsCloudAPI.models.base import CommonsModel

from CommonsCloudAPI.extensions import db
from CommonsCloudAPI.extensions import logger
from CommonsCloudAPI.extensions import sanitize
from CommonsCloudAPI.extensions import status as status_

from CommonsCloudAPI.models.application import Application


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
class ApplicationTemplates(db.Model, CommonsModel):

  __tablename__ = 'application_templates'
  __table_args__ = {
    'extend_existing': True
  }

  application_id = db.Column(db.Integer(), db.ForeignKey('application.id'), primary_key=True)
  template_id = db.Column(db.Integer(), db.ForeignKey('template.id'), primary_key=True)
  templates = db.relationship('Template', backref=db.backref("application_templates", cascade="all,delete", uselist=False))


"""
User to Template Association
"""
class UserTemplates(db.Model, CommonsModel):

  __tablename__ = 'user_templates'
  __table_args__ = {
    'extend_existing': True
  }

  user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), primary_key=True)
  template_id = db.Column(db.Integer(), db.ForeignKey('template.id'), primary_key=True)
  view = db.Column(db.Boolean())
  edit = db.Column(db.Boolean())
  delete = db.Column(db.Boolean())
  is_moderator = db.Column(db.Boolean())
  is_admin = db.Column(db.Boolean())
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

  __public__ = ['id', 'name', 'help', 'storage', 'is_public', 'is_crowdsourced', 'is_moderated', 'is_listed', 'is_geospatial', 'created', 'status', 'fields']

  __tablename__ = 'template'
  __table_args__ = {
    'extend_existing': True
  }

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(60))
  help = db.Column(db.String(255))
  storage = db.Column(db.String(255))
  is_public = db.Column(db.Boolean)
  is_crowdsourced = db.Column(db.Boolean)
  is_moderated = db.Column(db.Boolean)
  is_listed = db.Column(db.Boolean)
  is_geospatial = db.Column(db.Boolean)
  created = db.Column(db.DateTime)
  status = db.Column(db.Boolean)
  fields = db.relationship('Field', secondary='template_fields', backref=db.backref('template'), cascade="all,delete")


  def __init__(self, name="", help="", storage="", is_public=True, is_crowdsourced=False, is_moderated=True, is_listed=True, is_geospatial=True, created=datetime.now(), status=True):
    self.name = name
    self.help = help
    self.storage = storage
    self.is_public = is_public
    self.is_crowdsourced = is_crowdsourced
    self.is_moderated = is_moderated
    self.is_listed = is_listed
    self.is_geospatial = is_geospatial
    self.created = created
    self.status = status


  """
  Create a new Template in the CommonsCloudAPI

  @param (object) self

  @param (dictionary) application_content
      The content that is being submitted by the user
  """
  def template_create(self, request_object, application_id):

    """
    Make sure that some data was submitted before proceeding
    """
    if not request_object.data:
      logger.error('User %d new Template request failed because they didn\'t submit any `data` with their request', \
          self.current_user.id)
      return status_.status_400('You didn\'t include any `data` with your request.'), 400

    """
    Part 1: Make sure we can use the request data as json
    """
    content_ = json.loads(request_object.data)

    """
    Make sure that we have everything we need to created the
    template successfully, including things like a Name, an associated
    Application, and a Storage mechanism
    """
    if not application_id:
      logger.error('User %d new Template request failed because they didn\'t submit an Application ID with their request', \
          self.current_user.id)
      return status_.status_400('You didn\'t include an Application to associated with the Template'), 400


    allowed_applications = self.allowed_applications()

    if not application_id in allowed_applications:
      logger.warning('User %d with Applications %s tried to access Application %d', \
          self.current_user.id, allowed_applications, application_id)
      return status_.status_401(), 401


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
      'is_public': sanitize.sanitize_boolean(content_.get('is_public', True)),
      'is_crowdsourced': sanitize.sanitize_boolean(content_.get('is_crowdsourced', False)),
      'is_moderated': sanitize.sanitize_boolean(content_.get('is_moderated', True)),
      'is_listed': sanitize.sanitize_boolean(content_.get('is_listed', True)),
      'is_geospatial': sanitize.sanitize_boolean(content_.get('is_geospatial', True)),
      'created': datetime.now(),
      'status': sanitize.sanitize_boolean(content_.get('status', True))
    }

    template_ = Template(**new_template)

    db.session.add(template_)
    db.session.commit()

    """
    Tell the system what user should have permission to
    access the newly created application
    """
    permission = {
      'view': True,
      'edit': True,
      'delete': True,
      'is_moderator': True,
      'is_admin': True
    }

    self.set_user_template_permissions(template_, permission, self.current_user)


    """
    Tell the system what Application this template belongs to
    """
    application_ = Application().query.get(application_id)
    self.set_application_template_relationship(template_, application_)


    """
    Add an 'owner' field to the Storage engine here, because we can't
    do it in the 'create_storage' because of the User model stepping on
    itself and causing problems with permissions
    """
    self.create_owner_field(template_)

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

    """
    If there's no template_id we can't do any, so display a 404
    """
    if not template_id:
      return status_.status_404('That template doesn\'t seem to exist')

    """
    Before we make a database call to get the template, we should make sure the
    user is allowed to access that template in the first place. Either because
    they have explicit permission to access it (i.e., collaborator, owner) or
    the template is marked as `is_public`
    """
    template_id_list_ = self.allowed_templates()

    if not template_id in template_id_list_:
      return status_.status_401('That isn\'t your template'), 401

    """
    If we've made it this far, then the user can access the template, just show
    it to them already.
    """
    return Template.query.get(template_id)


  def template_update(self, template_id, request_object):

    """
    If there's no template_id we can't do any, so display a 404
    """
    if not template_id:
      return status_.status_404('That template doesn\'t seem to exist')

    """
    Before we make a database call to get the template, we should make sure the
    user is allowed to access that template in the first place. Either because
    they have explicit permission to access it (i.e., collaborator, owner) or
    the template is marked as `is_public`
    """
    template_id_list_ = self.allowed_templates(permission_type='edit')

    if not template_id in template_id_list_:
      return status_.status_401('That isn\'t your template'), 401

    """
    Part 1: Load the application we wish to make changes to
    """
    template_ = Template.query.get(template_id)

    """
    Make sure that some data was submitted before proceeding
    """
    if not request_object.data:
      logger.error('User %d updating Template failed because they didn\'t submit any `data` with their request', \
          self.current_user.id)
      return status_.status_400('You didn\'t include any `data` with your request.'), 400

    template_content = json.loads(request_object.data)

    """
    Part 2: Update the fields that we have data for
    """
    if hasattr(template_, 'name'):
      template_.name = sanitize.sanitize_string(template_content.get('name', template_.name))

    if hasattr(template_, 'help'):
      template_.help = sanitize.sanitize_string(template_content.get('help', template_.help))

    if hasattr(template_, 'is_crowdsourced'):
      template_.is_crowdsourced = sanitize.sanitize_boolean(template_content.get('is_crowdsourced', template_.is_crowdsourced))

    if hasattr(template_, 'is_listed'):
      template_.is_listed = sanitize.sanitize_boolean(template_content.get('is_listed', template_.is_listed))

    if hasattr(template_, 'is_moderated'):
      template_.is_moderated = sanitize.sanitize_boolean(template_content.get('is_moderated', template_.is_moderated))

    if hasattr(template_, 'is_public'):
      template_.is_public = sanitize.sanitize_boolean(template_content.get('is_public', template_.is_public))

    if hasattr(template_, 'is_geospatial'):
      template_.is_geospatial = sanitize.sanitize_boolean(template_content.get('is_geospatial', template_.is_geospatial))

    if hasattr(template_, 'status'):
      template_.status = sanitize.sanitize_boolean(template_content.get('status', template_.status))


    db.session.commit()

    return template_


  """
  Delete an existing Template from the CommonsCloudAPI

  @param (object) self

  @param (int) template_id
      The unique ID of the Template to be retrieved from the system

  @return (bool)
      A boolean to indicate if the deletion was succesful

  """
  def template_delete(self, template_id):

    """
    If there's no template_id we can't do any, so display a 404
    """
    if not template_id:
      return status_.status_404('That template doesn\'t seem to exist')

    """
    Before we make a database call to get the template, we should make sure the
    user is allowed to access that template in the first place. Either because
    they have explicit permission to access it (i.e., collaborator, owner) or
    the template is marked as `is_public`
    """
    template_id_list_ = self.allowed_templates(permission_type='delete')

    if not template_id in template_id_list_:
      return status_.status_401('That isn\'t your template'), 401

    template_ = Template.query.get(template_id)
    db.session.delete(template_)
    db.session.commit()

    return True


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

    return new_template


  """
  Get a list of Templates that belong to this Application

  """
  def application_templates_get(self, application_id):

    template_id_list_ = self.allowed_templates(application_id)

    templates_ = Template.query.filter(Template.id.in_(template_id_list_)).all()

    return templates_



  """
  Get a list of templates ids for the current application and convert
  them into a list of numbers so that our SQLAlchemy query can
  understand what's going on
  """
  def applications_templates(self, application_id):

    application_ = Application.query.get(application_id)

    templates_ = []

    for template in application_.templates:
      templates_.append(template.template_id)

    return templates_


  def allowed_templates(self, application_id='', permission_type='view'):

    if application_id:

      """
      Before doing anything make sure the user is allowed to access the
      application in the first place.
      """
      allowed_applications = self.allowed_applications()

      if not application_id in allowed_applications:
        logger.warning('User %d with Applications %s tried to access Application %d', \
            self.current_user.id, allowed_applications, application_id)
        return status_.status_401('You need to be logged in to access applications'), 401

      """
      Collect all of the templates the current user has access to, including both
      explicitly allowed templates and public templates
      """
      explicitly_allowed_templates_ = self.explicitly_allowed_templates(permission_type)
      logger.debug('All Templates user has permission to %s', explicitly_allowed_templates_)

      public_templates_ = self.public_templates()
      logger.debug('All Public Templates %s', public_templates_)

      combined_access = explicitly_allowed_templates_ + public_templates_

      """
      All Templates belonging to the requested Application
      """
      application_templates_ = self.applications_templates(application_id)
      logger.debug('All Templates for this Application %s', application_templates_)  

      """
      Using the `combined_template_access` filter the Application Templates (the
      Templates only for this Application that the user has access to)
      """
      template_id_list_ = set(combined_access) & set(application_templates_)
      logger.debug('Templates to display %s', template_id_list_)

    else:

      """
      Collect all of the templates the current user has access to, including both
      explicitly allowed templates and public templates
      """
      explicitly_allowed_templates_ = self.explicitly_allowed_templates(permission_type)
      logger.debug('All Templates user has permission to %s', explicitly_allowed_templates_)

      public_templates_ = self.public_templates()
      logger.debug('All Public Templates %s', public_templates_)

      template_id_list_ = explicitly_allowed_templates_ + public_templates_


    return template_id_list_



  """
  Get a list of templates that are marked as `is_public`
  """
  def public_templates(self):

    templates_ = Template.query.filter_by(is_public=True).all()

    public_ = []

    for template in templates_:
      public_.append(template.id)

    return public_


  """
  Get a list of template ids from the current user and convert
  them into a list of numbers so that our SQLAlchemy query can
  understand what's going on
  """
  def explicitly_allowed_templates(self, permission_type='view'):

    templates_ = []

    if not hasattr(self.current_user, 'id'):
      logger.warning('User did\'t submit their information %s', \
          self.current_user)
      return status_.status_401('You need to be logged in to access applications'), 401

    for template in self.current_user.templates:
      if permission_type and getattr(template, permission_type):
        templates_.append(template.template_id)

    return templates_


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
      logger.warning('User did\'t submit their information %s', \
          self.current_user)
      return status_.status_401('You need to be logged in to access applications'), 401

    for application in self.current_user.applications:
      if permission_type and getattr(application, permission_type):
        applications_.append(application.application_id)

    return applications_
