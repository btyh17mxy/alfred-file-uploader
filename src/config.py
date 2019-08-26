#!/usr/bin/python
# encoding: utf-8
import sys
from lib.workflow import Workflow


ICON_CONFIG = 'config.png'


ICON_KEY = 'key.png'

def main(wf):
    args = wf.args
    wf.add_item(
        title=u'set imgur client id', 
        subtitle=u'id',
        arg='imgur_client_id',
        valid=True,
        icon=ICON_KEY
    )
    wf.add_item(
        title=u'set imgur client secret', 
        subtitle=u'secret',
        arg='imgur_client_secret',
        valid=True,
        icon=ICON_KEY
    )
    wf.add_item(
        title=u'set aws access key id', 
        subtitle=u'aws access key id',
        arg='aws_access_key_id',
        valid=True,
        icon=ICON_KEY
    )
    wf.add_item(
        title=u'set aws secret access key', 
        subtitle=u'aws secret access key',
        arg='aws_secret_access_key',
        valid=True,
        icon=ICON_KEY
    )
    wf.add_item(
        title=u'set aws region', 
        subtitle=u'aws region',
        arg='aws_region',
        valid=True,
        icon=ICON_KEY
    )
    wf.send_feedback()


if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main))
