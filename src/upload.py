#!/usr/bin/python
# encoding: utf-8
import os
import sys
sys.path.append('./lib')  # noqa

import subprocess
import hashlib
from imgurpython import ImgurClient

from workflow import Workflow3 as Workflow
from workflow.background import is_running, run_in_background


ICON_ERROR = 'error.png'
ICON_CLIPBOARD = 'clipboard.png'


def get_file_type(file_path):
    return file_path.split('.')[-1].lower()


def imgur_uploader(wf, file_path):
    support_type = ['jpeg', 'png', 'gif', 'apng', 'tiff', 'pdf', 'jpg']
    if get_file_type(file_path) not in support_type:
        error = u'imgur only support {}'.format(','.join(support_type))
        return '', error
    client_id = os.getenv(u'IMGUR_CLIENT_ID', None)
    client_secret = os.getenv(u'IMGUR_CLIENT_SECRET', None)
    url, error = '', False

    if not client_id:
        error = u'please set IMGUR_CLIENT_ID'
    if not client_secret:
        error = u'please set IMGUR_CLIENT_SECRET'
    if client_id and client_secret:
        client = ImgurClient(client_id, client_secret)
        resp = client.upload_from_path(file_path)
        url = resp['link']
        error = False

    return url, error


def main(wf):
    log = wf.logger
    uploader_backend = os.getenv(u'UPLOADER_BACKEND', 'aws').lower()
    log.debug('main start, using backend %s' % uploader_backend)

    is_uploading = False
    bg_name = wf.stored_data('bg_name')
    upload_started = wf.stored_data('upload_started')
    log.debug('upload_started: %s' % upload_started)
    log.debug('bg_name: %s' % bg_name)
    if bg_name:
        is_uploading = is_running(bg_name)

    should_copy_file = all((
        not is_uploading,
        not upload_started,
    )) or uploader_backend == 'imgur'

    log.debug('should_copy_file: %s' % should_copy_file)

    file_path = None
    if should_copy_file:
        proc = subprocess.Popen(
            [
                'osascript',
                'clipboard.scpt'
            ],
            stdout=subprocess.PIPE,
        )
        proc.wait()
        file_path = proc.stdout.readline().strip()
        if not file_path:
            wf.add_item(
                title=u'Unable to upload', 
                subtitle='copy a file or image to clipboard',
                valid=False,
                icon=ICON_ERROR
            )
            wf.send_feedback()
            return 0
    url = error = None
    if uploader_backend == 'imgur':
        url, error = imgur_uploader(wf, file_path)
    elif not is_uploading and not upload_started:
        log.debug('uploader is not running')
        wf.store_data('uploaded_bytes', 0)
        bg_name = hashlib.md5(file_path).hexdigest()
        log.debug(file_path)

        if not file_path:
            wf.add_item(
                title=u'Unable to upload',
                subtitle='copy a file or image to clipboard',
                valid=False,
                icon=ICON_ERROR
            )
            wf.store_data('upload_started', False)
        else:
            wf.rerun = 0.5
            wf.store_data('bg_name', bg_name)
            wf.store_data('upload_started', True)
            run_in_background(
                bg_name,
                [
                    '/usr/bin/python',
                    wf.workflowfile('aws_uploader.py'),
                    file_path
                ]
            )
            wf.add_item(
                "Upload file",
                "Uploading in progress ..."
            )
    else:
        bg_name = wf.stored_data('bg_name')
        if is_running(bg_name):
            wf.rerun = 0.5
            uploaded_bytes = int(wf.stored_data('uploaded_bytes') or 0)
            total_bytes = int(wf.stored_data('total_bytes'))
            percentage = 100.0 * uploaded_bytes / total_bytes

            wf.add_item(
                "Upload file",
                "Uploading in progress, %2.1f%% done." % (percentage)
            )
        else:
            """Last case"""
            wf.store_data('upload_started', False)
            url = wf.stored_data('upload_url')
            wf.store_data('upload_url', None)
            error = wf.stored_data('upload_error')
            wf.store_data('upload_error', None)

    if error and not is_uploading:
        wf.add_item(
            title=u'Unable to upload',
            subtitle=error,
            valid=False,
            icon=ICON_ERROR
        )
    if url and not is_uploading:
        wf.add_item(
            title=u'Copy url',
            subtitle=url,
            arg=url,
            valid=True,
            icon=ICON_CLIPBOARD,
            quicklookurl=url
        )
        md_image_url = u'![]({})'.format(url)
        wf.add_item(
            title=u'Copy url as markdown image',
            subtitle=md_image_url,
            arg=md_image_url,
            icon=ICON_CLIPBOARD,
            valid=True
        )
        rst_image_url = u'.. image:: {}'.format(url)
        wf.add_item(
            title=u'Copy url as rst image',
            subtitle=rst_image_url,
            icon=ICON_CLIPBOARD,
            arg=rst_image_url,
            valid=True
        )
        md_url = u'[Link Text]({})'.format(url)
        wf.add_item(
            title=u'Copy url as markdown link',
            subtitle=md_url,
            arg=md_url,
            icon=ICON_CLIPBOARD,
            valid=True
        )
        rst_url = u'`Link Text <{}>`_'.format(url)
        wf.add_item(
            title=u'Copy url as rst link',
            subtitle=rst_url,
            icon=ICON_CLIPBOARD,
            arg=rst_url,
            valid=True
        )

    wf.send_feedback()


if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main))
