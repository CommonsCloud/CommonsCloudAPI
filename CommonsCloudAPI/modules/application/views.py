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


from CommonsCloudAPI.extensions import status


"""
Import Application Module Dependencies
"""
from . import module

from .models import Application
from .permissions import check_permissions


@module.route('/application/', methods=['GET'])
@login_required
def application_list():

  Application_ = Application()
  applications = Application_.application_list()

  return render_template('application/list.html', applications=applications), 200


@module.route('/application/<int:application_id>/', methods=['GET'])
@login_required
def application_get(application_id):

  permission = check_permissions(application_id)

  if not permission.get('can_view', True):
    return status.status_401(), 401

  Application_ = Application()
  this_application = Application_.application_get(application_id)

  return render_template('application/single.html', application=this_application, permissions=permission), 200


@module.route('/application/new/', methods=['GET'])
@login_required
def application_create():
  return render_template('application/new.html'), 200


@module.route('/application/new/', methods=['POST'])
@login_required
def application_post():

  if not current_user.is_authenticated():
    return status_.status_401(), 401

  Application_ = Application()
  new_application = Application_.application_create(request.form)

  print new_application.id

  return redirect(url_for('application.application_get', application_id=new_application.id))

