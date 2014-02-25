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
from collections import namedtuple
from functools import partial
from functools import wraps

"""
Import Flask Dependencies
"""
from flask import current_app

from flask.ext.security import current_user

from flask.ext.principal import identity_loaded, Permission, RoleNeed, UserNeed


"""
Import CommonsCloud Dependencies
"""
from CommonsCloudAPI.extensions import principal
from CommonsCloudAPI.extensions import status as status_


class permission_required(object):

    def __init__(self, permission_type='can_view'):
        self.permission_type = permission_type

    def __call__(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):

          print self.permission_type

          permission = check_permissions(kwargs['application_id'])

          if not permission.get(self.permission_type, True):
            return status_.status_401(), 401
     
          return f(*args, **kwargs)
     
        return decorated_function


"""
Define the most basic Principal need for our Application module
""" 
ApplicationNeed = namedtuple('application', ['method', 'value'])


ViewApplicationNeed = partial(ApplicationNeed, 'view')
class ViewApplicationPermission(Permission):
    def __init__(self, application_id):
        need = ViewApplicationNeed(application_id)
        super(ViewApplicationPermission, self).__init__(need)


EditApplicationNeed = partial(ApplicationNeed, 'edit')
class EditApplicationPermission(Permission):
    def __init__(self, application_id):
        need = EditApplicationNeed(application_id)
        super(EditApplicationPermission, self).__init__(need)


DeleteApplicationNeed = partial(ApplicationNeed, 'delete')
class DeleteApplicationPermission(Permission):
    def __init__(self, application_id):
        need = DeleteApplicationNeed(application_id)
        super(DeleteApplicationPermission, self).__init__(need)


"""
Returns a list of possible permissions for the current application

@param (int) application_id
    The application id that you wish to check against

@return (dict) <unnamed>
    A dictionary of all the possible permissions that a user can have

"""
def check_permissions(application_id):

  return {
    'can_view': ViewApplicationPermission(application_id).can(),
    'can_edit': EditApplicationPermission(application_id).can(),
    'can_delete': DeleteApplicationPermission(application_id).can()
  }

