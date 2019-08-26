#!/usr/bin/python
# encoding: utf-8
import sys
sys.path.append('./lib')  # noqa

import subprocess
import hashlib

from workflow import Workflow3 as Workflow
from workflow.background import is_running, run_in_background


ICON_ERROR = 'error.png'
ICON_CLIPBOARD = 'clipboard.png'


def get_file_type(file_path):
    return file_path.split('.')[-1].lower()


def main(wf):
    log = wf.logger
    log.debug('main start')
    try:
        total_bytes = int(wf.stored_data('total_bytes'))
        log.debug("totalBytes: %s" % total_bytes)
    except Exception as e:
        log.error(e)

    is_uploading = False
    bg_name = wf.stored_data('bg_name')
    upload_started = wf.stored_data('upload_started')
    log.debug('upload_started: %s' % upload_started)
    log.debug('bg_name: %s' % bg_name)
    if bg_name:
        is_uploading = is_running(bg_name)

    if not is_uploading and not upload_started:
        log.debug('uploader is not running')
        wf.store_data('uploaded_bytes', 0)
        proc = subprocess.Popen(
            [
                'osascript',
                'clipboard.scpt'
            ],
            stdout=subprocess.PIPE,
        )
        proc.wait()
        file_path = proc.stdout.readline().strip()
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
            if error:
                wf.add_item(
                    title=u'Unable to upload',
                    subtitle=error,
                    valid=False,
                    icon=ICON_ERROR
                )
            else:
                wf.add_item(
                    title=u'Copy url',
                    subtitle=url,
                    arg=url,
                    valid=True,
                    icon=ICON_CLIPBOARD,
                    quicklookurl=url
                )
                md_url = u'![]({})'.format(url)
                wf.add_item(
                    title=u'Copy markdown url',
                    subtitle=md_url,
                    arg=md_url,
                    icon=ICON_CLIPBOARD,
                    valid=True
                )
                rst_url = u'.. image:: {}'.format(url)
                wf.add_item(
                    title=u'Copy rst url',
                    subtitle=rst_url,
                    icon=ICON_CLIPBOARD,
                    arg=rst_url,
                    valid=True
                )

    wf.send_feedback()


if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main))
