#!/bin/env python
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import os
import sys

from vsm import db
from vsm import context
from vsm import flags
from vsm import exception
from vsm.openstack.common import log as logging
from vsm import utils
from vsm import conductor

import pprint

FLAGS = flags.FLAGS


class Main(object):
    def __init__(self):
        self.conductor_api = conductor.API()

    def main(self, context):
        storage_groups = map(lambda sg: sg['name'],
                self.conductor_api.storage_group_get_all(context))
        storage_groups = list(set(storage_groups))

        #LOG.info("storage_groups is: %s " % storage_groups)
        zones = map(lambda zone: zone['name'],
                self.conductor_api.zone_get_all(context))
        zones = list(set(zones))

        node_info = self.conductor_api.ceph_node_info(context, 1)

        print storage_groups
        print zones
        pprint.pprint(node_info)

if __name__ == '__main__':
    flags.parse_args(sys.argv)
    _context = context.get_admin_context()
    nodes = db.cluster_get_all(_context)
    print nodes

    Main().main(_context)
