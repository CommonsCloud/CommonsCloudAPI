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
Import Python/System Dependencies
"""
import uuid

from collections import OrderedDict


"""
Import Flask Dependencies
"""
from flask import current_app


"""
A Base Class for defining how content should be formatted, this class
allows for some basic cross-document-type functionality that would need
to exist regardless of the type of document we are generating

@variable (list) the_content

@method unique_identifier
@method serialize_object
@method get_directory_name
@method get_file_name

"""
class FormatContent:

  """
  Define our default variables

  @param (object) self
      The object we are acting on behalf of

  @param (object) data
      The actual content we'll be converting

  @param (boolean) serialize
      A flag to identify whether or not the content needs to be serialized
      before it is processed by our formatting tasks
  """
  def __init__(self, data, serialize=False, exclude_fields=[]):
    self.the_content = data
    self.serialize = serialize
    self.exclude_fields = exclude_fields


  """
  This is a helper function to use along side naming items, whether that
  be templates, files, or other items

  @requires
      import uuid

  @todo
    It's possible that we need to create a class that encompasses all utility
    functionality, because we're going to need this same function in the 
    Tempalte Class and possible others.

  @param (object) self
      The object we are acting on behalf of

  @param (string) prefix
      A prefix to add to the string we are generating

  @param (string) suffix
      A suffix to add to the string we are generating

  @return (string) unique_identifier
      A unique string with prefixed and suffixed options if available

  """
  def unique_identifier(self, prefix='', suffix=''):

    unique_base = uuid.uuid4()
    unique_identifier = prefix + str(unique_base).replace('-', '') + suffix

    return unique_identifier


  """
  In order to be able to work with an object it needs to be serialized,
  otherwise we can turn it into any type of file

  @requires
      from collections import OrderedDict

  @param (object) self
      The object we are acting on behalf of

  @return (dict) result
      A dictionary of the contents of our objects

  """
  def serialize_list(self):

      list_ = []

      for object_ in self.the_content:
        result = OrderedDict()
        for key in object_.__mapper__.c.keys():
          if not key in self.exclude_fields:
            result[key] = getattr(object_, key)

        list_.append(result)

      return list_


  """
  In order to be able to work with an object it needs to be serialized,
  otherwise we can turn it into any type of file

  @requires
      from collections import OrderedDict

  @param (object) self
      The object we are acting on behalf of

  @return (dict) result
      A dictionary of the contents of our objects

  """
  def serialize_object(self):

      result = OrderedDict()

      for key in self.the_content.__mapper__.c.keys():
        if not key in self.exclude_fields:
          result[key] = getattr(self.the_content, key)

      return result


  """
  When writing files for the enduser to download we need to make sure
  that we have the directory name where the files belong in the current
  environment we have enabled

  @requires
      from flask import current_app

  @param (object) self
      The object we are acting on behalf of

  @return (string) directory
      A file path that points us to user generated/contributed files
      within the current environment

  """
  def get_directory_name(self):
    directory = current_app.config['FILE_ATTACHMENTS_DIRECTORY']
    return directory

  
  """
  We should try to create a unique name for each file that we create
  on our system, we should prefer to use a system name rather than a
  name that could possibly injected into the class

  @param (object) self
      The object we are acting on behalf of

  @param (string) extension
      An extension to append to the generated file name

  @return (string) filename
      A file name that is unique to this application and has the proper
      extensions for the specific type of file being created

  """
  def get_file_name(self, extension='csv'):

    generated_filename = self.unique_identifier()
    filename = ('%s.%s') % (generated_filename, extension)

    return filename

