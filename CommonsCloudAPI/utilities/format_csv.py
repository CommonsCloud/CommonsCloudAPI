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

import csv

from .format import FormatContent

from flask import send_from_directory

class CSV(FormatContent):

  def create_csv(self):

    this_directory = self.get_directory_name()
    this_filename  = self.get_file_name()
    this_filepath  = ('%s%s%s') % (this_directory, '/', this_filename)
    this_content   = self.serialize_object()

    """
    Create the CSV header
    """
    with open(this_filepath, 'wb') as open_file:

      headers = []

      for column in this_content:
        headers.append(column)

      dict_writer = csv.DictWriter(open_file, headers, lineterminator="\r\n", delimiter=",", doublequote=False, quoting=csv.QUOTE_NONNUMERIC, quotechar="'")
      dict_writer.writeheader()

      """
      Create the CSV Content
      """
      dict_writer.writerows([this_content])

      open_file.close()

    return send_from_directory(this_directory, this_filename, as_attachment=True)





