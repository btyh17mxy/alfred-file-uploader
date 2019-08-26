#!/usr/bin/python
# encoding: utf-8
import sys
import os

from lib.workflow.util import set_config
from lib.workflow.notify import notify
from lib.workflow import Workflow


def main(wf):
    args = wf.args
    print(args)
    if len(args) < 2:
        return 0
    if not args[1]:
        return 0
    if args[0] == u'imgur_client_id':
        set_config('IMGUR_CLIENT_ID', args[1])
        notify('imgur client id saved !')
    elif args[0] == u'imgur_client_secret':
        set_config('IMGUR_CLIENT_SECRET', args[1])
        notify('imgur client secret saved !')
    elif args[0] == u'aws_access_key_id':
        set_config('AWS_ACCESS_KEY_ID', args[1])
        notify('aws access key id saved !')
    elif args[0] == u'aws_secret_access_key':
        set_config('AWS_SECRET_ACCESS_KEY', args[1])
        notify('aws secret access key saved !')
    elif args[0] == u'aws_region':
        set_config('AWS_REGION_NAME', args[1])
        notify('aws region name saved !')
    else:
        notify('Nothing to do')
    return 0


if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main))
