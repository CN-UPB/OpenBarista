##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##
import paramiko
import logging

class Element(object):
    pass

class IElementManager(object):


    def before_pause(self, *args, **kwargs):
        pass

    def after_startup(self, *args, **kwargs):
        pass

    def before_shutdown(self, *args, **kwargs):
        pass

    def new_predecessor(self, *args, **kwargs):
        pass

    def new_successor(self, *args, **kwargs):
        pass

    def delete_predecessor(self, *args, **kwargs):
        pass

    def delete_successor(self, *args, **kwargs):
        pass

    def get_status(self,*args,**kwargs):
        pass


class IElementListener(object):

    def poll(self, tag, *args, **kwargs):
        pass

    def on_event(self, tag, *args, **kwargs):
        pass


class ElementProxy(IElementManager):
    pass


class ElementListener(IElementManager):
    pass


class ElementManagerAgent(IElementManager):
    pass