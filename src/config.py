#!/usr/bin/python
# encoding: utf-8
import sys
from lib.workflow import Workflow3


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
    wf.send_feedback()


if __name__ == '__main__':
    wf = Workflow3()
    sys.exit(wf.run(main))
