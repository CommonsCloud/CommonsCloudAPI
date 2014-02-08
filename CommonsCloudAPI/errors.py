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
Import Flask dependencies
"""
from flask import render_template


"""
Setup some basic routes to get our application started, even if all
we're showing folks is a 404, 500, or the home page.
"""
def load_errorhandlers(app):

  """
  If a user would happen to arrive at a deadend within the system, we should at least give
  them a little feedback. These should get better over time, but for now we can at least make
  it look like they aren't completely leaving the system and lost with default server error pages.
  """
  @app.errorhandler(404)
  def internal_error(error):
    return render_template('system/error_404.html'), 404
  
  @app.errorhandler(500)
  def internal_error(error):
      return render_template('system/error_500.html'), 500
  
