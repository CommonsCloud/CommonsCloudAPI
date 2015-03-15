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
from flask import render_template
from flask import request
from flask import url_for

from flask.ext.security import current_user
from flask.ext.security import login_required

from flask.ext.restless import APIManager


"""
Import CommonsCloud Dependencies
"""
from CommonsCloudAPI.extensions import db

from CommonsCloudAPI.models.user import User
from CommonsCloudAPI.models.address import Address
from CommonsCloudAPI.models.organization import Organization
from CommonsCloudAPI.models.role import Role
from CommonsCloudAPI.models.telephone import Telephone
from CommonsCloudAPI.models.territory import Territory


"""
Import Module Dependencies
"""
from . import module


"""
API Endpoints that do not exist by default
"""
@module.route('/v2.1/', methods=['GET'])
def api():
  return jsonify(
    status = '200 OK',
    code = 200,
    message = 'Welcome to the CommonsCloudAPI, to learn more about the api visit https://docs.commonscloud.org/api/v2.1/'
  ), 200


@module.route('/v2.1/user/me', methods=['GET'])
def user_me():
  
  from CommonsCloudAPI.permissions import verify_authorization
  from CommonsCloudAPI.models.user import User
  
  authorization = verify_authorization()

  user_ = User()
  user_object = user_.user_get(authorization.id)

  return jsonify(user_object)


"""
User Account Views/Routes
"""
@module.route('/', methods=['GET'])
def index():
  return redirect('/user/profile/'), 301


@module.route('/user/profile/', methods=['GET'])
@login_required
def user_profile_get():

  user_ = User()
  this_user = user_.user_get(current_user.id)

  return render_template('user/profile.html', user=this_user), 200


@module.route('/user/profile/edit', methods=['GET'])
@login_required
def user_profile_edit():

  user_ = User()
  this_user = user_.user_get(current_user.id)

  return render_template('user/profile-edit.html', user=this_user), 200


@module.route('/user/profile/', methods=['POST'])
@login_required
def user_profile_post():

  user_ = User()
  user_.user_update(request.form)

  return redirect(url_for('user.user_profile_get')), 301


@module.route('/account/create/success/', methods=['GET'])
def account_creation_success():
  return render_template('security/register-success.html'), 200

