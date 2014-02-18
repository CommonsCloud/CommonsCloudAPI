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
Load all of our application's blueprints
"""
def load_blueprints(app):

    path = 'CommonsCloudAPI/modules'
    dir_list = os.listdir(path)
    mods = {}
    
    for fname in dir_list:
        if os.path.isdir(os.path.join(path, fname)) and os.path.exists(os.path.join(path, fname, '__init__.py')):
            f, filename, descr = imp.find_module(fname, [path])
            mods[fname] = imp.load_module(fname, f, filename, descr)
            app.register_blueprint(getattr(mods[fname], 'module'))
        elif os.path.isfile(os.path.join(path, fname)):
            name, ext = os.path.splitext(fname)
            if ext == '.py' and not name == '__init__':
                f, filename, descr = imp.find_module(name, [path])
                mods[fname] = imp.load_module(name, f, filename, descr)
                app.register_blueprint(getattr(mods[fname], 'module'))

