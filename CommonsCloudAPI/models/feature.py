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
import ast
import boto
import json
import os.path
import uuid

from datetime import datetime
from uuid import uuid4

from functools import wraps

"""
Import Flask Dependencies
"""
from werkzeug import secure_filename

from flask import abort
from flask import request
from flask import current_app

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
from CommonsCloudAPI.extensions import oauth
from CommonsCloudAPI.extensions import sanitize
from CommonsCloudAPI.extensions import status as status_

from CommonsCloudAPI.utilities.geometry import ST_GeomFromGeoJSON

from CommonsCloudAPI.signals import trigger_feature_created

from geoalchemy2.elements import WKBElement
import geoalchemy2.functions as func


"""
is_public allows us to check if feature collections are supposed to public, if
they are, then we don't need to check for OAuth crednetials to allow access
"""
class is_public(object):

    def __init__(self):
      pass

    def __call__(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):

          storage = self.validate_storage(kwargs['storage'])

          this_template = Template.query.filter_by(storage=storage).first()

          keywords = kwargs

          if not this_template.is_public:
            keywords['is_public'] = False
          else:
            keywords['is_public'] = True

          return f(*args, **keywords)
     
        return decorated_function

    """
    Storage name
    """
    def validate_storage(self, storage_name):

      if not storage_name.startswith('type_'):
        storage_name = str('type_' + storage_name)

      return storage_name

