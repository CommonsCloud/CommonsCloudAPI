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
Import Flask Dependencies
"""
from flask import redirect
from flask import request
from flask import url_for

from flask.ext.security import current_user


"""
Import Application Dependencies
"""
from CommonsCloudAPI.extensions import oauth
from CommonsCloudAPI.extensions import status as status_

from CommonsCloudAPI.utilities.format_csv import CSV
from CommonsCloudAPI.utilities.format_json import JSON


"""
Import Module Dependencies
"""
from . import module

from CommonsCloudAPI.models.feature import Feature

from .permissions import permission_required


@module.route('/feature/', methods=['GET'])
# @oauth.require_oauth()
def feature_index():

    return status_.status_303(), 303


"""
CREATE

Everyone that has a user account can add new features, and any templates that
are considered to be `is_public` anyone can add features to.
"""
@module.route('/feature/<string:storage>/', methods=['POST'])
# @oauth.require_oauth()
def feature_create(storage):

    try:
        Feature_ = Feature()
        new_feature = Feature_.feature_create(request, storage)
    except Exception as e:
        return status_.status_500(e), 500

    return Feature_.endpoint_response(new_feature, code=201)
