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
from flask import render_template

from flask.ext.security import current_user
from flask.ext.security import login_required


"""
Import Module Dependencies
"""
from . import module


"""
The front page of the application for authenticated Unless
"""
@module.route('/')
@login_required
def index():
  return render_template('dashboard/index.html', user=current_user), 200


@module.route('/mapbox')
def mapbox():
	return render_template('mapbox.html'), 200