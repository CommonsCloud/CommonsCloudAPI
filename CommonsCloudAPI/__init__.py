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
from .extensions import apimanager
from .extensions import babel
from .extensions import db
from .extensions import mail
from .extensions import security
from .extensions import images

from .models import user_datastore


"""
Define necessary modules

Load all of our Flask Blueprints or Modules that we have placed in
the */modules directory of our application. If a folder is named and
has an included __init__.py file, the module will be automatically
loaded when the system is started or restarted.

A list of app modules and their prefixes. Each APP entry must contain a
'name', the remaining arguments are optional. An optional 'models': False
argument can be given to disable loading models for a given module.

"""
MODULES = [
    {'name': 'api', 'url_prefix': '/api'},
    {'name': 'system', 'url_prefix': '/applications'}
]


"""
Setup our base Flask application, retaining it as our application
object for use throughout the application
"""
def create_application(name = __name__, env = 'settings_testing'):
    
    app = Flask(__name__, static_path = '/static')

    # Load our default configuration
    load_configuration(app, env)
    
    # Load Babel for translation
    babel.init_app(app)
    
    # Initialize our database
    db.init_app(app)
        
    # Setup Mail
    mail.init_app(app)

    # Setup Mail
    images.init_app(app)
    
    # Setup API Endpoints
    apimanager.init_app(app)
    
    # Setup Flask Security 
    security.init_app(app, user_datastore)
    
    # Load all of our default modules
    register_local_modules(app)
    
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
    app.config.from_object(__name__)
    app.config.from_pyfile('config/settings_default.py')
    app.config.from_pyfile('config/' + environment + '.py')


"""
Load a specified module into our application
"""
def load_module_models(app, module):
    if 'models' in module and module['models'] == False:
        return

    name = module['name']
    if app.config['DEBUG']:
        print '[MODEL] Loading db model %s' % (name)
    model_name = '%s.models' % (name)
    try:
        mod = __import__(model_name, globals(), locals(), [], -1)
    except ImportError as e:
        if re.match(r'No module named ', e.message) == None:
            print '[MODEL] Unable to load the model for %s: %s' % (model_name, e.message)
        else:
            print '[MODEL] Other(%s): %s' % (model_name, e.message)
        return False
    return True


"""
Automatically load all modules defined in our primary application

All modules should be placed in the commonscloud/modules directory in
order to be properly loaded. Any module not found in the list above and
placed in the commonscloud/modules directory **will not** be loaded into
our application.

"""
def register_local_modules(app):

    cur = os.path.abspath(__file__)
    
    sys.path.append(os.path.dirname(cur) + '/modules')
        
    for m in MODULES:
        mod_name = '%s.views' % m['name']
        try:
            views = __import__(mod_name, globals(), locals(), [], -1)
        except Exception as e:
            load_module_models(app, m)
        else:
            url_prefix = None

            if 'url_prefix' in m:
                url_prefix = m['url_prefix']
                
            if app.config['DEBUG']:
              print '[VIEW ] Mapping views in %s to prefix: %s' % (mod_name, url_prefix)

            # Automatically map '/' to None to prevent modules from
            # stepping on one another.
            if url_prefix == '/':
                url_prefix = None

            load_module_models(app, m)

            app.register_module(views.module, url_prefix=url_prefix)    


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
    return redirect(url_for('applications.index'))


  """
  The Application Attachments gives us a route to access uploads through. By doing things this
  way we can migrate files to whatever server we need to ... perhaps a custom Digital Ocean server,
  an S3 bucket, or some other CDN we decide on later down the road.
  """
  @app.route('/attachment/<path:filename>', methods=['GET'])
  def application_attachment(filename):
      return send_from_directory(app.config['FILE_ATTACHMENTS_DIRECTORY'], filename)

  @app.route('/mu-69d0c0c8-fdd4a7b8-206c72b0-633bea2d', methods=['GET'])
  def application_blitz():
      return '42'


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
  
