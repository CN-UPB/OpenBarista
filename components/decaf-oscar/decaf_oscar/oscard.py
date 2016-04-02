#!/usr/bin/env python

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
# from .model.database import Database


__author__ = "Andreas Krakau"
__date__ = "$20-oct-2015 12:25:08$"

PIDFILE = '/var/run/decaf/oscard.pid'
LOGFILE = '/var/log/decaf/oscard.log'
CONFIGFILE = '/etc/decaf/oscard.cfg'

oscar = None
context = None


class OscarDaemon:
    def __init__(self, logger, configuration_file=CONFIGFILE):
        self.logger = logger
        self.configuration_file = configuration_file
        self.config = self.load_configuration()
        self.logger.setLevel(self.config['log']['level'])
        # self.db = None
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
        # self.db = Database(self.config["database"])
        self.logger.debug('Create BunnyConnector')
        self.bunny_connector = BunnyConnector(self.config['rpc']['url'], self.logger)
        while self.running:
            time.sleep(80460)

    def __del__(self):
        self.dispose()

    def dispose(self):
        self.logger.debug('Terminating Oscar...')
        if self.running:
            self.running = False

            if self.bunny_connector is not None:
                self.bunny_connector.dispose()
                del self.bunny_connector
                self.bunny_connector = None

            sys.exit()


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
    global oscar
    oscar.logger.debug(
        'Received signal %s (%s)' % (signal_number, (v for v, k in signal.__dict__.items() if
                                     v.startswith('SIG') and not v.startswith('SIG_') and k == signal_number).next()))
    oscar.logger.debug('Shutting down...')
    oscar.dispose()


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
    logger = logging.getLogger('Oscar')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(log_file)
    logger.addHandler(fh)

    logger.info('Starting oscar daemon')
    logger.debug('PIDFILE = %s' % pid_file)
    logger.debug('Config  = %s' % configuration_file)

    global oscar
    global context
    oscar = OscarDaemon(logger, configuration_file)
    context = DaemonContext(
        working_directory=working_directory,
        pidfile=PIDLockFile(pid_file),
        files_preserve=[fh.stream],
        umask=066,
        signal_map={signal.SIGTERM: shutdown}
    )

    with context:
        oscar.run()


if __name__ == '__main__':
    daemon()
