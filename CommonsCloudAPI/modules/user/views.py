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
from flask.ext.security import login_required

"""
Import CommonsCloudAPI Dependencies
"""
from CommonsCloudAPI.extensions import oauth
from CommonsCloudAPI.extensions import status as status_

from CommonsCloudAPI.models.user import User

from . import module


"""
Basic route for currently logged in user
"""
@module.route('/', methods=['GET'])
def index():
  return redirect(url_for('user.user_profile_get')), 301


@module.route('/v2/user/me.<string:extension>', methods=['GET'])
@oauth.require_oauth('user')
def user_me(oauth_request, extension):

  arguments = {
    'the_content': oauth_request.user,
    'exclude_fields': ['password'],
    'extension': extension
  }

  return User().endpoint_response(**arguments)


@module.route('/v2/users/list.<string:extension>', methods=['GET'])
@oauth.require_oauth('admin')
def user_list(oauth_request, extension):

  User_ = User()
  user_list = User_.user_list()

  arguments = {
    'the_content': user_list,
    'list_name': 'users',
    'extension': extension
  }

  return User_.endpoint_response(**arguments)


@module.route('/user/profile/', methods=['GET'])
@login_required
def user_profile_get():

  user_ = User()
  this_user = user_.user_get(current_user.id)

  picture = user_.user_picture(this_user.email)
  member_since = this_user.confirmed_at.strftime('%b %d, %Y')

  return render_template('user/profile.html', user=this_user, picture=picture, member_since=member_since), 200


# @module.route('/user/remove/', methods=['GET', 'POST'])
# @login_required
# def user_remove():
#   return render_template('user/remove.html', user=current_user), 200


@module.route('/user/profile/', methods=['POST'])
@login_required
def user_profile_post():

  user_ = User()
  user_.user_update(request.form)

  return redirect(url_for('user.user_profile_get')), 301
