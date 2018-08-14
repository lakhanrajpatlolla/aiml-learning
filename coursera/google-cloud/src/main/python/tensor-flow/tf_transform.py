%bash
pip uninstall -y google-cloud-dataflow
pip install --upgrade --force tensorflow_transform==0.6.0 apache-beam[gcp]



# change these to try this notebook out
BUCKET = 'qwiklabs-gcp-84572a16d020c88c'
PROJECT = 'qwiklabs-gcp-84572a16d020c88c'
REGION = 'us-central1'

import os
os.environ['BUCKET'] = BUCKET
os.environ['PROJECT'] = PROJECT
os.environ['REGION'] = REGION

%bash
gcloud config set project $PROJECT
gcloud config set compute/region $REGION



import google.datalab.bigquery as bq
def create_query(phase, EVERY_N):
  """
  phase: 1=train 2=valid
  """
  base_query = """
WITH daynames AS
  (SELECT ['Sun', 'Mon', 'Tues', 'Wed', 'Thurs', 'Fri', 'Sat'] AS daysofweek)
SELECT
  (tolls_amount + fare_amount) AS fare_amount,
  daysofweek[ORDINAL(EXTRACT(DAYOFWEEK FROM pickup_datetime))] AS dayofweek,
  EXTRACT(HOUR FROM pickup_datetime) AS hourofday,
  pickup_longitude AS pickuplon,
  pickup_latitude AS pickuplat,
  dropoff_longitude AS dropofflon,
  dropoff_latitude AS dropofflat,
  passenger_count AS passengers,
  'notneeded' AS key
FROM
  `nyc-tlc.yellow.trips`, daynames
WHERE
  trip_distance > 0 AND fare_amount > 0
  """

  if EVERY_N == None:
    if phase < 2:
      # training
      query = "{0} AND MOD(ABS(FARM_FINGERPRINT(CAST(pickup_datetime AS STRING)),4) < 2".format(base_query)
    else:
      query = "{0} AND MOD(ABS(FARM_FINGERPRINT(CAST(pickup_datetime AS STRING)),4) = {1}".format(base_query, phase)
  else:
      query = "{0} AND MOD(ABS(FARM_FINGERPRINT(CAST(pickup_datetime AS STRING))),{1}) = {2}".format(base_query, EVERY_N, phase)
    
  return query

query = create_query(2, 100000)







df_valid = bq.Query(query).execute().result().to_dataframe()
df_valid.head()
df_valid.describe()



import datetime
import tensorflow as tf
import apache_beam as beam
import tensorflow_transform as tft
from tensorflow_transform.beam import impl as beam_impl

def is_valid(inputs):
  try:
    pickup_longitude = inputs['pickuplon']
    dropoff_longitude = inputs['dropofflon']
    pickup_latitude = inputs['pickuplat']
    dropoff_latitude = inputs['dropofflat']
    hourofday = inputs['hourofday']
    dayofweek = inputs['dayofweek']
    passenger_count = inputs['passengers']
    fare_amount = inputs['fare_amount']
    return (fare_amount >= 2.5 and pickup_longitude > -78 and pickup_longitude < -70 \
      and dropoff_longitude > -78 and dropoff_longitude < -70 and pickup_latitude > 37 \
      and pickup_latitude < 45 and dropoff_latitude > 37 and dropoff_latitude < 45 \
      and passenger_count > 0)
  except:
    return False
  
def preprocess_tft(inputs):
      import datetime   
      print inputs
      result = {}
      result['fare_amount'] = tf.identity(inputs['fare_amount'])     
      result['dayofweek'] = tft.string_to_int(inputs['dayofweek']) # builds a vocabulary
      result['hourofday'] = tf.identity(inputs['hourofday']) # pass through
      result['pickuplon'] = (tft.scale_to_0_1(inputs['pickuplon'])) # scaling numeric values
      result['pickuplat'] = (tft.scale_to_0_1(inputs['pickuplat']))
      result['dropofflon'] = (tft.scale_to_0_1(inputs['dropofflon']))
      result['dropofflat'] = (tft.scale_to_0_1(inputs['dropofflat']))
      result['passengers'] = tf.cast(inputs['passengers'], tf.float32) # a cast
      result['key'] = tf.as_string(tf.ones_like(inputs['passengers'])) # arbitrary TF func
      # engineered features
      latdiff = inputs['pickuplat'] - inputs['dropofflat']
      londiff = inputs['pickuplon'] - inputs['dropofflon']
      result['latdiff'] = tft.scale_to_0_1(latdiff)
      result['londiff'] = tft.scale_to_0_1(londiff)
      dist = tf.sqrt(latdiff * latdiff + londiff * londiff)
      result['euclidean'] = dist
      return result

