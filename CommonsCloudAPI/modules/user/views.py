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
from flask import render_template
from flask import request
from flask import url_for

from flask.ext.security import current_user

"""
Import CommonsCloudAPI Dependencies
"""
from CommonsCloudAPI.models.user import User

from . import module


"""
Basic route for currently logged in user
"""
@module.route('/', methods=['GET'])
def index():
  return redirect(url_for('user.user_profile_get'))


@module.route('/user/me/', methods=['GET'])
def user_me():

  if not current_user.is_authenticated():
    return redirect('/login')

  arguments = {
    'the_content': current_user,
    'exclude_fields': ['password']

  }

  return User().endpoint_response(**arguments)


@module.route('/user/profile/', methods=['GET'])
def user_profile_get():

  if not current_user.is_authenticated():
    return redirect('/login')

  user_ = User()
  this_user = user_.user_get(current_user.id)
  return render_template('user/profile.html', user=this_user), 200


@module.route('/user/profile/', methods=['POST'])
def user_profile_post():

  if not current_user.is_authenticated():
    return redirect('/login')

  user_ = User()
  user_.user_update(request.form)

  return redirect(url_for('user.user_profile_get'))

