#datalab create mydatalabvm --zone us-east1-c

git clone https://github.com/GoogleCloudPlatform/training-data-analyst

cd training-data-analyst/courses/data_analysis/lab2/python

sudo ./install_packages.sh

pip -V


#!/usr/bin/env python

import apache_beam as beam
import re
import sys

def my_grep(line, term):
   if re.match( r'^' + re.escape(term), line):
      yield line

if __name__ == '__main__':
   p = beam.Pipeline(argv=sys.argv)
   input = '../javahelp/src/main/java/com/google/cloud/training/dataanalyst/javahelp/*.java'
   output_prefix = '/tmp/output'
   searchTerm = 'import'

   # find all lines that contain the searchTerm
   (p
      | 'GetJava' >> beam.io.ReadFromText(input)
      | 'Grep' >> beam.FlatMap(lambda line: my_grep(line, searchTerm) )
      | 'write' >> beam.io.WriteToText(output_prefix)
   )

   p.run().wait_until_finish()



gsutil cp ../javahelp/src/main/java/com/google/cloud/training/dataanalyst/javahelp/*.java gs://qwiklabs-gcp-a910dde7a992b2bb/javahelp








grepc python file:
#!/usr/bin/env python

import apache_beam as beam
import re

def my_grep(line, term):
   if re.match( r'^' + re.escape(term), line):
      yield line

PROJECT='cloud-training-demos'
BUCKET='cloud-training-demos'

def run():
   argv = [
      '--project={0}'.format(PROJECT),
      '--job_name=examplejob2',
      '--save_main_session',
      '--staging_location=gs://{0}/staging/'.format(BUCKET),
      '--temp_location=gs://{0}/staging/'.format(BUCKET),
      '--runner=DataflowRunner'
   ]

   p = beam.Pipeline(argv=argv)
   input = 'gs://{0}/javahelp/*.java'.format(BUCKET)
   output_prefix = 'gs://{0}/javahelp/output'.format(BUCKET)
   searchTerm = 'import'

   # find all lines that contain the searchTerm
   (p
      | 'GetJava' >> beam.io.ReadFromText(input)
      | 'Grep' >> beam.FlatMap(lambda line: my_grep(line, searchTerm) )
      | 'write' >> beam.io.WriteToText(output_prefix)
   )

   p.run()

if __name__ == '__main__':
   run()

python grepc.py


gsutil cat gs://qwiklabs-gcp-a910dde7a992b2bb/javahelp/output-*


Executed a Dataflow pipeline locally
Executed a Dataflow pipeline on the cloud.