def preprocess(in_test_mode):
  import os
  import os.path
  import tempfile
  from apache_beam.io import tfrecordio
  from tensorflow_transform.coders import example_proto_coder
  from tensorflow_transform.tf_metadata import dataset_metadata
  from tensorflow_transform.tf_metadata import dataset_schema
  from tensorflow_transform.beam import tft_beam_io
  from tensorflow_transform.beam.tft_beam_io import transform_fn_io

  job_name = 'preprocess-taxi-features' + '-' + datetime.datetime.now().strftime('%y%m%d-%H%M%S')    
  if in_test_mode:
    import shutil
    print 'Launching local job ... hang on'
    OUTPUT_DIR = './preproc_tft'
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
    EVERY_N = 100000
  else:
    print 'Launching Dataflow job {} ... hang on'.format(job_name)
    OUTPUT_DIR = 'gs://{0}/taxifare/preproc_tft/'.format(BUCKET)
    import subprocess
    subprocess.call('gsutil rm -r {}'.format(OUTPUT_DIR).split())
    EVERY_N = 10000
    
  options = {
    'staging_location': os.path.join(OUTPUT_DIR, 'tmp', 'staging'),
    'temp_location': os.path.join(OUTPUT_DIR, 'tmp'),
    'job_name': job_name,
    'project': PROJECT,
    'max_num_workers': 24,
    'teardown_policy': 'TEARDOWN_ALWAYS',
    'no_save_main_session': True,
    'requirements_file': 'requirements.txt'
  }
  opts = beam.pipeline.PipelineOptions(flags=[], **options)
  if in_test_mode:
    RUNNER = 'DirectRunner'
  else:
    RUNNER = 'DataflowRunner'

  # set up metadata
  raw_data_schema = {
    colname : dataset_schema.ColumnSchema(tf.string, [], dataset_schema.FixedColumnRepresentation())
                   for colname in 'dayofweek,key'.split(',')
  }
  raw_data_schema.update({
      colname : dataset_schema.ColumnSchema(tf.float32, [], dataset_schema.FixedColumnRepresentation())
                   for colname in 'fare_amount,pickuplon,pickuplat,dropofflon,dropofflat'.split(',')
    })
  raw_data_schema.update({
      colname : dataset_schema.ColumnSchema(tf.int64, [], dataset_schema.FixedColumnRepresentation())
                   for colname in 'hourofday,passengers'.split(',')
    })
  raw_data_metadata = dataset_metadata.DatasetMetadata(dataset_schema.Schema(raw_data_schema))

  # run Beam  
  with beam.Pipeline(RUNNER, options=opts) as p:
    with beam_impl.Context(temp_dir=os.path.join(OUTPUT_DIR, 'tmp')):
      # save the raw data metadata
      _ = (raw_data_metadata
        | 'WriteInputMetadata' >> tft_beam_io.WriteMetadata(
            os.path.join(OUTPUT_DIR, 'metadata/rawdata_metadata'),
            pipeline=p))
      
      # analyze and transform training       
      raw_data = (p 
        | 'train_read' >> beam.io.Read(beam.io.BigQuerySource(query=create_query(1, EVERY_N), use_standard_sql=True))
        | 'train_filter' >> beam.Filter(is_valid))

      raw_dataset = (raw_data, raw_data_metadata)
      transformed_dataset, transform_fn = (
          raw_dataset | beam_impl.AnalyzeAndTransformDataset(preprocess_tft))
      transformed_data, transformed_metadata = transformed_dataset
      _ = transformed_data | 'WriteTrainData' >> tfrecordio.WriteToTFRecord(
          os.path.join(OUTPUT_DIR, 'train'),
          file_name_suffix='.gz',
          coder=example_proto_coder.ExampleProtoCoder(
              transformed_metadata.schema))
      
      # transform eval data
      raw_test_data = (p 
        | 'eval_read' >> beam.io.Read(beam.io.BigQuerySource(query=create_query(2, EVERY_N), use_standard_sql=True))
        | 'eval_filter' >> beam.Filter(is_valid))
      
      raw_test_dataset = (raw_test_data, raw_data_metadata)
      transformed_test_dataset = (
          (raw_test_dataset, transform_fn) | beam_impl.TransformDataset())
      transformed_test_data, _ = transformed_test_dataset
      _ = transformed_test_data | 'WriteTestData' >> tfrecordio.WriteToTFRecord(
          os.path.join(OUTPUT_DIR, 'eval'),
          file_name_suffix='.gz',
          coder=example_proto_coder.ExampleProtoCoder(
              transformed_metadata.schema))
      _ = (transform_fn
           | 'WriteTransformFn' >>
           transform_fn_io.WriteTransformFn(os.path.join(OUTPUT_DIR, 'metadata')))

preprocess(in_test_mode=False)



%bash
rm -rf taxifare_tft.tar.gz taxi_trained
export PYTHONPATH=${PYTHONPATH}:$PWD/taxifare_tft
python -m trainer.task \
   --train_data_paths="gs://${BUCKET}/taxifare/preproc_tft/train*" \
   --eval_data_paths="gs://${BUCKET}/taxifare/preproc_tft/eval*"  \
   --output_dir=./taxi_trained \
   --train_steps=10 --job-dir=/tmp \
   --metadata_path=gs://${BUCKET}/taxifare/preproc_tft/metadata