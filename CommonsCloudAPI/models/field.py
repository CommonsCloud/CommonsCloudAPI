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

from CommonsCloudAPI.models.template import Template


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
  view = db.Column(db.Boolean())
  edit = db.Column(db.Boolean())
  delete = db.Column(db.Boolean())
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
  
    __public__ = ['id', 'label', 'name', 'help', 'data_type', 'relationship', 'is_listed', 'is_searchable', 'is_required', 'weight', 'status']

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
    is_listed = db.Column(db.Boolean)
    is_searchable = db.Column(db.Boolean)
    is_required = db.Column(db.Boolean)
    weight = db.Column(db.Integer)
    status = db.Column(db.Boolean)
    statistics = db.relationship('Statistic', backref=db.backref('field'))

    def __init__(self, label="", name="", help="", data_type="", relationship="", association="", is_listed=True, is_searchable=False, is_required=False, weight="", status=True, templates=[]):
        self.label = label
        self.name = name
        self.help = help
        self.data_type = data_type
        self.relationship = relationship
        self.association = association
        self.is_listed = is_listed
        self.is_searchable = is_searchable
        self.is_required = is_required
        self.weight = weight
        self.status = status
        self.templates = templates


    """
    Create a new Field in the CommonsCloudAPI

    @param (object) self

    @param (dictionary) request_object
      The content that is being submitted by the user
    """
    def field_create(self, request_object, template_id):

        """
        Section 1: Create the a new Field record
        """

        """
        Convert our request object into usable data
        """
        content_ = json.loads(request_object.data)


        """
        Fields are directly tied to Templates and really have no life of their
        own outside of Templates. Because of that we need to instantiate a 
        Template object that we can work with
        """
        Template_ = Template().query.get(template_id)


        """
        To create a Field you must at least provide a name for your field
        """
        if not content_.get('name', ''):
            return abort(400)

        user_defined_label = sanitize.sanitize_string(content_.get('name', ''))

        new_field = {
          'label': user_defined_label,
          'name': self.generate_machine_name(user_defined_label),
          'help': sanitize.sanitize_string(content_.get('help', '')),
          'data_type': sanitize.sanitize_string(content_.get('data_type', 'text')),
          'relationship': sanitize.sanitize_string(content_.get('relationship', None)),
          'is_listed': content_.get('is_listed', False),
          'is_searchable': content_.get('is_searchable', True),
          'is_required': content_.get('is_required', False),
          'weight': content_.get('created', 1),
          'status': content_.get('status', True),
          'templates': [Template_]
        }

        field_ = Field(**new_field)

        db.session.add(field_)
        db.session.commit()


        """
        Section 2: Relate the Template with the Field and the User with the Field
        """
        permission = {
          'view': True,
          'edit': True,
          'delete': True
        }

        self.set_user_field_permissions(field_, permission, current_user)
        
        # self.set_template_field_relationship(field_, Template_)


        """
        Section 3: Create the Field in the Template Storage
        """
        field_storage = self.create_storage_field(Template_, field_)

        """
        Before attempting to return the field as a JSON object, we need to
        make sure that we have a saved field to display, otherwise we'll
        start throwing errors
        """
        if not hasattr(field_, 'id'):
            return abort(404)


        return field_

    """
    Update an existing Field in the CommonsCloudAPI

    @param (object) self

    @param (dictionary) request_object
      The content that is being submitted by the user
    """
    def field_update(self, request_object, template_id, field_id):

        """
        Before attempting to return the field as a JSON object, we need to
        make sure that we have a saved field to display, otherwise we'll
        start throwing errors
        """
        if not field_id:
            return abort(404)


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
          field_.is_listed = field_content.get('is_listed', field_.is_listed)

        if hasattr(field_, 'is_searchable'):
          field_.is_searchable = field_content.get('is_searchable', field_.is_searchable)

        if hasattr(field_, 'is_required'):
          field_.is_required = field_content.get('is_required', field_.is_required)

        if hasattr(field_, 'weight'):
          field_.weight = field_content.get('weight', field_.weight)

        if hasattr(field_, 'status'):
          field_.status = field_content.get('status', field_.status)


        #
        # @todo
        #    We should probably make the 'name' of the field change if the
        #    user can change the label ... but I'm not sure at the same time.
        #    Could that mess up existing applications? Does it matter?
        #

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
    def field_get(self, field_id):
        
        field_ = Field.query.get(field_id)

        if not hasattr(field_, 'id'):
            return abort(404)

        return field_



    """
    Associate a user with a specific field

    @param (object) self

    @param (object) field
      A fully qualified Field object to act on

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

        """
        Add the new permissions defined with the user defined
        """
        template.fields.append(new_field)
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

        print template_.fields

        fields_ = []

        for field in template_.fields:
            fields_.append(field.field_id)

        return fields_


    """
    Get a list of Fields that belong to this Template

    """
    def template_fields_get(self, template_id):

        template_ = Template.query.get(template_id)

        if not hasattr(template_, 'id'):
          return abort(404)
    
        return list(template_.fields)


    """
    Delete an existing Field from the CommonsCloudAPI

    @param (object) self

    @param (int) field_id
        The unique ID of the Field to be retrieved from the system

    @return (bool)
        A boolean to indicate if the deletion was succesful

    """
    def field_delete(self, template_id, field_id):

        template_ = Template.query.get(template_id)
        field_ = Field.query.get(field_id)

        self.delete_storage_field(template_, field_)

        db.session.delete(field_)
        db.session.commit()

        return True

