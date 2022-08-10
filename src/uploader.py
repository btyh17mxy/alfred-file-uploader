#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright © 2021 dailyinnovation.biz
"""
import sys
import os
sys.path.append(os.path.abspath('./lib'))
from boto3.session import Session
from boto3.s3.transfer import TransferConfig
from workflow import Workflow5
from background import Daemon
import subprocess
import mimetypes
import urllib
from datetime import datetime
import hashlib

__author__ = "Mush Mo <mush@dailyinnovation.biz>"


ICON_ERR = 'error.png'
ICON_CLIPBOARD = 'clipboard.png'

class MyDaemon(Daemon):

    def __init__(self, *args, **kwargs):
        super(MyDaemon, self).__init__(*args, **kwargs)
        self.uploaded = 0

    def progress_listener(self, chunk):
        self.uploaded += chunk
        self.wf.store_data('progress', self.uploaded)

    def run(self, file_path):
        try:
            boto_session = Session(
                aws_access_key_id=os.getenv('AK'),
                aws_secret_access_key=os.getenv('SK'),
                region_name=os.getenv('REGION_NAME')
            )
            s3 = boto_session.client(
                "s3",
                region_name=os.getenv('REGION_NAME')
            )
            content_type = mimetypes.guess_type(
                urllib.request.pathname2url(file_path)
            )[0]

            with open(file_path, 'rb') as f_file:
                file_body = f_file.read()
                file_size = len(file_body)
                self.wf.store_data('total_bytes', file_size)

            file_md5 = hashlib.md5(file_body).hexdigest()
            date_str = datetime.now().strftime("%Y-%m")
            s3_key = f'alfread-upload/{date_str}/{file_md5}.{file_path.split(".")[-1]}'
            s3.upload_file(
                file_path,
                os.getenv('BUCKET_NAME'),
                s3_key,
                ExtraArgs={
                    'ContentType': content_type
                },
                Callback=self.progress_listener,
                Config=TransferConfig(use_threads=False)
            )
            self.wf.store_data(
                'upload_url',
                f'{os.getenv("CDN_HOST")}/{s3_key}'
            )
        except Exception as e:
            self.wf.logger.error(e)
        finally:
            self.wf.store_data('daemon_running', False)
            self.wf.store_data('total_bytes', 0)
            self.wf.store_data('progress', 0)


def main(wf):
    wf.logger.debug(f"started is_firstrun: {wf.is_firstrun}")
    wf.logger.debug(f"show progress bar: {os.getenv('SHOW_PROGRESS_BAR')} {type(os.getenv('SHOW_PROGRESS_BAR'))}")
    import json
    wf.logger.debug(json.dumps(wf.info))
    wf.logger.debug(f"session id: {wf.session_id}")
    d = MyDaemon(
        wf,
        os.path.join(wf.cachedir, f'{wf.session_id}.pid'),
    )
    if wf.is_firstrun:
        env = os.environ
        env['cache_dir'] = wf.cachedir
        proc = subprocess.Popen(
            [
                'osascript',
                'clipboard.scpt'
            ],
            stdout=subprocess.PIPE,
            env=env
        )
        proc.wait()
        file_path = proc.stdout.readline().strip()
        if not file_path:
            wf.add_item(
                title=u'Unable to upload', 
                subtitle='copy a file/html fragment/image to clipboard',
                valid=False,
                icon=ICON_ERR
            )
            wf.send_feedback()
            return 0

        wf.rerun = 0.2
        wf.logger.debug('daemon is not running')
        wf.logger.debug('daemon started')
        wf.logger.debug(file_path)
        wf.add_item("uploading")
        wf.send_feedback()
        d.start(file_path.decode('utf-8'))
        return 0
    if d.is_running:
        wf.rerun = 0.2
        wf.logger.debug('daemon is running')
        uploaded_bytes = int(wf.stored_data('progress', 0))
        total_size = int(wf.stored_data('total_bytes', 0))
        if total_size:
            percentage = 100.0 * uploaded_bytes / total_size
        else:
            percentage = 0.0
        wf.add_item("upload in progress", subtitle=f'progress: {percentage:.2f}%')
        # wf.add_item("upload in progress", subtitle=f'progress: {percentage:.2f}% |{"█" * int(0.3*percentage) :-<30}|')
        wf.send_feedback()
        return 0
    else:
        wf.rerun = 0
        url = wf.stored_data('upload_url')
        if not url:
            wf.add_item('failed')
            wf.send_feedback()
            return 0
        url_list = [
            ('Copy plain url', url),
            ('Copy url as markdown image', f'![]({url})'),
            ('Copy url as rst image', f'.. image:: {url}'),
            ('Copy url as markdown link', f'[Link Text]({url})'),
            ('Copy url as rst link', f'`Link Text <{url}>`_'),
        ]
        for title, url in url_list:
            wf.add_item(
                title=title,
                subtitle=url,
                arg=url,
                icon=ICON_CLIPBOARD,
                valid=True
            )
        wf.send_feedback()
        return 0


if __name__ == "__main__":
    wf = Workflow5()
    sys.exit(wf.run(main))
