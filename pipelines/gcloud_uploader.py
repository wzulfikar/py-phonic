import os
import json
from typing import NamedTuple
from logging import info, error, debug
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import Future

from gcloud import storage


class GCloudUploaderArgs(NamedTuple):
    file: str or Future
    path: str = None


class GCloudUploader:
    def __init__(self, conf: str, pool: ThreadPoolExecutor = None):
        """
        check if os environment can be used for auth. see more:
        https://cloud.google.com/docs/authentication/production#providing_credentials_to_your_application
        """
        info('pipeline initialized: %s', self.__class__.__name__)

        if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
            error("gcloud_uploader: environment is not ready for auth")
            exit(1)

        self.pool = pool

        self.conf = conf
        self.bucket = self.conf['bucket']
        self.creds = json.load(open(conf['cred_file']))
        self.url_tpl = 'https://storage.cloud.google.com/{}/{}'

    def client(self):
        """
        create client for each instance to fight lack of
        thread-safety in httplib2. see more:
        https://github.com/GoogleCloudPlatform/google-cloud-python/issues/3501
        """
        return storage.Client(project=self.creds['project_id'])

    def process(self, count, payload, cli, args: GCloudUploaderArgs) -> str:
        debug('gcloud_uploader pipeline is processing. thread: %s', self.pool)
        args = (count, payload, cli, args)
        if self.pool is None:
            return self._process(*args)
        else:
            future = self.pool.submit(self._process, *args)
            debug('gcloud_uploader future: %s', future)
            return future

    def _process(self, count, payload, cli, args: GCloudUploaderArgs) -> str:
        file = None
        if type(args.file) is Future:
            file = args.file.result()
            debug('file future.result: %s', file)
        else:
            file = args.file

        if file is None:
            error('gc_uploader file is empty')
            return

        if not os.path.exists(file):
            error("gc_uploader file not found: %s", args.file)
            return

        try:
            filename = os.path.basename(file)

            if args.path is not None:
                filename = '{}/{}'.format(args.path, filename)

            bucket = self.client().get_bucket(self.bucket)
            blob = bucket.blob(filename)

            debug('uploading file to cloud storage: %s', file)
            blob.upload_from_filename(file)

            url = self.url_tpl.format(self.bucket, filename)

            info('file uploaded to cloud storage: %s', url)

            return url

        except Exception as e:
            error("gcloud_uploader: %s", e)
            return
