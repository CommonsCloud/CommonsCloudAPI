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


"""
Define our individual models
"""
class Feature(CommonsModel):

    __public__ = ['id', 'name', 'created', 'status']

    def __init__(self):
        pass

    def feature_create(self, request_object, storage):

        Template_ = Template.query.filter_by(storage=storage).first()

        Storage_ = self.get_storage(Template_)

        print 'Storage_'
        print dir(Storage_)

        content_ = json.loads(request_object.data)

        content_['created'] = content_.get('created', datetime.now())
        content_['status'] = content_.get('status', 'public')

        new_feature = Storage_(**content_)

        db.session.add(new_feature)
        db.session.commit()

        return new_feature

    def feature_get(self, storage, feature_id):

        Template_ = Template()
        Field_ = Field()

        this_template = Template_.query.filter_by(storage=storage).first()
        fields_ = Field_.template_fields_get(this_template.id)

        Storage_ = self.get_storage(this_template, fields_)

        feature = Storage_.query.get(feature_id)

        if not hasattr(feature, 'id'):
            return abort(404)

        return feature

    def feature_list(self, storage):

        Template_ = Template.query.filter_by(storage=storage).first()
        Storage_ = self.get_storage(Template_)

        features = Storage_.query.all()

        return features

    def feature_update(self, request_object, template_id, feature_id):
        pass

    def feature_statistic(self, storage, search_path):

        this_template = Template.query.filter_by(storage=storage).first()

        Model_ = self.get_storage(this_template)

        endpoint_ = FunctionAPI(db.session, Model_)

        return endpoint_.get()

    def feature_search(self, storage, search_path):

        this_template = Template.query.filter_by(storage=storage).first()

        Model_ = self.get_storage(this_template)

        endpoint_ = API(db.session, Model_)

        return endpoint_._search()

    def feature_delete(self, storage, feature_id):
        
        this_template = Template.query.filter_by(storage=storage).first()

        Storage_ = self.get_storage(this_template)

        feature = Storage_.query.get(feature_id)

        if not hasattr(feature, 'id'):
            return abort(404)

        db.session.delete(feature)
        db.session.commit()

        return True

