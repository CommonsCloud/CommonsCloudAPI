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

from flask.ext.security import current_user

from geoalchemy2.functions import ST_AsGeoJSON

from flask.ext.restless.views import API
from flask.ext.restless.views import FunctionAPI



"""
Import Commons Cloud Dependencies
"""
from CommonsCloudAPI.models.base import CommonsModel

from CommonsCloudAPI.models.template import Template
from CommonsCloudAPI.models.field import Field

from CommonsCloudAPI.extensions import db
from CommonsCloudAPI.extensions import sanitize
from CommonsCloudAPI.extensions import status as status_

from CommonsCloudAPI.utilities.geometry import ST_GeomFromGeoJSON


"""
Define our individual models
"""
class Feature(CommonsModel):

    __public__ = ['id', 'name', 'created', 'status', 'geometry']

    def __init__(self):
        pass

    def feature_create(self, request_object, storage_):

        print 'creation for ', storage_

        storage = self.validate_storage(storage_)
        Template_ = Template.query.filter_by(storage=storage).first()
        Storage_ = self.get_storage(Template_)

        print Storage_
        print dir(Storage_)

        """
        Relationships and Attachments
        """
        attachments = self._get_fields_of_type(Template_, 'file')
        relationships = self._get_fields_of_type(Template_, 'relationship')

        """
        Setup the request object so that we can work with it
        """
        request_ = json.loads(request_object.data)
        content_ = request_

        """
        Check for a geometry and if it exists, we need to add a new geometry
        key to the content_ dictionary
        """
        geometry_ = content_.get('geometry', None)
        if geometry_ is not None:
            content_['geometry'] = ST_GeomFromGeoJSON(json.dumps(geometry_))

        """
        Set our created and status attributes based on user input or at least
        setup the default
        """
        content_['created'] = content_.get('created', datetime.now())
        content_['status'] = content_.get('status', 'public')

        """
        Strip and re-process any relationships or attachments
        """
        new_content = {}

        for field_ in content_:
          if field_ not in relationships:
            new_content[field_] = content_.get(field_, None)

        """
        Create the new feature and save it to the database
        """
        print 'Complete Feature ready for submission > ', new_content, new_content.keys()

        new_feature = Storage_(**new_content)
        db.session.add(new_feature)
        db.session.commit()

        for field_ in content_:
          if field_ in relationships:
            this_field = content_.get(field_, None)
            association_table = self._get_field_association(Template_, field_)
            print 'association_table', association_table
            new_feature_relationships = self.feature_relationships(this_field, new_feature.id, association_table)

        db.session.commit()

        return new_feature

    def feature_get(self, storage_, feature_id):

        storage = self.validate_storage(storage_)

        Template_ = Template()
        Field_ = Field()

        this_template = Template_.query.filter_by(storage=storage).first()

        Storage_ = self.get_storage(this_template, this_template.fields)

        feature = Storage_.query.get(feature_id)

        if this_template.is_geospatial and feature.geometry is not None:
          print 'feature.geometry', feature.geometry
          the_geometry = db.session.scalar(ST_AsGeoJSON(feature.geometry))

          feature.geometry = json.loads(the_geometry)

        if not hasattr(feature, 'id'):
            return abort(404)

        return feature

    def feature_update(self, request_object, template_id, feature_id):
        pass

    def feature_statistic(self, storage_, search_path):

        storage = self.validate_storage(storage_)

        this_template = Template.query.filter_by(storage=storage).first()

        Model_ = self.get_storage(this_template)

        endpoint_ = FunctionAPI(db.session, Model_)

        return endpoint_.get()

    def feature_list(self, storage_):

        storage = self.validate_storage(storage_)

        this_template = Template.query.filter_by(storage=storage).first()

        Model_ = self.get_storage(this_template)

        #
        # @todo
        #       This is where we need to get a list of fields, from the
        #       template `this_template` that have an `is_listed` value
        #       of True in the database
        #
        # @todo
        #       We also need to make sure we're post processing the data
        #       so that GeoJSON is being returned properly and so that
        #       we can easily export to other formats.
        #
        #
        arguments = {
            "include_columns": ['id', 'well_name'],
            "preprocessors": {
                'GET_SINGLE': [],
                'GET_MANY': []
            }
        }

        endpoint_ = API(db.session, Model_, **arguments)

        return endpoint_._search()

    def feature_delete(self, storage_, feature_id):

        storage = self.validate_storage(storage_)

        this_template = Template.query.filter_by(storage=storage).first()

        Storage_ = self.get_storage(this_template)

        feature = Storage_.query.get(feature_id)

        if not hasattr(feature, 'id'):
            return abort(404)

        db.session.delete(feature)
        db.session.commit()

        return True

    def feature_relationships(self, content, parent_id, association_table):

      if not type(content) is list:
        abort(500)

      print 'association_table', type(association_table), association_table
      Storage_ = self.get_storage(str(association_table))

      for child_feature in content:
        if 'id' in child_feature:
          relationship_ = Storage_(parent_id=parent_id, child_id=child_feature['id'])
          db.session.add(relationship_)


    def _feature_relationship_associate(self):
      pass

    def _feature_relationship_create(self, request_object, ):
      # for storage in new_feature.__mapper__.relationships.keys():
      #   self.feature_create(self, request_object, storage_)
      pass

    def feature_attachments(self):
      print 'attachment processing > '
      pass

    def _feature_attachment_associate(self):
      pass

    def _feature_attachment_create(self):
      pass

    def _get_field_association(self, template, relationship):

      for field in template.fields:
        if field.relationship == relationship:
          return field.association

    def _get_fields_of_type(self, template_, type_):

      fields_ = []

      for field in template_.fields:
        if field.data_type == type_:
          if type_ == 'relationship':
            fields_.append(field.relationship)
          else:
            fields_.append(field.name)

      return fields_
