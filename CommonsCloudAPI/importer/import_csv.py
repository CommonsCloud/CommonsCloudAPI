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
import json
import urllib2

from CommonsCloudAPI.models.activity import Activity
from CommonsCloudAPI.models.template import Template


"""
Imports features from a CSV file based on user defined content

@requires
    import csv
    from .forfmat import FormatContent

@param (object) self
    The object we are acting on behalf of

"""
def import_csv(filename, storage, template_fields, activity_id):

  """
  Ensure we have a valid URL, the nominal case is 
  """
  filename_ = validate_url(filename)
  
  """
  List of new features that has been created
  """
  features = []
  headers = []

  print filename_

  """
  Open the CSV from a remote server (AmazonS3)
  """
  try:
    response = urllib2.urlopen(filename_)
    reader = csv.reader(response)
  except urllib2.HTTPError as error:
      reader = error.read()

  post_url = ('http://api.commonscloud.org/v2/type_%s.json') % (storage)

  """
  Process each row of the CSV and save each row as a separate Feature
  """
  for index, row in enumerate(reader):

    if not index:
      headers = process_import_headers(row, template_fields)
      continue

    feature_object = build_feature_object(row, headers)

    req = urllib2.Request(post_url)
    req.add_header('Content-Type', 'application/json')

    response = urllib2.urlopen(req, json.dumps(feature_object), 300)


# def import_csv(filename, storage, template_fields, activity_id):

#   """
#   Ensure we have a valid URL, the nominal case is 
#   """
#   filename_ = validate_url(filename)
  
#   """
#   List of new features that has been created
#   """
#   features = []
#   headers = []

#   print filename_

#   """
#   Open the CSV from a remote server (AmazonS3)
#   """
#   try:
#     response = urllib2.urlopen(filename_)
#     reader = csv.reader(response)
#   except urllib2.HTTPError as error:
#       reader = error.read()

#   """
#   Process each row of the CSV and save each row as a separate Feature
#   """
#   for index, row in enumerate(reader):

#     if not index:
#       headers = process_import_headers(row, template_fields)
#       continue

#     feature_object = build_feature_object(row, headers)

#     features.append(feature_object)

#   """
#   Send list of Features to our batch import function
#   """
#   batch_url = ('http://api.commonscloud.org/v2/type_%s/batch.json') % (storage)
#   data = {
#     'features': features,
#     'activity_id': activity_id
#   }
#   content_length = len(data)
#   timeout = 3600

#   req = urllib2.Request(batch_url)
#   req.add_header('Content-Type', 'application/json')
#   # req.add_header('Content-Length', content_length)

#   response = urllib2.urlopen(req, json.dumps(data), timeout)


#   """
#   Return a list of newly created Features
#   """
#   return response

def build_feature_object(data, columns):

  feature = {}

  for index, column in enumerate(columns):
    if column.startswith('type_'):
      feature[column] = [
        {
          'id': data[index]
        }
      ]
    elif data[index] is None or data[index] == '':
      feature[column] = None
    else:
      feature[column] = data[index]

  return feature
  

def process_import_headers(headers, template_fields):

  fields = []

  for index, field in enumerate(headers):
    if field.endswith('__id'):
      field_name = field.replace('__id', '')
      relationship_field = get_relationship_field(field_name, template_fields)
      fields.append(relationship_field)
      continue

    fields.append(field)

  return fields


def get_relationship_field(field_name, fields):

  for field in fields:
    if field.get('name') == field_name:
      return field.get('relationship')

"""
Ensures that the URL we're opening is prepended with an appropriate
http:// or https://

@requires
    

@param (string) url
    The URL to check for proper structure

"""
def validate_url(url):

    if url.startswith('http://') or url.startswith('https://'):
      return url

    return ('http://%s' % url)




