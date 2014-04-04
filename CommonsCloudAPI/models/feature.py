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

        storage = str('type_' + storage_)

        Template_ = Template.query.filter_by(storage=storage).first()

        """
        Relationships and Attachments
        """
        attachments = self._get_fields_of_type(Template_, 'file')
        relationships = self._get_fields_of_type(Template_, 'relationships')

        print attachments
        print relationships

        Storage_ = self.get_storage(Template_)

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
        Create the new feature and save it to the database
        """
        new_feature = Storage_(**content_)

        db.session.add(new_feature)
        db.session.commit()

        return new_feature

    def feature_get(self, storage_, feature_id):

        storage = str('type_' + storage_)

        Template_ = Template()
        Field_ = Field()

        this_template = Template_.query.filter_by(storage=storage).first()

        Storage_ = self.get_storage(this_template, this_template.fields)

        feature = Storage_.query.get(feature_id)

        the_geometry = db.session.scalar(ST_AsGeoJSON(feature.geometry))

        feature.geometry = json.loads(the_geometry)

        if not hasattr(feature, 'id'):
            return abort(404)

        return feature

    def feature_update(self, request_object, template_id, feature_id):
        pass

    def feature_statistic(self, storage_, search_path):

        storage = str('type_' + storage_)

        this_template = Template.query.filter_by(storage=storage).first()

        Model_ = self.get_storage(this_template)

        endpoint_ = FunctionAPI(db.session, Model_)

        return endpoint_.get()

    def feature_list(self, storage_):

        storage = str('type_' + storage_)

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

        storage = str('type_' + storage_)

        this_template = Template.query.filter_by(storage=storage).first()

        Storage_ = self.get_storage(this_template)

        feature = Storage_.query.get(feature_id)

        if not hasattr(feature, 'id'):
            return abort(404)

        db.session.delete(feature)
        db.session.commit()

        return True

    def _get_fields_of_type(self, template_, type_):

      fields_ = []

      for field in template_.fields:
        if field.data_type == type_:
          fields_.append(field.name)

      return fields_