class is_crowdsourced(object):

    def __init__(self):
      pass

    def __call__(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):

          storage = self.validate_storage(kwargs['storage'])

          this_template = Template.query.filter_by(storage=storage).first()

          keywords = kwargs

          if not this_template.is_crowdsourced:
            keywords['is_crowdsourced'] = False
          else:
            keywords['is_crowdsourced'] = True

          return f(*args, **keywords)
     
        return decorated_function

    """
    Storage name
    """
    def validate_storage(self, storage_name):

      if not storage_name.startswith('type_'):
        storage_name = str('type_' + storage_name)

      return storage_name


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
        logger.warning("attachments %s", attachments)

        relationships = self._get_fields_of_type(Template_, 'relationship')
        logger.warning("relationships %s", relationships)

        """
        Setup the request object so that we can work with it
        """
        try:
          content_ = json.loads(request_object.data)
          logger.warning("request_object.data %s", dir(request_object.data))
        except ValueError, e:
          content_ = request_object.form
          logger.warning("request_object.form %s", request_object.form)

        new_content = {}
        
        for field_ in content_.keys():
          if field_ == 'geometry':
            logger.warning('Processing Field (geometry) %s', field_)
            geometry_ = content_.get('geometry', None)
            if geometry_ is not None:
                new_content['geometry'] = ST_GeomFromGeoJSON(json.dumps(geometry_))
          elif field_ == 'created':
            logger.warning('Processing Field (created) %s', field_)
            new_content['created'] = content_.get('created', datetime.now())
          elif field_ == 'status':
            logger.warning('Processing Field (status) %s', field_)
            new_content['status'] = content_.get('status', 'public')
          elif field_ not in relationships and field_ not in attachments:
            logger.warning('Processing Field (other) %s', field_)
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
          if field_ in relationships:
            assoc_ = self._feature_relationship_associate(Template_, field_)

            logger.warning('%s %s', field_, type(content_.get(field_, None)))

            if type(content_.get(field_, None)) is not list:
              logger.warning('We need to do something else with this value %s', type(content_.get(field_, None)))
              list_of_relationships = json.loads(content_.get(field_, None))
              logger.warning('We updated it to %s', type(list_of_relationships))
            else:
              list_of_relationships = content_.get(field_, None)

            # @todo
            #
            # Check to see if the values being passed are a list or a dictionary
            #

            details = {
              "parent_id": new_feature.id,
              "child_table": field_,
              "content": list_of_relationships,
              "assoc_": assoc_
            }
        
            new_feature_relationships = self.feature_relationships(**details)


        """
        Saving attachments
        """
        for attachment in attachments:

          assoc_ = self._feature_relationship_associate(Template_, attachment)
          Attachment_ = self.get_storage(str(attachment))

          field_attachments = request_object.files.getlist(attachment)

          for file_ in field_attachments:
        
            if file_ and self.allowed_file(file_.filename):

              output = self.s3_upload(file_)

              # There's two steps to get a file related to the feature.
              #
              # Step 1: Create a record in the attachment_ so that we have
              #         an ID for our attachment
              #              
              attachment_details = {
                'caption': sanitize.sanitize_string(''),
                'credit': sanitize.sanitize_string(''),
                'credit_link': sanitize.sanitize_string(''),
                'filename': sanitize.sanitize_string(file_.filename),
                'filepath': output,
                'filetype': sanitize.sanitize_string(file_.mimetype),
                'filesize': file_.content_length,
                'created': datetime.now(),
                'status': 'public',
              }
              
              new_attachment = Attachment_(**attachment_details)
              db.session.add(new_attachment)
              db.session.commit()

              #
              # Step 2: Take that Attachment ID and pass it along in the
              #         `details` dictionary
              details = {
                "parent_id": new_feature.id,
                "child_table": attachment,
                "content": new_attachment.id,
                "assoc_": assoc_
              }

              #
              # Step 3: Finally, we create the relationship between the new
              #         attachment and the new feature
              #
              new_feature_attachments = self.feature_attachments(**details)

        feature_json = self.feature_get(storage, new_feature.id)
        trigger_feature_created.send(current_app._get_current_object(),
                             storage=storage, template=Template_, feature=new_feature, feature_json=feature_json)
        logger.info('A new feature was created in %s with an id of %d', 
            storage, new_feature.id)

        return new_feature

    def feature_get(self, storage_, feature_id):

        storage = self.validate_storage(storage_)

        this_template = Template.query.filter_by(storage=storage).first()

        Storage_ = self.get_storage(this_template, this_template.fields)

        feature = Storage_.query.get(feature_id)

        if not hasattr(feature, 'id'):
            return abort(404)

        # if this_template.is_geospatial and feature.geometry is not None:
        #   the_geometry = db.session.scalar(ST_AsGeoJSON(feature.geometry))

        #   feature.geometry = json.loads(the_geometry)

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

      logger.warning('Feature to be saved: %s', feature_)

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

      """
      Saving attachments
      """
      for attachment in attachments:

        assoc_ = self._feature_relationship_associate(Template_, attachment)
        Attachment_ = self.get_storage(str(attachment))

        field_attachments = request_object.files.getlist(attachment)

        for file_ in field_attachments:
      
          if file_ and self.allowed_file(file_.filename):

            output = self.s3_upload(file_)

            # There's two steps to get a file related to the feature.
            #
            # Step 1: Create a record in the attachment_ so that we have
            #         an ID for our attachment
            #              
            attachment_details = {
              'caption': sanitize.sanitize_string(''),
              'credit': sanitize.sanitize_string(''),
              'credit_link': sanitize.sanitize_string(''),
              'filename': sanitize.sanitize_string(file_.filename),
              'filepath': output,
              'filetype': sanitize.sanitize_string(file_.mimetype),
              'filesize': file_.content_length,
              'created': datetime.now(),
              'status': 'public',
            }
            
            new_attachment = Attachment_(**attachment_details)
            db.session.add(new_attachment)
            db.session.commit()

            #
            # Step 2: Take that Attachment ID and pass it along in the
            #         `details` dictionary
            details = {
              "parent_id": feature_id,
              "child_table": attachment,
              "content": new_attachment.id,
              "assoc_": assoc_
            }

            #
            # Step 3: Finally, we create the relationship between the new
            #         attachment and the new feature
            #
            new_feature_attachments = self.feature_attachments(**details)

      return self.feature_get(storage_, feature_id)

    def feature_statistic(self, storage_):

        search_params = json.loads(request.args.get('q', '{}'))

        storage = self.validate_storage(storage_)

        this_template = Template.query.filter_by(storage=storage).first()

        Model_ = self.get_storage(this_template)

        query = search(db.session, Model_, search_params)

        return self.get_statistics(query.all(), this_template)

    def feature_list(self, storage_, results_per_page=25):

        storage = self.validate_storage(storage_)

        this_template = Template.query.filter_by(storage=storage).first()

        Model_ = self.get_storage(this_template, this_template.fields)

        endpoint_ = API(db.session, Model_, results_per_page=results_per_page)

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

    def feature_get_intersection(self, storage_, geometry):

        storage = self.validate_storage(storage_)

        this_template = Template.query.filter_by(storage=storage).first()

        Storage_ = self.get_storage(this_template)

        # features = Storage_.query(func.ST_Intersects(geometry, 4)).all()

        point = str('SRID=4326;POINT(%s)' % geometry)

        features = db.session.execute(db.select([Storage_]).select_from(Storage_).where(func.ST_Intersects(point, Storage_.geometry))).fetchall()

        return features

    def feature_attachments(self, child_table, content, parent_id, assoc_):
      """
      We have to make sure that our dynamically typed Model for the association
      table has been loaded, prior to attempting to save data to it.
      """
      Storage_ = self.get_storage(str(assoc_))

      relationship_ = Storage_(parent_id=parent_id, child_id=content)
      db.session.add(relationship_)

      db.session.commit()

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
      logger.warning('content %s', type(content))

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

    def _get_fields_of_type(self, template_, type_):

      fields_ = []

      for field in template_.fields:
        if field.data_type == type_:
          if type_ == 'relationship' or type_ == 'file':
            fields_.append(field.relationship)

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
        logger.warning(e)
          
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

    """
    Check the file name's extension to ensure it is in our safe list
    """
    def allowed_file(self, filename):
      return '.' in filename and \
        filename.rsplit('.', 1)[1] in ['png', 'jpg']


    """
    Upload files directly to S3
    """
    def s3_upload(self, source_file, acl='public-read'):
        ''' Uploads WTForm File Object to Amazon S3

            Expects following current_app.config attributes to be set:
                S3_KEY              :   S3 API Key
                S3_SECRET           :   S3 Secret Key
                S3_BUCKET           :   What bucket to upload to
                S3_UPLOAD_DIRECTORY :   Which S3 Directory.

            The default sets the access rights on the uploaded file to
            public-read.  It also generates a unique filename via
            the uuid4 function combined with the file extension from
            the source file.
        '''

        source_filename = secure_filename(source_file.filename)
        source_extension = os.path.splitext(source_filename)[1]

        destination_filename = uuid4().hex + source_extension

        # Connect to S3 and upload file.
        conn = boto.connect_s3(current_app.config["S3_KEY"], current_app.config["S3_SECRET"])
        b = conn.get_bucket(current_app.config["S3_BUCKET"])

        sml = b.new_key("/".join([current_app.config["S3_UPLOAD_DIRECTORY"],destination_filename]))
        sml.set_metadata('Content-Type', source_file.mimetype)
        sml.set_contents_from_string(source_file.read())
        sml.set_acl(acl)

        return "/".join([current_app.config["S3_BUCKET"],current_app.config["S3_UPLOAD_DIRECTORY"],destination_filename])




