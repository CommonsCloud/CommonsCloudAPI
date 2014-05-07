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
Import Python Dependencies
"""
import boto
import json

from datetime import datetime


"""
Import Flask Dependencies
"""
from flask import abort
from flask import request
from flask import current_app

from flask.ext.security import current_user

from geoalchemy2.functions import ST_AsGeoJSON

from flask.ext.restless.views import API
from flask.ext.restless.views import FunctionAPI
from flask.ext.restless.search import search


"""
Import Commons Cloud Dependencies
"""
from CommonsCloudAPI.models.base import CommonsModel

from CommonsCloudAPI.models.template import Template
from CommonsCloudAPI.models.field import Field
from CommonsCloudAPI.models.statistic import Statistic

from CommonsCloudAPI.extensions import db
from CommonsCloudAPI.extensions import logger
from CommonsCloudAPI.extensions import sanitize
from CommonsCloudAPI.extensions import status as status_

from CommonsCloudAPI.utilities.geometry import ST_GeomFromGeoJSON


"""
Define our individual models
"""
class Feature(CommonsModel):

    __public__ = ['id', 'name', 'created', 'status', 'geometry']

    def __init__(self):
        pass

    def feature_create(self, request_object, storage_):

        storage = self.validate_storage(storage_)
        Template_ = Template.query.filter_by(storage=storage).first()
        Storage_ = self.get_storage(Template_)

        """
        Relationships and Attachments
        """
        attachments = self._get_fields_of_type(Template_, 'file')
        relationships = self._get_fields_of_type(Template_, 'relationship')
        print relationships
        print 'Storage_', dir(Storage_), Storage_

        """
        Setup the request object so that we can work with it
        """
        if request_object.data:
          content_ = json.loads(request_object.data)
        elif request_object.form:
          content_ = json.loads(request_object.form['data'])
          print 'content_', content_
        else:
          return abort(400)

        """
        Check for a geometry and if it exists, we need to add a new geometry
        key to the content_ dictionary
        """
        geometry_ = content_.get('geometry', None)
        if geometry_ is not None:
            content_['geometry'] = ST_GeomFromGeoJSON(json.dumps(geometry_))
        
        """
        Set our created and status attributes based on user input or at least
        setup the default
        """
        content_['created'] = content_.get('created', datetime.now())
        content_['status'] = content_.get('status', 'public')
        
        new_content = {}
        
        for field_ in content_:
          if field_ not in relationships and field_ not in attachments:
            new_content[field_] = content_.get(field_, None)
        
        """
        Create the new feature and save it to the database
        """
        new_feature = Storage_(**new_content)
        db.session.add(new_feature)
        db.session.commit()
        
        
        """
        Save relationships and attachments
        """
        for field_ in content_:
          print 'field_', field_
          if field_ in relationships:
        
            assoc_ = self._feature_relationship_associate(Template_, field_)
        
            details = {
              "parent_id": new_feature.id,
              "child_table": field_,
              "content": content_.get(field_, None),
              "assoc_": assoc_
            }
        
            new_feature_relationships = self.feature_relationships(**details)
          elif field_ in attachments:
            s3 = self.get_s3_connection()
            print 'request_object.files', request_object.files
            print dir(s3)
            print s3
            pass

        return new_feature

    def feature_get(self, storage_, feature_id):

        storage = self.validate_storage(storage_)

        this_template = Template.query.filter_by(storage=storage).first()

        Storage_ = self.get_storage(this_template, this_template.fields)

        feature = Storage_.query.get(feature_id)

        if not hasattr(feature, 'id'):
            return abort(404)

        if this_template.is_geospatial and feature.geometry is not None:
          the_geometry = db.session.scalar(ST_AsGeoJSON(feature.geometry))

          feature.geometry = json.loads(the_geometry)

        return feature

    def feature_get_relationship(self, storage_, feature_id, relationship):

        storage = self.validate_storage(storage_)

        this_template = Template.query.filter_by(storage=storage).first()

        Storage_ = self.get_storage(this_template, this_template.fields)

        feature = Storage_.query.get(feature_id)

        if not hasattr(feature, 'id'):
            return abort(404)

        """
        We need to create a generic list of each of the features because we
        cannot display a InstrumentedList via `endpoint_response`
        """
        relationships = []

        for child_feature in getattr(feature, relationship):
          relationships.append(child_feature)

        return relationships

    def feature_update(self, request_object, storage_, feature_id):

      """
      Prepare a dynamic model so we can submit Features to the database
      """
      storage = self.validate_storage(storage_)
      Template_ = Template.query.filter_by(storage=storage).first()
      Storage_ = self.get_storage(Template_)

      feature_ = Storage_.query.get(feature_id)

      logger.warning('Feature to be updated %s', dir(feature_))
      logger.warning('Owner %d', feature_.owner)

      """
      Get a list of File and Relationship fields that belong to our dynamic
      model, but weren't loaded during the model creation above
      """
      attachments = self._get_fields_of_type(Template_, 'file')
      relationships = self._get_fields_of_type(Template_, 'relationship')

      """
      Setup the request object so that we can work with it
      """
      if request_object.data:
        content_ = json.loads(request_object.data)
        logger.warning('JSON Data %s', content_)

      elif request_object.form:
        content_ = json.loads(request_object.form['data'])
        files_ = request_object.files

        logger.warning('Form Content %s', content_)
        logger.warning('Form Files %s', files_)

      """
      Check for a geometry and if it exists, we need to add a new geometry
      key to the content_ dictionary
      """
      geometry_ = content_.get('geometry', None)
      if geometry_ is not None:
        content_['geometry'] = ST_GeomFromGeoJSON(json.dumps(geometry_))
        logger.warning('Geometry %s', content_['geometry'])
      else:
        logger.warning('No geometry was attached')


      """
      Update the content of the Feature.

          1. This first grouping of fields are ones that every Feature has.
          2. The second grouping (loop) are user defined fields that our Model_
             knows about, but ones we cannot hard code.
      """
      if hasattr(feature_, 'status'):
        feature_.status = sanitize.sanitize_string(content_.get('status', feature_.status))

      if hasattr(feature_, 'geometry'):
        feature_.geometry = content_.get('geometry', feature_.geometry)

      #
      # @todo We should be able to transfer the ownership of a feature, but
      #       only if we are the current owner, an admin or a moderator
      #
      # @todo We should also make sure the owner ID exists before allowing them
      #       to save or else we could end up with orphaned Features
      #
      if hasattr(feature_, 'owner'):
        feature_.owner = feature_.owner # content_.get('owner', feature_.owner)

      for field_ in content_:
        if field_ not in relationships and field_ not in attachments:
          if hasattr(feature_, field_):

            # Use the existing value as the default value, if the user has not
            # updated the content of the field
            existing_value = getattr(feature_, field_)
            new_value = content_.get(field_, existing_value)

            setattr(feature_, field_, new_value)

      db.session.commit()


      """
      Save relationships and attachments
      """
      for field_ in content_:
        if field_ in relationships:
      
          assoc_ = self._feature_relationship_associate(Template_, field_)
      
          details = {
            "parent_id": feature_id,
            "child_table": field_,
            "content": content_.get(field_, None),
            "assoc_": assoc_
          }
      
          new_feature_relationships = self.feature_relationships(**details)

      return self.feature_get(storage_, feature_id)

    def feature_statistic(self, storage_):

        search_params = json.loads(request.args.get('q', '{}'))

        storage = self.validate_storage(storage_)

        this_template = Template.query.filter_by(storage=storage).first()

        Model_ = self.get_storage(this_template)

        query = search(db.session, Model_, search_params)

        return self.get_statistics(query.all(), this_template)

    def feature_list(self, storage_):

        storage = self.validate_storage(storage_)

        this_template = Template.query.filter_by(storage=storage).first()

        if not this_template.is_public:
          return abort(403)

        Model_ = self.get_storage(this_template, this_template.fields)

        endpoint_ = API(db.session, Model_)

        results = endpoint_._search()

        # @todo loop over these and make sure we're dropping anything that isn't
        # set to 'public' unless the user has the appropriate permissions

        return endpoint_._search()

    def feature_delete(self, storage_, feature_id):

        storage = self.validate_storage(storage_)

        this_template = Template.query.filter_by(storage=storage).first()

        Storage_ = self.get_storage(this_template)

        feature = Storage_.query.get(feature_id)

        if not hasattr(feature, 'id'):
            return abort(404)

        db.session.delete(feature)
        db.session.commit()

        return True

    def feature_relationships(self, child_table, content, parent_id, assoc_):

      """
      We have to make sure that our dynamically typed Model for the association
      table has been loaded, prior to attempting to save data to it.
      """
      Storage_ = self.get_storage(str(assoc_))

      """
      The only way we can reliably keep lists of relationships is to submit
      all relationships with every update. Because of that, we'd get duplicates
      so we wipe away all of the existing relationships with this parent and
      then re-save all relationships based on user submitted content
      """
      existing_relationships = Storage_.query.filter_by(parent_id=parent_id).all()
      for relationship_ in existing_relationships:
        db.session.delete(relationship_)
        db.session.commit()

      """
      This is a little complicated.

      [if] If the object has an `id` then we simply need to take the parent id
           and the child id, saving them to the association table
      [el] Else we are assuming that the child doesn't exist and we need to
           create it before we save it to the assocation table
      """
      for child_feature in content:
        if 'id' in child_feature:
          relationship_ = Storage_(parent_id=parent_id, child_id=child_feature['id'])
          db.session.add(relationship_)
        else:
          new_feature = self.feature_create(child_feature, child_table)
          db.session.add(new_feature)
          db.session.commit()

          relationship_ = Storage_(parent_id=parent_id, child_id=new_feature.id)
          db.session.add(relationship_)

      """
      Instead of doing commits on each individual relationship add, we're doing
      a single commit at the end so we're only writing to the database once.
      """
      db.session.commit()

    def _feature_relationship_associate(self, template, relationship):
      for field in template.fields:
        if field.relationship == relationship:
          return field.association

    def feature_attachments(self):
      pass

    def _feature_attachment_associate(self):
      pass

    def _feature_attachment_create(self):
      pass

    def _get_fields_of_type(self, template_, type_):

      fields_ = []

      for field in template_.fields:
        if field.data_type == type_:
          if type_ == 'relationship':
            fields_.append(field.relationship)
          else:
            fields_.append(field.name)

      return fields_

    """
    Determine statistics for this query
    """
    def get_statistics(self, query_results, template):

      statistics_list = []

      statistic_field_id_list = self._statistic_field_id_list(template.fields)
      
      statistics = Statistic.query.filter(Statistic.field_id.in_(statistic_field_id_list)).all()
      
      for statistic in statistics:
        
        this_statistic_field = Field.query.get(statistic.field_id)
        this_statistic_value = self.get_statistic_value(statistic, query_results, this_statistic_field)
        
        this_statistic = {
          "name": statistic.name,
          "units": statistic.units,
          "value": this_statistic_value
        }
        
        statistics_list.append(this_statistic)
        
      return statistics_list
        
    """
    Return a single value for a given field
    """
    def get_statistic_value(self, statistic_object, query_results, field):
          
      try:
        if 'SUM' in statistic_object.function:
          return self.get_statistic_value_sum(query_results, field)

      except Exception as e:
        print e
          
    def get_statistic_value_sum(self, query_results, field, product = 0):

      for result in query_results:
        field_value = getattr(result, field.name, '')
        product = product+int(field_value or 0)

      return product

    def _statistic_field_id_list(self, fields):

      ids = []

      for field in fields:
        ids.append(field.id)

      return ids

    def get_s3_connection(self):
      """
      Amazon S3 Connection
      """
      arguments = {
          "aws_access_key_id": current_app.config['AWS_ACCESS_KEY_ID'],
          "aws_secret_access_key": current_app.config['AWS_SECRET_ACCESS_KEY']
      }

      return boto.connect_s3(**arguments)

