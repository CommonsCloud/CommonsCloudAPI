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
from flask import request


"""
Import Application Dependencies
"""
from CommonsCloudAPI.extensions import oauth
from CommonsCloudAPI.extensions import status as status_

from CommonsCloudAPI.models.feature import Feature

from . import module

from .permissions import permission_required


@module.route('/v2/features.<string:extension>', methods=['GET'])
# @oauth.require_oauth()
def feature_index(extension):

    return status_.status_303(), 303


@module.route('/v2/features/<string:storage>.<string:extension>', methods=['GET'])
# @oauth.require_oauth()
def feature_list(storage, extension):

    Feature_ = Feature()
    feature_list = Feature_.feature_list(storage)

    arguments = {
        'the_content': feature_list,
        'list_name': 'features',
        "extension": extension,
        'code': 200
    }

    try:
        return Feature_.endpoint_response(**arguments)
    except Exception as e:
        return status_.status_500(e), 500


@module.route('/v2/features/<string:storage>/search.<string:extension>', methods=['GET'])
# @oauth.require_oauth()
def feature_search(storage, extension):

    Feature_ = Feature()
    feature_list = Feature_.feature_search(storage, request.args['q'])

    try:
        return feature_list, 200
    except Exception as e:
        return status_.status_500(e), 500


@module.route('/v2/features/<string:storage>/statistic.<string:extension>', methods=['GET'])
# @oauth.require_oauth()
def feature_statistic(storage, extension):

    Feature_ = Feature()
    feature_list = Feature_.feature_statistic(storage, request.args['q'])

    try:
        return feature_list, 200
    except Exception as e:
        return status_.status_500(e), 500



@module.route('/v2/features/<string:storage>/<int:feature_id>.<string:extension>', methods=['GET'])
# @oauth.require_oauth()
def feature_get(storage, feature_id, extension):

    Feature_ = Feature()
    feature = Feature_.feature_get(storage, feature_id)

    arguments = {
        'the_content': feature,
        "extension": extension,
        'code': 200
    }

    try:
        return Feature_.endpoint_response(**arguments)
    except Exception as e:
        return status_.status_500(e), 500


@module.route('/v2/features/<string:storage>.<string:extension>', methods=['POST'])
# @oauth.require_oauth()
def feature_create(storage, extension):

    Feature_ = Feature()
    new_feature = Feature_.feature_create(request, storage)

    arguments = {
        "the_content": new_feature,
        "extension": extension,
        "code": 201
    }

    try:
        return Feature_.endpoint_response(**arguments)
    except Exception as e:
        return status_.status_500(e), 500



@module.route('/v2/features/<string:storage>/<int:feature_id>.<string:extension>', methods=['DELETE'])
# @oauth.require_oauth()
def feature_delete(storage, feature_id, extension):

    Feature().feature_delete(storage, feature_id)
    
    try:
        return status_.status_204(), 204
    except Exception as e:
        return status_.status_500(e), 500
