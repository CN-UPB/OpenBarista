#!/usr/bin/env python

##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

import model
__author__ = ''


class DocGenerator(object):

    @staticmethod
    def print_entities():

        classes_dict = dict([(name, cls) for name, cls in model.__dict__.items() if isinstance(cls, type)])
        for cls_name, cls in sorted(classes_dict.iteritems()):
                print cls_name

    @staticmethod
    def print_call_types():
        """
            prints docu for call_type in ['add', 'get', 'delete', 'update']:
        :return:
        """

        print ''
        print 'h2. add'
        print ''
        print 'usage:'
        print '* rpc method: @storage.add_<entity>@'
        print '* arguments:'
        print '@data@: dictionary of properties'

        print ''
        print 'h2. get'
        print ''
        print 'usage:'
        print '* rpc method: @storage.get_<entity>@'
        print '* arguments:'
        print '@options: array of strings@'
        print 'loads nested entities'
        print 'Example:'
        print ' @["vms", "sce_vnfs.scenario"]@ would also appended vms and the parent scenario of a vnf'
        print '@filters@: dictionary'
        print ' filters for properties'
        print ' Example:'
        print '  @{"uuid": "123" }@ would filter for entity with uuid 123'

        print ''
        print 'h2. update'
        print ''
        print 'usage:'
        print '* rpc method: @storage.update_<entity>@'
        print '* arguments:'
        print '@uuid@: string'
        print ' the uuid of the object to update'
        print '@data@: dictionary of properties to update'

        print ''
        print 'h2. delete'
        print ''
        print 'usage:'
        print '* rpc method: @storage.delete_<entity>@'
        print '* arguments:'
        print '@uuid@: string'
        print ' the uuid of the object to delete'


if __name__ == '__main__':

    generator = DocGenerator()
    print 'h2. supported entities:'
    print
    generator.print_entities()

    print 'h2. supported operations'
    print ''
    generator.print_call_types()

