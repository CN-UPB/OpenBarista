##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

import json
import threading
from flask import Flask
from flask_restful import Resource, Api, request

class MastaServer(threading.Thread):

    controller = None

    def __init__(self, masta_controller, logger, port):
        threading.Thread.__init__(self)
        MastaServer.controller = masta_controller
        self.app = Flask(__name__)
        self.api = Api(self.app)
        self.api.add_resource(Alarm,"/alarm")
        self.port = port

    def run(self):
        self.app.run(host="0.0.0.0", port=self.port)

class Alarm(Resource):
    def post(self):
        MastaServer.controller.invoke_monitoring_alarm(request.get_json(silent=True))
