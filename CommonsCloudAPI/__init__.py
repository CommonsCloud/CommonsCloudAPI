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
Import System dependencies
"""
import imp
import os
import re
import sys


"""
Import Flask dependencies
"""
from flask import Flask
from flask import redirect
from flask import render_template
from flask import send_from_directory
from flask import url_for

from flask.ext.security import login_required


"""
Import Application Dependencies
"""
from .extensions import db
from .extensions import mail
from .extensions import security

from .models import user_datastore


"""
Setup our base Flask application, retaining it as our application
object for use throughout the application
"""
def create_application(name = __name__, env = 'testing'):
    
    app = Flask(__name__, static_path = '/static')

    # Load our default configuration
    load_configuration(app, env)
    
    # Initialize our database
    db.init_app(app)
        
    # Setup Mail
    mail.init_app(app)
    
    # Setup Flask Security 
    security.init_app(app, user_datastore)
    
    # Load default application routes/paths
    basic_routing(app)

    return app


"""
Load the basic configuration settings for our application from
another file that holds all of our default settings. All Flask
and Flask Extension defaults/configuration handling should be
placed in the this 'settings.py' folder in the application root.
"""
def load_configuration(app, environment):

	environment_configuration = ('config/settings_%s.py') % (environment)

    app.config.from_object(__name__)
    app.config.from_pyfile('config/settings_default.py')
    app.config.from_pyfile(environment_configuration)


"""
Setup some basic routes to get our application started, even if all
we're showing folks is a 404, 500, or the home page.
"""
def basic_routing(app):

  
  """
  The Application Index gives us a route to the "homepage" of our application. Currently
  this takes you to the Application Dashboard, but in the future I sould see the index or
  www.commonscloud.org going to a sales home page and linking to other "sales" pages, versus
  just being associated with the application.
  """
  @app.route('/')
  @login_required
  def application_index():
    return 'CommonsCloudAPI Loaded'


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
  
