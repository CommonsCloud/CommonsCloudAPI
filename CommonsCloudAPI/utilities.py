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


def process_nested_object(nested_object):

  processed_objects = []

  if not nested_object:
    return processed_objects

  if len(nested_object):
    
    for index, object_ in enumerate(nested_object):
      new_object = {}
      
      for key, value in object_.__dict__.iteritems():
        if key != "_sa_instance_state":
          new_object[key] = value

      processed_objects.append(new_object)

  return processed_objects