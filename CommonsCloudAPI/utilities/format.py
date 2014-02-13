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

import uuid

from collections import OrderedDict

from flask import current_app

class FormatContent:

  the_content = ''
  the_filename = ''

  def unique_identifier(self, prefix='', suffix=''):

    unique_base = uuid.uuid4()
    unique_identifier = prefix + str(unique_base).replace('-', '') + suffix

    return unique_identifier

  def serialize_object(self):

    result = OrderedDict()
    for key in self.the_content.__mapper__.c.keys():
        result[key] = getattr(self.the_content, key)
    return result


  def get_directory_name(self):
    directory = current_app.config['FILE_ATTACHMENTS_DIRECTORY']
    return directory


  def get_file_name(self, extension='csv'):

    if not self.the_filename:
      generated_filename = self.unique_identifier()
      self.the_filename = ('%s.%s') % (generated_filename, extension)

    return self.the_filename

