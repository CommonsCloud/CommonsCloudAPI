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
Import System Dependencies
"""
import imp
import os
import flask.ext.restless
import json


"""
Import Flask dependencies
"""
from flask import Flask
from flask import jsonify


"""
Import Application Dependencies
"""
from .errors import load_errorhandlers

from .extensions import db
from .extensions import mail
from .extensions import security
from .extensions import oauth
from .extensions import rq


"""
Setup our base Flask application, retaining it as our application
object for use throughout the application
"""
def create_application(name=__name__, env='testing'):
    
    app = Flask(__name__, **{
        'static_path': '/static',
        'template_folder': 'static/templates'
    })

    # Load our default configuration
    load_configuration(app, env)
            
    # Setup Mail
    mail.init_app(app)
    
    # Setup OAuth2 Provider
    oauth.init_app(app)

    # Load our application's blueprints
    load_modules(app, db)

    
    """
    Initialize our database and create tables
    """
    db.init_app(app)
    db.app = app
    db.create_all()


    """
    Setup Flask Security 
    
    We cannot load the security information until after our blueprints
    have been loaded into our application.
    """
    from CommonsCloudAPI.models.user import User
    from CommonsCloudAPI.models.role import Role

    from flask.ext.security import SQLAlchemyUserDatastore

    """
    Hook the User model and the Role model up to the User Datastore provided
    by SQLAlchemy's Engine's datastore that provides Flask-Security with
    User/Role information so we can lock down access to the system and it's
    resources.
    """
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)

    security.init_app(app, user_datastore)


    """
    Load default application routes/paths
    """
    load_errorhandlers(app)

    def add_cors_header(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Authorization, Accept, Content-Type, X-Requested-With, Origin, Access-Control-Request-Method, Access-Control-Request-Headers, Cache-Control, Expires, Set-Cookie'
        response.headers['Access-Control-Allow-Credentials'] = True
        return response

    app.after_request(add_cors_header)

    return app


"""
Load the basic configuration settings for our application from
another file that holds all of our default settings. All Flask
and Flask Extension defaults/configuration handling should be
placed in the this 'settings.py' folder in the application root.
"""
def load_configuration(app, environment):

  """
  Create the file path based on the selected environment
  """
  environment_configuration = ('config/settings_%s.py') % (environment)

  app.config.from_object(__name__)
  app.config.from_pyfile('config/settings_default.py')
  app.config.from_pyfile(environment_configuration)


"""
Load all of our application's endpoints
"""
def load_endpoints(app, db, path):

  """
  Load dynamic endpoints
  """
  manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)

  endpoints = os.listdir(path)
  
  for endpoint in endpoints:

    if os.path.isdir(os.path.join(path, endpoint)) and os.path.exists(os.path.join(path, endpoint, '__init__.py')):

      f, filename, descr = imp.find_module(endpoint, [path])

      Packet = imp.load_module(endpoint, f, filename, descr)

      if hasattr(Packet, 'Model'):
        Seed_ = Packet.Seed()
        manager.create_api(Packet.Model, **Seed_.__arguments__)


"""
Load all of our application's modules
"""
def load_modules(app, db):

    """
    Load dynamic endpoints
    """
    manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)

    """
    Check the `modules` directory to see if we need to load any modules
    for our application to operate properly.
    """
    path = 'CommonsCloudAPI/modules'
    module_list = os.listdir(path)
    modules = {}
    
    """
    Iterate over the list of modules from in the `modules` directory
    """
    for module in module_list:

        """
        Before loading our modules, we need to make sure if there's a directory
        that exists, this will help us weed out broken modules
        """
        if os.path.isdir(os.path.join(path, module)) and \
            os.path.exists(os.path.join(path, module, '__init__.py')):
            
            """
            Check to see if this `module` has any API endpoints that need to be
            created dynamically. If so, we should go ahead and load those now
            so that they are loaded with the application
            """
            api_path = os.path.join(path, module, 'endpoints')

            if os.path.isdir(api_path):
              load_endpoints(app, db, api_path)

            f, filename, descr = imp.find_module(module, [path])
            
            modules[module] = imp.load_module(module, f, filename, descr)

            
            """
            Register the current module as an official `Module` within
            Flask so that we can load views and other Flask specific
            items within the `app`
            """
            app.register_blueprint(getattr(modules[module], 'module'))

