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
from functools import wraps


"""
Import Flask Dependencies
"""
from flask import abort


"""
Import Commons Cloud Dependencies
"""
from CommonsCloudAPI.models.base import CommonsModel

from CommonsCloudAPI.extensions import db
from CommonsCloudAPI.extensions import logger
from CommonsCloudAPI.extensions import sanitize
from CommonsCloudAPI.extensions import status as status_

from CommonsCloudAPI.models.template import Template


"""
is_public allows us to check if feature collections are supposed to public, if
they are, then we don't need to check for OAuth crednetials to allow access
"""
class is_public(object):

    def __init__(self):
      pass

    def __call__(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):

          if 'template_id' in kwargs:
            element_ = Template.query.get(kwargs['template_id'])
          elif 'field_id' in kwargs:
            element_ = Field.query.get(kwargs['field_id'])

          keywords = kwargs

          if not element_.is_public:
            keywords['is_public'] = False
          else:
            keywords['is_public'] = True

          return f(*args, **keywords)
     
        return decorated_function

"""
Field to Template Association
"""
class TemplateFields(db.Model):

    __tablename__ = 'template_fields'
    __table_args__ = {
        'extend_existing': True
    }

    template_id = db.Column(db.Integer(), db.ForeignKey('template.id'), primary_key=True)
    field_id = db.Column(db.Integer(), db.ForeignKey('field.id'), primary_key=True)
    fields = db.relationship('Field', backref=db.backref("template_fields", cascade="all,delete"))


"""
User to Template Association
"""
class UserFields(db.Model):

  __tablename__ = 'user_fields'
  __table_args__ = {
    'extend_existing': True
  }

  user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), primary_key=True)
  field_id = db.Column(db.Integer(), db.ForeignKey('field.id'), primary_key=True)
  read = db.Column(db.Boolean())
  write = db.Column(db.Boolean())
  is_admin = db.Column(db.Boolean())
  templates = db.relationship('Field', backref=db.backref("user_fields", cascade="all,delete"))


