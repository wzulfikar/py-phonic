import os
import sys
import yaml

from gcloud_uploader import GCloudUploader, GCloudUploaderArgs

if len(sys.argv) < 3:
    print('USAGE: gcloud_uploader_test.py <config file> <dummy file>')
    exit(0)

config_file = sys.argv[1]
dummy_file = sys.argv[2]

conf = yaml.safe_load(open(config_file))
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = conf['gcloud']['cred_file']

uploader = GCloudUploader(conf['gcloud'])
print('uploader type:', type(uploader))

print('uploaded file:', dummy_file)
args = GCloudUploaderArgs(file=dummy_file, path='test-uploader')
url = uploader.process(0, None, 'test-uploader', args)

print('file uploaded:', url)
