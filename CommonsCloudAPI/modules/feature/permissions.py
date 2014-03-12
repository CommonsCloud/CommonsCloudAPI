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
from flask.ext.principal import Permission


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

          permission = check_permissions(kwargs['feature_id'])

          if not permission.get(self.permission_type, True):
            return status_.status_401(), 401
     
          return f(*args, **kwargs)
     
        return decorated_function


"""
Define the most basic Principal need for our Application module
""" 
FeatureNeed = namedtuple('feature', ['method', 'value'])


ViewFeatureNeed = partial(FeatureNeed, 'view')
class ViewFeaturePermission(Permission):
    def __init__(self, feature_id):
        need = ViewFeatureNeed(feature_id)
        super(ViewFeaturePermission, self).__init__(need)


EditFeatureNeed = partial(FeatureNeed, 'edit')
class EditFeaturePermission(Permission):
    def __init__(self, feature_id):
        need = EditFeatureNeed(feature_id)
        super(EditFeaturePermission, self).__init__(need)


DeleteFeatureNeed = partial(FeatureNeed, 'delete')
class DeleteFeaturePermission(Permission):
    def __init__(self, feature_id):
        need = DeleteFeatureNeed(feature_id)
        super(DeleteFeaturePermission, self).__init__(need)


"""
Returns a list of possible permissions for the current feature

@param (int) feature_id
    The feature id that you wish to check against

@return (dict) <unnamed>
    A dictionary of all the possible permissions that a user can have

"""
def check_permissions(feature_id):

  return {
    'can_view': ViewFeaturePermission(feature_id).can(),
    'can_edit': EditFeaturePermission(feature_id).can(),
    'can_delete': DeleteFeaturePermission(feature_id).can()
  }

