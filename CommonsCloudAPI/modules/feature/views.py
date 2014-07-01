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
from CommonsCloudAPI.extensions import logger
from CommonsCloudAPI.extensions import status as status_

from CommonsCloudAPI.models.feature import Feature
from CommonsCloudAPI.models.feature import is_public
from CommonsCloudAPI.models.feature import is_crowdsourced

from . import module


@module.route('/v2/type_<string:storage>.<string:extension>', methods=['OPTIONS'])
def features_preflight(storage, extension):
    return status_.status_200(), 200

@module.route('/v2/type_<string:storage>/<int:feature_id>.<string:extension>', methods=['OPTIONS'])
def features_single_preflight(storage, feature_id, extension):
    return status_.status_200(), 200

@module.route('/v2/type_<string:storage>/<int:feature_id>/<string:relationship>.<string:extension>', methods=['OPTIONS'])
def features_relationship_preflight(storage, feature_id, relationship, extension):
    return status_.status_200(), 200

@module.route('/v2/type_<string:storage>/intersects.<string:extension>', methods=['OPTIONS'])
def features_intersects_preflight(storage, extension):
    return status_.status_200(), 200

@module.route('/v2/type_<string:storage>/region.<string:extension>', methods=['OPTIONS'])
def features_region_preflight(storage, extension):
    return status_.status_200(), 200

@module.route('/v2/type_<string:storage>.<string:extension>', methods=['GET'])
@is_public()
@oauth.oauth_or_public()
def feature_list(oauth_request, storage, extension, is_public):

    if (extension == 'csv'):
        return status_.status_415('We do not support exporting a feature list as a CSV file yet, but we\'re working on it.'), 415
    elif (extension == 'shp'):
        return status_.status_415('We do not support exporting a feature list as a SHP file yet, but we\'re working on it.'), 415

    results_per_page = request.args.get('results_per_page')
    if not results_per_page:
        results_per_page = 25
    elif results_per_page > 100:
        results_per_page = 100
    else:
        results_per_page = int(request.args.get('results_per_page'))



    Feature_ = Feature()
    Feature_.current_user = oauth_request.user
    feature_list = Feature_.feature_list(storage, results_per_page)
    feature_results = feature_list.get('results')
    feature_statistics = Feature_.feature_statistic(feature_list.get('model'),feature_list.get('template'))
    features_last_modified = Feature_.features_last_modified(feature_list.get('model'))

    if type(feature_results) is tuple:
        return feature_results

    arguments = {
        'the_content': feature_results.get('objects'),
        'list_name': 'features',
        'extension': extension,
        'current_page': feature_results.get('page'),
        'total_pages': feature_results.get('total_pages'),
        'total_features': feature_results.get('num_results'),
        'features_per_page': results_per_page,
        'statistics': feature_statistics,
        'last_modified': features_last_modified
    }

    return Feature_.endpoint_response(**arguments)


@module.route('/v2/type_<string:storage>/<int:feature_id>.<string:extension>', methods=['GET'])
@is_public()
@oauth.oauth_or_public()
def feature_get(oauth_request, storage, feature_id, extension, is_public):

    if (extension == 'csv'):
        return status_.status_415('We do not support exporting a single item as a CSV file.'), 415

    Feature_ = Feature()
    Feature_.current_user = oauth_request.user
    feature = Feature_.feature_get(storage, feature_id)

    if type(feature) is tuple:
        return feature

    arguments = {
        'the_content': feature,
        "extension": extension,
        'code': 200
    }

    return Feature_.endpoint_response(**arguments)


@module.route('/v2/type_<string:storage>/<int:feature_id>/<string:relationship>.<string:extension>', methods=['GET'])
@is_public()
@oauth.oauth_or_public()
def feature_get_relationship(oauth_request, storage, feature_id, relationship, extension, is_public):

    Feature_ = Feature()
    Feature_.current_user = oauth_request.user
    feature = Feature_.feature_get_relationship(storage, feature_id, relationship)

    if type(feature) is tuple:
        return feature

    arguments = {
        "the_content": feature,
        "list_name": "features",
        "extension": extension,
        "code": 200
    }

    if (extension == 'csv'):
        return status_.status_415("We do not support exporting a single item or it's relationships as a CSV file."), 415

    return Feature_.endpoint_response(**arguments)


@module.route('/v2/type_<string:storage>.<string:extension>', methods=['POST'])
@is_crowdsourced()
@oauth.oauth_or_crowdsourced()
def feature_create(oauth_request, storage, extension, is_crowdsourced):

    Feature_ = Feature()
    Feature_.current_user = oauth_request.user
    new_feature = Feature_.feature_create(request, storage)

    if type(new_feature) is tuple:
        return new_feature

    try:
        return status_.status_201(new_feature.id), 201
    except Exception as e:
        return status_.status_500(e), 500


@module.route('/v2/type_<string:storage>/<int:feature_id>.<string:extension>', methods=['PATCH','PUT'])
@oauth.require_oauth()
def feature_update(oauth_request, storage, feature_id, extension):

    Feature_ = Feature()
    Feature_.current_user = oauth_request.user
    updated_feature = Feature_.feature_update(request, storage, feature_id)

    if type(updated_feature) is tuple:
        return updated_feature

    arguments = {
      "the_content": updated_feature,
      "extension": extension
    }

    try:
        return Feature_.endpoint_response(**arguments)
    except Exception as e:
        return status_.status_500(e), 500


@module.route('/v2/type_<string:storage>/<int:feature_id>.<string:extension>', methods=['DELETE'])
@oauth.require_oauth()
def feature_delete(oauth_request, storage, feature_id, extension):

    Feature_ = Feature()
    Feature_.current_user = oauth_request.user
    Feature_.feature_delete(storage, feature_id)

    try:
        return status_.status_204(), 204
    except Exception as e:
        return status_.status_500(e), 500

@module.route('/v2/type_<string:storage>/intersects.<string:extension>', methods=['GET'])
@is_public()
@oauth.oauth_or_public()
def feature_intersects(oauth_request, storage, extension, is_public):

    geometry = request.args.get('geometry')
    results_per_page = request.args.get('results_per_page')

    Feature_ = Feature()
    Feature_.current_user = oauth_request.user
    feature_list = Feature_.feature_get_intersection(storage, geometry)

    if type(feature_list) is tuple:
        return feature_list

    arguments = {
        'the_content': feature_list,
        'list_name': 'features',
        'extension': extension
    }

    return Feature_.endpoint_response(**arguments)

@module.route('/v2/type_<string:storage>/region.<string:extension>', methods=['GET'])
@is_public()
@oauth.oauth_or_public()
def feature_region(oauth_request, storage, extension, is_public):

    geometry = request.args.get('geometry')
    results_per_page = request.args.get('results_per_page')

    Feature_ = Feature()
    Feature_.current_user = oauth_request.user
    feature_list = Feature_.feature_get_content_for_region(storage, geometry)

    if type(feature_list) is tuple:
        return feature_list

    arguments = {
        'the_content': feature_list,
        'list_name': 'features',
        'extension': extension
    }

    return Feature_.endpoint_response(**arguments)
