#!/usr/bin/python
# encoding: utf-8

import os
import sys
import subprocess
import requests
import urllib, mimetypes
import hashlib
import re

from lib.workflow import Workflow3 as Workflow


ICON_ERROR = 'error.png'
ICON_CLIPBOARD = 'clipboard.png'
uploaded = 0


def main(wf):
    wff = wf
    wf.store_data('is_uploading', 'true')
    wf.store_data('uploaded_bytes', 0)
    wf.store_data('total_bytes', 0)
    log = wf.logger
    file_path = sys.argv[1]
    progress = {'total': 0, 'now': 0}
    aws_region_name = os.getenv(u'AWS_REGION_NAME', None)
    aws_access_key_id = os.getenv(u'AWS_ACCESS_KEY_ID', None)
    aws_secret_access_key = os.getenv(u'AWS_SECRET_ACCESS_KEY', None)
    aws_cdn_prefix = os.getenv(u'AWS_CDN_PREFIX', None)
    aws_bucket_name = os.getenv(u'AWS_BUCKET_NAME', None)
    config = {
        "AWS_REGION_NAME": aws_region_name,
        "AWS_ACCESS_KEY_ID": aws_access_key_id,
        "AWS_SECRET_ACCESS_KEY": aws_secret_access_key,
        "AWS_CDN_PREFIX": aws_cdn_prefix,
        "AWS_BUCKET_NAME": aws_bucket_name
    }
    url, error = '', False

    for key, value in config.items():
        if not value:
            error = u'%s not config' % key
            return url, error
    client = boto3.client(
        's3',
        region_name=aws_region_name
    )
    content_type = mimetypes.guess_type(urllib.pathname2url(file_path))[0]
    with open(file_path, 'rb') as f_file:
        file_body = f_file.read()
        progress['total'] = len(file_body)
        wf.store_data('total_bytes', progress['total'])
    file_md5 = hashlib.md5(file_body).hexdigest()
    s3_key = 'alfread-upload/%s.%s' % (file_md5, file_path.split('.')[-1])
    
    def progress_listener(chunk):
        global uploaded
        uploaded += chunk
        wf.store_data('uploaded_bytes', uploaded)

    try:
        client.upload_file(
            file_path,
            aws_bucket_name,
            s3_key,
            ExtraArgs={
                'ContentType': content_type
            },
            Callback=progress_listener,
            Config=TransferConfig(use_threads=False)
        )
    except Exception as e:
        error = str(e)

    # upload with presigned url through Cloudfront not work with Origin Access Identity
    # upload_url = client.generate_presigned_url(
    #     'put_object',
    #     Params={
    #         'Bucket': aws_bucket_name,
    #         'Key': s3_key,
    #         'ContentType': content_type,
    #     },
    #     ExpiresIn=300,
    #     HttpMethod='PUT'
    # )
    # upload_url = re.sub(
    #     r'https://s3\.[a-z0-1-]*\.amazonaws\.com\/[^/]*',
    #     aws_cdn_prefix,
    #     upload_url
    # )
    # resp = requests.put(
    #     upload_url,
    #     data=open(file_path, 'rb'),
    #     headers={
    #         'content-type': content_type,
    #     }
    # )
    # if resp.status_code == 200:
    #     url = os.path.join(aws_cdn_prefix, s3_key)
    # else:
    #     error = 'Upload fail, please check log'
    # return url, error

    url = os.path.join(aws_cdn_prefix, s3_key)
    if error:
        wf.store_data('upload_error', error)
        wf.store_data('upload_url', None)
    else:
        wf.store_data('upload_url', url)
        wf.store_data('upload_error', None)
    log.error('done')

if __name__ == '__main__':
    wf = Workflow(libraries=['./lib'])
    import boto3
    from boto3.s3.transfer import TransferConfig
    sys.exit(wf.run(main))
