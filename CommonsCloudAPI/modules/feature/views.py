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
from flask import jsonify
from flask import redirect
from flask import request
from flask import url_for


"""
Import Application Dependencies
"""
from CommonsCloudAPI.extensions import oauth
from CommonsCloudAPI.extensions import status as status_

from CommonsCloudAPI.models.feature import Feature
from CommonsCloudAPI.models.statistic import Statistic

from . import module

from .permissions import permission_required


@module.route('/v2/type_<string:storage>.<string:extension>', methods=['OPTIONS'])
def features_preflight(storage, extension):
    return status_.status_200(), 200


@module.route('/v2/type_<string:storage>/<int:feature_id>.<string:extension>', methods=['OPTIONS'])
def features_single_preflight(storage, feature_id, extension):
    return status_.status_200(), 200


@module.route('/v2/type_<string:storage>.<string:extension>', methods=['GET'])
# @oauth.require_oauth()
def feature_list(storage, extension):

    if (extension == 'csv'):
        return status_.status_415('We do not support exporting a feature list as a CSV file yet, but we\'re working on it.'), 415

    Feature_ = Feature()
    feature_list = Feature_.feature_list(storage)
    feature_statistics = Feature_.feature_statistic(storage)

    arguments = {
        'the_content': feature_list.get('objects'),
        'list_name': 'features',
        'extension': extension,
        'current_page': feature_list.get('page'),
        'total_pages': feature_list.get('total_pages'),
        'total_features': feature_list.get('num_results'),
        'features_per_page': feature_list.get('limit'),
        'statistics': feature_statistics
    }

    try:
        return Feature_.endpoint_response(**arguments)
    except Exception as e:
        return status_.status_500(e), 500


# @module.route('/v2/type_<string:storage>/statistics.<string:extension>', methods=['GET'])
# # @oauth.require_oauth()
# def feature_statistic(storage, extension):

#     Feature_ = Feature()
#     feature_statistic = Feature_.feature_statistic(storage, request.args['q'])

#     arguments = {
#         'the_content': feature_statistic,
#         'extension': extension
#     }

#     try:
#         return Feature_.endpoint_response(**arguments)
#     except Exception as e:
#         return status_.status_500(e), 500


@module.route('/v2/type_<string:storage>/<int:feature_id>.<string:extension>', methods=['GET'])
# @oauth.require_oauth()
def feature_get(oauth_request, storage, feature_id, extension):

    if (extension == 'csv'):
        return status_.status_415('We do not support exporting a single item as a CSV file.'), 415

    Feature_ = Feature()
    feature = Feature_.feature_get(storage, feature_id)

    arguments = {
        'the_content': feature,
        "extension": extension,
        'code': 200
    }

    return Feature_.endpoint_response(**arguments)


@module.route('/v2/type_<string:storage>/<int:feature_id>/<string:relationship>.<string:extension>', methods=['GET'])
# @oauth.require_oauth()
def feature_get_relationship(oauth_request, storage, feature_id, relationship, extension):

    Feature_ = Feature()
    feature = Feature_.feature_get_relationship(storage, feature_id, relationship)

    arguments = {
        "the_content": feature,
        "extension": extension,
        "code": 200
    }

    if (extension == 'csv'):
        return status_.status_415("We do not support exporting a single item or it's relationships as a CSV file."), 415

    try:
        return Feature_.endpoint_response(**arguments)
    except Exception as e:
        return status_.status_500(e), 500


@module.route('/v2/type_<string:storage>.<string:extension>', methods=['POST'])
# @oauth.require_oauth()
def feature_create(oauth_request, storage, extension):

    Feature_ = Feature()
    new_feature = Feature_.feature_create(request, storage)

    try:
        arguments = {
          "storage": storage,
          "feature_id": new_feature.id,
          "extension": extension
        }
        return redirect(url_for('.feature_get', **arguments))
    except Exception as e:
        return status_.status_500(e), 500


@module.route('/v2/type_<string:storage>/<int:feature_id>.<string:extension>', methods=['DELETE'])
@oauth.require_oauth()
def feature_delete(oauth_request, storage, feature_id, extension):

    Feature().feature_delete(storage, feature_id)

    try:
        return status_.status_204(), 204
    except Exception as e:
        return status_.status_500(e), 500
