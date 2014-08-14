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
import csv
import urllib2


"""
Imports features from a CSV file based on user defined content

@requires
    import csv
    from .forfmat import FormatContent

@param (object) self
    The object we are acting on behalf of

"""
def import_csv(self, filename, storage, template_fields):

  """
  Ensure we have a valid URL, the nominal case is 
  """
  filename = self.validate_url(filename)
  
  """
  List of new features that has been created
  """
  features = []
  headers = []

  """
  Open the CSV from a remote server (AmazonS3)
  """
  response = urllib2.urlopen(filename)
  reader = csv.reader(response)

  """
  Process each row of the CSV and save each row as a separate Feature
  """
  for index, row in enumerate(reader):

    if not index:
      headers = self.process_import_headers(row, template_fields)
      logger.warning('Header: %s', headers)
      continue

    feature_object = {}
    feature_object['data'] = self.build_feature_object(row, headers)

    logger.warning('Request Object: %s', feature_object.data)

    # Feature_ = Feature()
    # new_feature = Feature_.feature_create(feature_object, storage)

    # logger.warning('Index: %s; Feature: %s', index, new_feature)


    # """
    # Create the new Feature within the correct storage table
    # """
    # new_feature = self.feature_create(feature, storage)

    # features.append(feature_object)

  """
  Return a list of newly created Features
  """
  # logger.warning("Imported Features: %s", features)
  # return features

def build_feature_object(self, data, columns):

  feature = {}

  for index, column in enumerate(columns):
    if column.startswith('type_'):
      feature[column] = [
        {
          'id': data[index]
        }
      ]
      continue          
    feature[column] = data[index]

  return feature
  

def process_import_headers(self, headers, template_fields):

  fields = []

  for index, field in enumerate(headers):
    if field.endswith('__id'):
      field_name = field.replace('__id', '')
      relationship_field = self.get_relationship_field(field_name, template_fields)
      logger.warning('Relationship Field Name: %s', relationship_field)
      fields.append(relationship_field)
      continue

    fields.append(field)

  return fields


def get_relationship_field(self, field_name, fields):

  for field in fields:
    if field.name == field_name:
      return field.relationship

"""
Ensures that the URL we're opening is prepended with an appropriate
http:// or https://

@requires
    

@param (string) url
    The URL to check for proper structure

"""
def validate_url(self, url):

    if url.startswith('http://') or url.startswith('https://'):
      return url

    return ('http://%s' % url)




