#!/usr/bin/python
# encoding: utf-8
import sys
import os

from lib.workflow.util import set_config
from lib.workflow.notify import notify
from lib.workflow import Workflow3


def main(wf):
    args = wf.args
    if args[0] == u'id':
        set_config('IMGUR_CLIENT_ID', args[1] if len(args) == 2 else '')
        notify('imgur client id saved !')
    elif args[0] == u'secret':
        set_config('IMGUR_CLIENT_SECRET', args[1] if len(args) == 2 else '')
        notify('imgur client secret saved !')
    else:
        notify('Nothing to do')
    return 0


if __name__ == '__main__':
    wf = Workflow3()
    sys.exit(wf.run(main))
