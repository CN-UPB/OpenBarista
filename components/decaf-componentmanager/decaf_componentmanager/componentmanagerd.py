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

import time
import sys
import getopt
import logging
import signal

import yaml
from daemon import DaemonContext
from lockfile.pidlockfile import PIDLockFile
from . import __version__, version_date
from .bunnyconnector import BunnyConnector
from .model.database import Database
from .componentregistry import ComponentRegistry
from .contractregistry import ContractRegistry

__author__ = "Andreas Krakau"
__date__ = "$25-aug-2015 16:03:02$"

PIDFILE = '/var/run/decaf/componentmanagerd.pid'
LOGFILE = '/var/log/decaf/componentmanagerd.log'
CONFIGFILE = '/etc/decaf/componentmanagerd.cfg'

component_manager = None
context = None

class ComponentManagerDaemon:
    def __init__(self, logger, configuration_file=CONFIGFILE):
        self.logger = logger
        self.configuration_file = configuration_file
        self.config = self.load_configuration()
        self.logger.setLevel(self.config['log']['level'])
        self.db = None
        self.component_register = None
        self.contract_register = None
        self.bunny_connector = None
        self.running = True

    def load_configuration(self):
        try:
            f = open(self.configuration_file)
            config = yaml.safe_load(f)
            f.close()
            result = {}
            if 'mysql' in config['database']:
                result["database"] = {}
                result["database"]["type"] = 'mysql'
                result["database"]["host"] = config['database']['mysql']['host']
                result["database"]["port"] = config['database']['mysql']['port']
                result["database"]["database"] = config['database']['mysql']['database']
                result["database"]["user"] = config['database']['mysql']['user']
                result["database"]["password"] = config['database']['mysql']['password']
            elif 'sqlite' in config['database']:
                result["database"] = {}
                result["database"]["type"] = 'sqlite'
                result["database"]["file"] = config['database']['sqlite']['file']
            result['log'] = {}
            result['log']['level'] = logging.DEBUG
            if 'log' in config:
                if 'level' in config['log']:
                    if config['log']['level'] == 'DEBUG':
                        result['log']['level'] = logging.DEBUG
                    elif config['log']['level'] == 'WARN':
                        result['log']['level'] = logging.WARN
                    elif config['log']['level'] == 'INFO':
                        result['log']['level'] = logging.INFO
            result['rpc'] = {'url': None}
            if 'rpc' in config:
                if 'url' in config['rpc']:
                    result['rpc']['url'] = config['rpc']['url']

            return result
        except yaml.YAMLError, err:
            if hasattr(err, 'problem_mark'):
                mark = err.problem_mark
                self.logger.exception(
                    "Error in configuration file at position: (%s:%s)" % (mark.line + 1, mark.column + 1))
            else:
                self.logger.exception("Error in configuration file: %s" % err.message)

    def run(self):
        self.logger.debug('Connect to Database')
        self.db = Database(self.config["database"])
        self.logger.debug('Create ContractRegistry')
        self.contract_register = ContractRegistry(self.db,  self.logger)
        self.logger.debug('Create ComponentRegistry')
        self.component_register = ComponentRegistry(self.db, self.contract_register, self.logger)
        self.logger.debug('Create BunnyConnector')
        self.bunny_connector = BunnyConnector(self.config['rpc']['url'], self.component_register, self.contract_register, self.logger)
        while self.running:
            self.logger.debug('Request heartbeats')
            # self.component_register.request_heartbeats(self.bunny_connector)
            time.sleep(300)
        self.logger.debug('Main loop stopped')
        sys.exit()

    def __del__(self):
        self.dispose()

    def dispose(self):
        self.logger.debug('Terminating ComponentManager...')
        if self.running:
            self.running = False

            self.db.dispose()
            if self.bunny_connector is not None:
                self.bunny_connector.dispose()
                del self.bunny_connector
                self.bunny_connector = None
            del self.contract_register
            del self.component_register
            del self.db


def usage():
    print "usage: ", sys.argv[0], "[arguments]\n"
    print "Arguments:"
    print "  -c\tReads the configuration from the given file"
    print "  -p\tSets the PID file"
    print "  -l\tSets the log file"
    print "  -w\tChanges the working directory to the given one"
    print "  -h\tPrint this help message and exit"
    print "  -v\tPrint version information and exit"
    return


def version():
    print sys.argv[0], __version__, '(' + version_date + ')'
    return


def shutdown(signal_number, stack_frame):
    global component_manager
    component_manager.logger.debug(
        'Received signal %s (%s)' % (signal_number, (v for v, k in signal.__dict__.items() if
                                     v.startswith('SIG') and not v.startswith('SIG_') and k == signal_number).next()))

    component_manager.logger.debug('Shutting down...')
    component_manager.dispose()


def daemon():
    configuration_file = CONFIGFILE
    pid_file = PIDFILE
    working_directory = "/"
    log_file = LOGFILE

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hvc:p:w:l:", ["help", "version"])
    except getopt.GetoptError, err:
        print "Error:", err
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-v", "--version"):
            version()
            sys.exit()
        elif opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt == "-c":
            configuration_file = arg
        elif opt == "-p":
            pid_file = arg
        elif opt == "-w":
            working_directory = arg
        elif opt == "-l":
            log_file = arg
        else:
            usage()
            sys.exit(2)

    # Configure logging
    logger = logging.getLogger('ComponentManager')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(log_file)
    logger.addHandler(fh)

    logger.info('Starting component manager daemon')
    logger.debug('PIDFILE = %s' % pid_file)
    logger.debug('Config  = %s' % configuration_file)
    global component_manager
    global context
    component_manager = ComponentManagerDaemon(logger, configuration_file)

    context = DaemonContext(
        working_directory=working_directory,
        pidfile=PIDLockFile(pid_file),
        files_preserve=[fh.stream],
        umask=066,
        signal_map={signal.SIGTERM: shutdown}
    )

    logger.debug('Running Daemon')
    try:
        with context:
            component_manager.run()
    except Exception, err:
        logger.exception(err.message)
    logger.debug('Daemon terminated')


if __name__ == '__main__':
    daemon()
