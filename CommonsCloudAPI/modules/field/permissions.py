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

          print self.permission_type

          permission = check_permissions(kwargs['template_id'])

          if not permission.get(self.permission_type, True):
            return status_.status_401(), 401
     
          return f(*args, **kwargs)
     
        return decorated_function


"""
Define the most basic Principal need for our Application module
""" 
FieldNeed = namedtuple('field', ['method', 'value'])


ViewFieldNeed = partial(FieldNeed, 'view')
class ViewFieldPermission(Permission):
    def __init__(self, field_id):
        need = ViewFieldNeed(field_id)
        super(ViewFieldPermission, self).__init__(need)


EditFieldNeed = partial(FieldNeed, 'edit')
class EditFieldPermission(Permission):
    def __init__(self, field_id):
        need = EditFieldNeed(field_id)
        super(EditFieldPermission, self).__init__(need)


DeleteTemplateNeed = partial(FieldNeed, 'delete')
class DeleteTemplatePermission(Permission):
    def __init__(self, field_id):
        need = DeleteFieldNeed(field_id)
        super(DeleteFieldPermission, self).__init__(need)


"""
Returns a list of possible permissions for the current template

@param (int) field_id
    The field id that you wish to check against

@return (dict) <unnamed>
    A dictionary of all the possible permissions that a user can have

"""
def check_permissions(field_id):

  return {
    'can_view': ViewFieldPermission(field_id).can(),
    'can_edit': EditFieldPermission(field_id).can(),
    'can_delete': DeleteTemplatePermission(field_id).can()
  }