"""
Field

A field that helps make up a Template within CommonsCloudAPI

@param (object) db.Model
    The model is the Base we use to define our database structure

@param (object) CommonsModel
    The base model for which all CommonsCloudAPI models stem
"""
class Field(db.Model, CommonsModel):

    __public__ = {'default': ['id', 'label', 'name', 'help', 'data_type', 'relationship', 'is_public', 'is_visible', 'is_listed', 'is_searchable', 'is_required', 'weight', 'status', 'options']}

    __tablename__ = 'field'
    __table_args__ = {
        'extend_existing': True
    }

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(100))
    name = db.Column(db.String(100))
    help = db.Column(db.String(255))
    data_type = db.Column(db.String(100))
    relationship = db.Column(db.String(255))
    association = db.Column(db.String(255))
    is_visible = db.Column(db.Boolean)
    is_public = db.Column(db.Boolean)
    is_listed = db.Column(db.Boolean)
    is_searchable = db.Column(db.Boolean)
    is_required = db.Column(db.Boolean)
    weight = db.Column(db.Integer)
    status = db.Column(db.Boolean)
    options = db.Column(db.Text)
    statistics = db.relationship('Statistic', backref=db.backref('field'), cascade="all,delete")

    def __init__(self, label="", name="", help="", data_type="", relationship="", association="", is_public=True, is_visible=True, is_listed=True, is_searchable=False, is_required=False, weight="", status=True, options="", templates=[]):
        self.label = label
        self.name = name
        self.help = help
        self.data_type = data_type
        self.relationship = relationship
        self.association = association
        self.is_visible = is_visible
        self.is_public = is_public
        self.is_listed = is_listed
        self.is_searchable = is_searchable
        self.is_required = is_required
        self.weight = weight
        self.status = status
        self.options = options
        self.templates = templates


    """
    Create a new Field in the CommonsCloudAPI

    @param (object) self

    @param (dictionary) request_object
      The content that is being submitted by the user
    """
    def field_create(self, request_object, template_id):

        """
        Make sure that we have everything we need to created the
        template successfully, including things like a Name, an associated
        Application, and a Storage mechanism
        """
        if not template_id:
          logger.error('User %d new Field request failed because they didn\'t submit an Template ID with their request', \
              self.current_user.id)
          return status_.status_400('You didn\'t include a Template to add this field to ... or else you\'re not the admin of this Template'), 400

        """
        Make sure that some data was submitted before proceeding
        """
        if not request_object.data:
          logger.error('User %d new Field request failed because they didn\'t submit any `data` with their request', \
              self.current_user.id)
          return status_.status_400('You didn\'t include any `data` with your request.'), 400

        """
        Convert our request object into usable data
        """
        content_ = json.loads(request_object.data)

        """
        Fields are directly tied to Templates and really have no life of their
        own outside of Templates. Because of that we need to instantiate a
        Template object that we can work with
        """
        allowed_fields = self.allowed_fields(template_id)
        if not template_id in allowed_fields:
          logger.warning('User %d with Templates %s tried to access Template %d', \
              self.current_user.id, allowed_fields, template_id)
          return status_.status_401(), 401

        Template_ = Template().query.get(template_id)

        """
        To create a Field you must at least provide a name for your field
        """
        if not content_.get('name', ''):
          logger.error('User %d new Field request failed because they didn\'t submit any `name` in the `data` of their request', \
              self.current_user.id)
          return status_.status_400('You didn\'t include a `name` in the `data` of your request.'), 400

        """
        To create a Field you must at least provide a data_type for your field
        """
        if not content_.get('data_type', ''):
          logger.error('User %d new Field request failed because they didn\'t submit any `data_type` in the `data` of their request', \
              self.current_user.id)
          return status_.status_400('You didn\'t include a `data_type` in the `data` of your request.'), 400
        elif 'relationship' in content_.get('data_type', '') and not content_.get('relationship', ''):
          logger.error('User %d new Field request failed because they didn\'t submit any `data_type` in the `data` of their request', \
              self.current_user.id)
          return status_.status_400('You can\'t create a Relationship field without specifying the `relationship` ... this starts with type_'), 400


        user_defined_label = sanitize.sanitize_string(content_.get('name', ''))

        """
        If someone's creating a relationship the storage string they've specified
        needs to belong to a template that they are allowed to access
        """
        if content_.get('relationship', ''):

          relationship_storage = content_.get('relationship', '')
          storage_check = Template().query.filter_by(storage=relationship_storage).first()

          if not storage_check.id in allowed_fields:
            logger.error('User %d tried to add a Field to a Template %d which they do not own', \
                self.current_user.id, template_id)
            return status_.status_401('The Template `relationship` string you entered either doesn\'t exist or you don\'t have permission to use it'), 401

          """
          Lastly, make sure that an identical relationship doesn't already exist.
          If the type_ and the template type_ already have a relationship it will
          cause bad things to happen when searching via the API
          """
          duplicate_check = self.check_relationship_field_duplicate(Template_.fields, relationship_storage)
          if duplicate_check:
            logger.warning('User %d tried to add a duplicate relationship type', \
                self.current_user.id, template_id)
            return status_.status_400('You already defined a relationship with this Template, you cannot create two relationship fields with the same relationship table.'), 400

        new_field = {
          'label': user_defined_label,
          'name': self.generate_machine_name(user_defined_label),
          'help': sanitize.sanitize_string(content_.get('help', '')),
          'data_type': sanitize.sanitize_string(content_.get('data_type', 'text')),
          'relationship': sanitize.sanitize_string(content_.get('relationship', None)),
          'is_public': sanitize.sanitize_boolean(content_.get('is_public', False)),
          'is_visible': sanitize.sanitize_boolean(content_.get('is_visible', False)),
          'is_listed': sanitize.sanitize_boolean(content_.get('is_listed', False)),
          'is_searchable': sanitize.sanitize_boolean(content_.get('is_searchable', True)),
          'is_required': sanitize.sanitize_boolean(content_.get('is_required', False)),
          'weight': sanitize.sanitize_integer(content_.get('created', 1)),
          'status': sanitize.sanitize_boolean(content_.get('status', True)),
          'options': sanitize.sanitize_string(content_.get('options', '')),
          'templates': [Template_]
        }

        logger.debug('Checking Field, %s', new_field)

        field_ = Field(**new_field)

        db.session.add(field_)
        db.session.commit()

        logger.warning('field %s', field_)


        """
        Section 2: Relate the Template with the Field and the User with the Field
        """
        permission = {
          'read': True,
          'write': True,
          'is_admin': True
        }

        self.set_user_field_permissions(field_, permission, self.current_user)

        self.set_template_field_relationship(field_, Template_)


        """
        Section 3: Create the Field in the Template Storage, if the field will
                   hold data. Some fields, like fieldset, are only for visual
                   and aesthetic purposes and do not need added to the Storage
        """
        if not 'fieldset' in field_.data_type:
          field_storage = self.create_storage_field(Template_, field_)

          if 'relationship' in content_.get('data_type', 'text') or 'file' in content_.get('data_type', 'text'):
              field_.association = field_storage['association']
              field_.relationship = field_storage['relationship']
              db.session.commit()

        return field_

    """
    Update an existing Field in the CommonsCloudAPI

    @param (object) self

    @param (dictionary) request_object
      The content that is being submitted by the user
    """
    def field_update(self, request_object, template_id, field_id):

        """
        Make sure that we have everything we need to created the
        template successfully, including things like a Name, an associated
        Application, and a Storage mechanism
        """
        if not field_id:
          logger.error('User %d update Field request failed because they didn\'t submit a Field ID with their request', \
              self.current_user.id)
          return status_.status_400('You didn\'t include a Field ID to update this field with'), 400

        """
        Fields are directly tied to Templates and really have no life of their
        own outside of Templates. Because of that we need to instantiate a
        Template object that we can work with
        """
        allowed_fields = self.allowed_fields(permission_type='write')
        if not field_id in allowed_fields:
          logger.warning('User %d with Fields %s tried to access Field %d', \
              self.current_user.id, allowed_fields, field_id)
          return status_.status_401('You can\'t edit this Field because it\'s not yours'), 401

        """
        Make sure that some data was submitted before proceeding
        """
        if not request_object.data:
          logger.error('User %d update Field request failed because they didn\'t submit any `data` with their request', \
              self.current_user.id)
          return status_.status_400('You didn\'t include any `data` with your request.'), 400

        """
        Convert our request object into usable data
        """
        field_content = json.loads(request_object.data)

        """
        Fields are directly tied to Templates and really have no life of their
        own outside of Templates. Because of that we need to instantiate a
        Template object that we can work with
        """
        field_ = Field().query.get(field_id)

        """
        Part 2: Update the fields that we have data for
        """
        if hasattr(field_, 'label'):
          field_.label = sanitize.sanitize_string(field_content.get('label', field_.label))

        if hasattr(field_, 'help'):
          field_.help = sanitize.sanitize_string(field_content.get('help', field_.help))

        if hasattr(field_, 'is_listed'):
          field_.is_listed = sanitize.sanitize_boolean(field_content.get('is_listed', field_.is_listed))

        if hasattr(field_, 'is_searchable'):
          field_.is_searchable = sanitize.sanitize_boolean(field_content.get('is_searchable', field_.is_searchable))

        if hasattr(field_, 'is_required'):
          field_.is_required = sanitize.sanitize_boolean(field_content.get('is_required', field_.is_required))

        if hasattr(field_, 'weight'):
          field_.weight = sanitize.sanitize_integer(field_content.get('weight', field_.weight))

        if hasattr(field_, 'status'):
          field_.status = sanitize.sanitize_boolean(field_content.get('status', field_.status))

        if hasattr(field_, 'options'):
          field_.options = sanitize.sanitize_string(field_content.get('options', field_.options))

        #
        # @todo
        #    We probably need to make the API capable of changing
        #    data_types, after all, PostgreSQL does it out of the box
        #
        # @see
        #    http://www.postgresql.org/docs/9.3/static/sql-altertable.html
        #

        db.session.commit()

        return field_


    """
    Retrieve an existing Field from the CommonsCloudAPI

    @param (object) self

    @param (int) field_id
      The unique ID of the Field to be retrieved from the system

    @return (object) field_
      A fully qualified Field object

    """
    def field_get(self, field_id, is_public=False):

      if not is_public:
        """
        Make sure that we have everything we need to created the
        template successfully, including things like a Name, an associated
        Application, and a Storage mechanism
        """
        if not field_id:
          logger.error('User %d update Field request failed because they didn\'t submit a Field ID with their request', \
              self.current_user.id)
          return status_.status_400('You didn\'t include a Field ID to update this field with'), 400

        """
        Fields are directly tied to Templates and really have no life of their
        own outside of Templates. Because of that we need to instantiate a
        Template object that we can work with
        """
        allowed_fields = self.allowed_fields(permission_type='read')

        public_fields_ = self.public_templates()

        if not field_id in allowed_fields + public_fields_:
          logger.warning('User %d with Fields %s tried to access Field %d', \
              self.current_user.id, allowed_fields, field_id)
          return status_.status_401('You can\'t edit this Field because it\'s not yours'), 401

      field_ = {}

      if field_id:
        field_ = Field.query.get(field_id)

      return field_



    """
    Associate a user with a specific field

    @param (object) self

    @param (object) field
      A fully qualified Field object to act on

    @param (dict) permission
      A dictionary containing boolean values for the `read`, `write`, and `is_admin` properties

      Example:

        permission = {
          'read': True,
          'write': True,
          'is_admin': True
        }

    @param (object) user
      A fully qualified User object that we can act on

    @return (object) new_permission
      The permission object that was saved to the database

    """
    def set_user_field_permissions(self, field, permission, user):

        """
        Start a new Permission object
        """
        new_permission = UserFields(**permission)

        """
        Set the ID of the Template to act upon
        """
        new_permission.field_id = field.id

        """
        Add the new permissions defined with the user defined
        """
        user.fields.append(new_permission)
        db.session.commit()

        return new_permission


    """
    Associate a Field with a specific Template

    @param (object) self

    @param (object) field
      A fully qualified Field object to act on

    @param (object) template
      A fully qualified Template object that we can act on

    @return (object) new_field
      The permission object that was saved to the database

    """
    def set_template_field_relationship(self, field, template):

        """
        Start a new Permission object
        """
        new_field = TemplateFields()

        """
        Set the ID of the Template to act upon
        """
        new_field.field_id = field.id
        new_field.template_id = template.id

        db.session.add(new_field)
        db.session.commit()

        return new_field

    """
    Get a list of field ids for the current template and convert
    them into a list of numbers so that our SQLAlchemy query can
    understand what's going on

    @param (object) self

    @return (list) field
        A list of fields the current user has access to
    """
    def _template_fields_id_list(self, template_id):

        template_ = Template.query.get(template_id)

        fields_ = []

        for field in template_.fields:
            fields_.append(field.field_id)

        return fields_


    """
    Get a list of Fields that belong to this Template

    """
    def template_fields_get(self, template_id, is_public=False):

        """
        Make sure that we have everything we need to created the
        template successfully, including things like a Name, an associated
        Application, and a Storage mechanism
        """
        if not template_id:
          logger.error('User %d update Field request failed because they didn\'t submit a Template ID with their request', \
              self.current_user.id)
          return status_.status_400('You didn\'t include a Template ID to get a list of fields with'), 400

        template_ = Template.query.get(template_id)
        fields_ = []

        if not is_public:

          """
          Fields are directly tied to Templates and really have no life of their
          own outside of Templates. Because of that we need to instantiate a
          Template object that we can work with
          """
          allowed_templates = self.allowed_fields(template_id=template_id)

          if not template_id in allowed_templates:
            logger.warning('User %d with Templates %s tried to access Template Fields %d', \
                self.current_user.id, allowed_templates, template_id)
            return status_.status_401('You can\'t edit this Template because it\'s not yours'), 401

          allowed_fields = self.allowed_fields()
          public_fields_ = self.public_templates()

          allowed_fields_list = allowed_fields + public_fields_

          for field in template_.fields:
              if field.id in allowed_fields_list:
                  fields_.append(field)
  
        else:
          for field in template_.fields:
            fields_.append(field)

        return fields_


    """
    Delete an existing Field from the CommonsCloudAPI

    @param (object) self

    @param (int) field_id
        The unique ID of the Field to be retrieved from the system

    @return (bool)
        A boolean to indicate if the deletion was succesful

    """
    def field_delete(self, template_id, field_id):

        """
        Fields are directly tied to Templates and really have no life of their
        own outside of Templates. Because of that we need to instantiate a
        Template object that we can work with
        """
        allowed_templates = self.allowed_fields(template_id=template_id,permission_type='is_admin')

        if not template_id in allowed_templates:
          logger.warning('User %d with Templates %s tried to access Template Fields %d', \
              self.current_user.id, allowed_templates, template_id)
          return status_.status_401('You can\'t delete this Field because it\'s Template is not yours'), 401

        allowed_fields = self.allowed_fields(permission_type='is_admin')

        if not field_id in allowed_fields:
          logger.warning('User %d with Fields %s tried to delete Field %d', \
              self.current_user.id, allowed_fields, field_id)
          return status_.status_401('You can\'t delete this Field because it\'s not yours'), 401

        template_ = Template.query.get(template_id)
        field_ = Field.query.get(field_id)

        db.session.delete(field_)
        db.session.commit()

        """
        We only want to call the next method, if and when the field actually
        exists in the Storage database table. In the case of some special
        fields, such as the `fieldset` tag, the column doesn't exist in the
        database table for the Storage, only in the Field table.
        """
        if not 'fieldset' in field_.data_type:
          self.delete_storage_field(template_, field_)

        return True


    def allowed_fields(self, template_id='', permission_type='read'):

        if template_id:

            """
            Collect all of the templates the current user has access to, including both
            explicitly allowed templates and public templates
            """
            explicitly_allowed_templates_ = self.explicitly_allowed_templates(permission_type)
            logger.debug('All Templates user has permission to %s', explicitly_allowed_templates_)

            public_templates_ = self.public_templates()
            logger.debug('All Public Templates %s', public_templates_)

            id_list_ = explicitly_allowed_templates_ + public_templates_
            logger.debug('All Fields user has permission to %s', id_list_)

        else:
            id_list_ = self.explicitly_allowed_fields(permission_type)
            logger.debug('All Fields user has permission to %s', id_list_)

        return id_list_


    def check_relationship_field_duplicate(self, fields, relationship):

      for field in fields:
        if relationship in field.relationship:
          return True

      return False



    """
    Get a list of templates that are marked as `is_public`
    """
    def public_fields(self):

        fields_ = Field.query.filter_by(is_public=True).all()

        public_ = []

        for field in fields_:
            public_.append(field.id)

        return public_

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
    Get a list of templates that are marked as `is_public`
    """
    def community_templates(self):

        templates_ = Template.query.filter_by(is_community=True).all()

        community_ = []

        for template in templates_:
            community_.append(template.id)

        return community_


    """
    Get a list of template ids from the current user and convert
    them into a list of numbers so that our SQLAlchemy query can
    understand what's going on
    """
    def explicitly_allowed_templates(self, permission_type='read'):

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
    Get a list of template ids from the current user and convert
    them into a list of numbers so that our SQLAlchemy query can
    understand what's going on
    """
    def explicitly_allowed_fields(self, permission_type='read'):

        fields_ = []

        if not hasattr(self.current_user, 'id'):
          logger.warning('User did\'t submit their information %s', \
              self.current_user)
          return status_.status_401('You need to be logged in to access applications'), 401

        for field in self.current_user.fields:
          if permission_type and getattr(field, permission_type):
            fields_.append(field.field_id)

        return fields_
