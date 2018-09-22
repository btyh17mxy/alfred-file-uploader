#!/usr/bin/python
# encoding: utf-8

import os
import sys
import subprocess

from lib.workflow import Workflow3
from lib.imgurpython import ImgurClient


ICON_ERROR = 'error.png'
ICON_CLIPBOARD = 'clipboard.png'


def get_file_type(file_path):
    return file_path.split('.')[-1].lower()


def imgur_uploader(wf, file_path):
    support_type = ['jpeg', 'png', 'gif', 'apng', 'tiff', 'pdf', 'jpg']
    if get_file_type(file_path) not in support_type:
        wf.add_item(
            title=u'unsupport file type', 
            subtitle=u'imgur only support {}'.format(','.join(support_type)),
            valid=False,
            icon=ICON_ERROR
        )
        error = 'file type not support by imgur'
        return '', error
    client_id = os.getenv(u'IMGUR_CLIENT_ID', None)
    client_secret = os.getenv(u'IMGUR_CLIENT_SECRET', None)
    url, error = '', False

    if not client_id:
        wf.add_item(
            title=u'IMGUR_CLIENT_ID not set', 
            subtitle=u'please set IMGUR_CLIENT_ID by useing config-imgur',
            valid=False,
            icon=ICON_ERROR
        )
        error = 'imgur not configured'
    if not client_secret:
        wf.add_item(
            title=u'IMGUR_CLIENT_SECRET not set', 
            subtitle=u'please set IMGUR_CLIENT_SECRET by useing config-imgur',
            valid=False,
            icon=ICON_ERROR
        )
        error = 'imgur not configured'
    if client_id and client_secret:
        client = ImgurClient(client_id, client_secret)
        resp = client.upload_from_path(file_path)
        url = resp['link']
        error = False

    return url, error


def main(wf):
    args = wf.args

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
    else:
        url, error = imgur_uploader(wf, file_path)
        if not error:
            wf.add_item(
                title=u'Copy url', 
                subtitle=url,
                arg=url,
                valid=True,
                icon=ICON_CLIPBOARD ,
                quicklookurl=url
            )
            md_url = u'![]({})'.format(url)
            wf.add_item(
                title=u'Copy markdown url', 
                subtitle=md_url,
                arg=md_url,
                icon=ICON_CLIPBOARD ,
                valid=True
            )
            rst_url = u'.. image:: {}'.format(url)
            wf.add_item(
                title=u'Copy rst url', 
                subtitle=rst_url,
                icon=ICON_CLIPBOARD ,
                arg=rst_url,
                valid=True
            )
        else:
            wf.add_item(
                title=u'Upload error', 
                subtitle=error,
                arg=error,
                valid=True,
                icon=ICON_ERROR
            )

    wf.send_feedback()


if __name__ == '__main__':
    wf = Workflow3(libraries=['./lib'])
    sys.exit(wf.run(main))
