##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

class ProxyProtocol(object):

    def configureProtocol(self, *args, **kwargs):
        pass

    def connect(self, *args, **kwargs):
        pass

    def invoke(self, *args, **kwargs):
        pass

    def listenForNotification(self, tag, function_ptr, *args, **kwargs):
        pass


class RESTProtocol(object):

    def configureProtocol(self, *args, **kwargs):
        pass

    def connect(self, *args, **kwargs):
        pass

    def invoke(self, *args, **kwargs):
        pass

    def listenForNotification(self, tag, function_ptr, *args, **kwargs):
        pass

class RabbitMQProtocol(object):

    def configureProtocol(self, *args, **kwargs):
        pass

    def connect(self, *args, **kwargs):
        pass

    def invoke(self, *args, **kwargs):
        pass

    def listenForNotification(self, tag, function_ptr, *args, **kwargs):
        pass

