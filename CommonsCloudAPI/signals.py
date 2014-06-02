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

from contextlib import contextmanager

from CommonsCloudAPI.extensions import logger
from CommonsCloudAPI.extensions import signals
from CommonsCloudAPI.notifications import execute_notification

"""
Users
"""
trigger_user_created = signals.signal("user-created")
trigger_user_updated = signals.signal("user-updated")
trigger_user_deleted = signals.signal("user-deleted")


"""
Applications
"""
trigger_application_created = signals.signal("application-created")
trigger_application_updated = signals.signal("application-updated")
trigger_application_deleted = signals.signal("application-deleted")


"""
Templates
"""
trigger_template_created = signals.signal("template-created")
trigger_template_updated = signals.signal("template-updated")
trigger_template_deleted = signals.signal("template-deleted")


"""
Fields
"""
trigger_field_created = signals.signal("field-created")
trigger_field_updated = signals.signal("field-updated")
trigger_field_deleted = signals.signal("field-deleted")


"""
Features
"""
trigger_feature_created = signals.signal("feature-created")
trigger_feature_updated = signals.signal("feature-updated")
trigger_feature_deleted = signals.signal("feature-deleted")

def _trigger_feature_created(app, **data):
    logger.warning('SIGNAL: _trigger_feature_created')
    execute_notification('feature-created', app, **data)

def _trigger_feature_updated(app, **data):
    logger.warning('SIGNAL: _trigger_feature_updated')
    # feature_created.append(data)

def _trigger_feature_deleted(app, **data):
    logger.warning('SIGNAL: _trigger_feature_deleted')
    # feature_created.append(data)

trigger_feature_created.connect(_trigger_feature_created)
trigger_feature_updated.connect(_trigger_feature_updated)
trigger_feature_deleted.connect(_trigger_feature_deleted)


"""
Statistics
"""
trigger_statistic_created = signals.signal("statistic-created")
trigger_statistic_updated = signals.signal("statistic-updated")
trigger_statistic_deleted = signals.signal("statistic-deleted")
