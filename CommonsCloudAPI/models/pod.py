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
from flask import abort


"""
Import SnapologyAPI Dependencies
"""
from CommonsCloudAPI.extensions import logger

from CommonsCloudAPI.permissions import verify_authorization
from CommonsCloudAPI.permissions import verify_roles


"""
The BaseSeed is a Class to create all other endpoints within the system
"""
class Pod():

  """
  Preprocessors
  """
  def preprocessor_get_many(**kw):
    authorization = verify_authorization()
    role = verify_roles(authorization, ['admin'])

  def preprocessor_get_single(**kw):
    authorization = verify_authorization()
    role = verify_roles(authorization, ['admin'])

  def preprocessor_put_single(**kw):
    authorization = verify_authorization()
    role = verify_roles(authorization, ['admin'])

  def preprocessor_put_many(**kw):
    authorization = abort(403)

  def preprocessor_patch_single(**kw):
    authorization = verify_authorization()
    role = verify_roles(authorization, ['admin'])

  def preprocessor_patch_many(**kw):
    authorization = abort(403)

  def preprocessor_post(**kw):
    authorization = verify_authorization()
    role = verify_roles(authorization, ['admin'])

  def preprocessor_delete(**kw):
    authorization = verify_authorization()
    role = verify_roles(authorization, ['admin'])


  """
  Postprocessors
  """
  def postprocessor_get_single(**kw):
    logger.debug('postprocessor_get_single')
    pass

  def postprocessor_get_many(**kw):
    logger.debug('postprocessor_get_many')
    pass

  def postprocessor_put_single(**kw):
    logger.debug('postprocessor_put_single')
    pass

  def postprocessor_put_many(**kw):
    logger.debug('postprocessor_put_many')
    pass

  def postprocessor_patch_single(**kw):
    logger.debug('postprocessor_patch_single')
    pass

  def postprocessor_patch_many(**kw):
    logger.debug('postprocessor_patch_many')
    pass

  def postprocessor_post(**kw):
    logger.debug('postprocessor_post')
    pass

  def postprocessor_delete(**kw):
    logger.debug('postprocessor_delete')
    pass


  """
  Flask-Restless Endpoint Arguments

  These arguments define how the Endpoint will be loaded into the system and
  how it will be made available to the user

  @see https://flask-restless.readthedocs.org/en/latest/customizing.html
  """
  __arguments__ = {
    'url_prefix': '/v2.1',
    'exclude_columns': [],
    'methods': [
      'GET',
      'POST',
      'PATCH',
      'PUT',
      'DELETE'
    ],
    'preprocessors': {
      'GET_SINGLE': [preprocessor_get_single],
      'GET_MANY': [preprocessor_get_many],
      'PUT_SINGLE': [preprocessor_put_single],
      'PUT_MANY': [preprocessor_put_many],
      'PATCH_SINGLE': [preprocessor_patch_single],
      'PATCH_MANY': [preprocessor_patch_many],
      'POST': [preprocessor_post],
      'DELETE': [preprocessor_delete]
    },
    'postprocessors': {
      'GET_SINGLE': [postprocessor_get_single],
      'GET_MANY': [postprocessor_get_many],
      'PUT_SINGLE': [postprocessor_put_single],
      'PUT_MANY': [postprocessor_put_many],
      'PATCH_SINGLE': [postprocessor_patch_single],
      'PATCH_MANY': [postprocessor_patch_many],
      'POST': [postprocessor_post],
      'DELETE': [postprocessor_delete]
    },
    'allow_functions': True,
    'allow_patch_many': True
  }


  def __init__(self):
    self.current_user = None
