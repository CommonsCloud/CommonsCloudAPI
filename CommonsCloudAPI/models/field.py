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

from CommonsCloudAPI.models.application import Template

from CommonsCloudAPI.utilities.format_csv import CSV
from CommonsCloudAPI.utilities.format_json import JSON


"""
Field to Template Association
"""
class TemplateFields(db.Model):

  __tablename__ = 'application_templates'
  __table_args__ = {
    'extend_existing': True
  }

  template_id = db.Column(db.Integer(), db.ForeignKey('template.id'), primary_key=True)
  field_id = db.Column(db.Integer(), db.ForeignKey('field.id'), primary_key=True)
  fields = db.relationship('Field', backref=db.backref("template_fields", cascade="all,delete"))


"""
Field

A field that helps make up a Template within CommonsCloudAPI

@param (object) db.Model
    The model is the Base we use to define our database structure

@param (object) CommonsModel
    The base model for which all CommonsCloudAPI models stem
"""
class Field(db.Model, CommonsModel):
  
  id = db.Column(db.Integer, primary_key=True)
  label = db.Column(db.String(100))
  name = db.Column(db.String(100))
  help = db.Column(db.String(255))
  data_type = db.Column(db.String(100))
  field_type = db.Column(db.String(100))
  relationship = db.Column(db.String(255))
  is_listed = db.Column(db.Boolean)
  is_searchable = db.Column(db.Boolean)
  is_required = db.Column(db.Boolean)
  weight = db.Column(db.Integer)
  status = db.Column(db.Boolean)

  def __init__(self, label="", name="", help="", data_type="", field_type="", relationship="", is_listed=True, is_searchable=False, is_required=False, weight="", status=True):
    self.label = label
    self.name = name
    self.help = help
    self.data_type = data_type
    self.field_type = field_type
    self.relationship = relationship
    self.is_listed = is_listed
    self.is_searchable = is_searchable
    self.is_required = is_required
    self.weight = weight
    self.status = status


  
