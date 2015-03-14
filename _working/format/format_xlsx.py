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
import xlsxwriter


"""
Import Flask Dependencies
"""
from flask import send_from_directory


"""
Import CommonsCloudAPI Dependencies
"""
from . import FormatContent


"""
A class for formatting objects as comma separated value documents or CSV

@requires ForamtContent

@method create

"""
class XLSX(FormatContent):

  """
  Creates a CSV file based on user requested content

  @requires
      import csv
      from .format import FormatContent

  @see send_from_directory
      http://flask.pocoo.org/docs/api/#flask.send_from_directory

  @param (object) self
      The object we are acting on behalf of

  @return (method) send_from_directory
      The final file that was create and sent to the user as an attachment,
      for more information on this function see the official Flask documentation
      here http://flask.pocoo.org/docs/api/#flask.send_from_directory

  """
  def create(self):
    pass

    # """
    # The following variables help us define what, where, and how things will be saved
    # as we walk through the CSV creation process
    # """
    # this_directory = self.get_directory_name()
    # this_filename  = self.get_file_name()
    # this_filepath  = ('%s%s%s') % (this_directory, '/', this_filename)
    # workbook = xlsxwriter.Workbook(this_filepath)

    # """
    # Add our base Worksheet that will serve as our template
    # """
    # storage_worksheet = workbook.add_worksheet('Sheet 1')

    # """
    # With the current file open, begin writing our content
    # """
    # with open(this_filepath, 'wb') as open_file:

      
      # storage_worksheet.write(0, index, field.name)

      # # """
      # # Create the header row for our CSV
      # # """
      # # for index, column in enumerate(self.the_content['features'][0]):
      # #   storage_worksheet.write(0, index, field.name)

  def createHeaders(self, object_):

    headers = []

    for item in object_:
      headers.append(item)

    return headers