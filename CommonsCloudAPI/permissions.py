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

from flask.ext.security import current_user
from flask.ext.security import roles_accepted


"""
Import CommonsCloudAPI Dependencies
"""
from CommonsCloudAPI.extensions import logger
from CommonsCloudAPI.extensions import oauth


"""
Verify that the user has appropriate authorization to access this resource

The code below checks for the following:

  1. Has the user submitted an `access_token` with their request
  2. Is that `access_token` valid or not expired
  2. Is the user account being used `active` or not suspended

If any of these checks should fail, the method should present the user
requesting this endpoint with a `403: Forbidden` response

  @param (object) oauth_request A fully qualified SQLAlchemy `OAuth` object
  @param kwargs See https://docs.python.org/2/glossary.html#term-keyword-argument

  @return (object) user_object A fully qualified SQLAlchemy `User` object

"""
@oauth.require_oauth()
def verify_authorization(oauth_request, **kwargs):

  logger.debug('security.verify_authorization')

  if oauth_request.user:
    if not oauth_request.user.active:
      abort(401)
    return oauth_request.user

  logger.error('403 Forbidden: You have insufficient priveleges or have \
      submitted an invalid or expired `access_token`')

  abort(403)


"""
Verify that the user is part of the group required to access this resource

  @param (object) user_object A fully qualified SQLAlchemy `User` object

  @return (object) grant A fully qualified SQLAlchemy `Grant` object

"""
def verify_group(user_object, requested_account):

  for grant in user_object.group:
    if grant.id == requested_account:
      return grant

  abort(403)


"""
Verify that the user has the appropriate `Role` to access the requested data.

If any of these checks should fail, the method should present the user
requesting this endpoint with a `403: Forbidden` response

  @param user_object (object) A SQLAlchemy `User` object
  @param role_required (array) An array of `Role` strings that the function is requiring

  @return (bool)

"""
def verify_roles(user_object, role_required):

  logger.debug('security.verify_roles')

  if not check_roles(role_required, user_object.roles):
    abort(403)

  return True


"""
Return `bool` based on precense of `role_required` in `role_list`

  @param (string) role_required The `Role` required to access `this` resource 
  @param (list) role_list A list `current_user` `Role`s

  @return (bool)

"""
def check_roles(role_required, role_list):

  logger.debug('security.check_roles')

  for index, role in enumerate(role_list):    
    if role.name in role_required:
      return True

  abort(403)
  
