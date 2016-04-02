##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

import signal
import sys
from time import sleep
import os
import re
import logging
import traceback
from abc import abstractmethod
import yaml
from lockfile.pidlockfile import PIDLockFile

from service import Service
from decaf_utils_components import BasePlugin

__author__ = ''
__date__ = "$27-aug-2015 12:05:34$"

the_daemon = None
context = None


# --------------------------------------------------------------------------
# ----------------------- DEFAULT VALUES -----------------------------------
# --------------------------------------------------------------------------

PIDDIR = '/var/run/decaf/'
LOGFILE = '/var/log/decaf/{0}.log'
CONFIGFILE = '/etc/decaf/{0}.cfg'

AMPQ_URL = u"amqp://127.0.0.1:5672"


class BaseDaemon(Service):
    """
    Base class for a daemon process.

    The functionality is a bit similar (but not equal) to a generic class in Java.

    A daemon for a specific plugin is a subclass of this and specifies the class of the plugin which it is for.
    """

    __version__ = "0.1"

    __versiondate__ = "$27-aug-2015 12:05:34$"

    @abstractmethod
    def _before_connect(self):
        self.logger.debug('Daemon is about to connect...')
        pass

    @abstractmethod
    def _before_shutdown(self):
        self.logger.debug('Daemon is about to shutdown...')
        pass

    @abstractmethod
    def __init_plugin__(self, logger, config, **kwargs):
        pass

    def load_configuration(self, configuration_file):
        try:

            f = open(configuration_file, "r")
            # safe_load returns None if File is empty
            config = yaml.safe_load(f)
            f.close()
            return config
        except IOError:
            self.logger.error('Configfile %s not found' % configuration_file)
            self.dispose()
        except yaml.YAMLError, err:
            if hasattr(err, 'problem_mark'):
                mark = err.problem_mark
                self.logger.exception(
                    "Error in configuration file at position: (%s:%s)" % (mark.line + 1, mark.column + 1))
            else:
                self.logger.exception("Error in configuration file: %s" % err.message)
            self.dispose()

    def configure(self, config_yaml):

        if not config_yaml:
            config_yaml = {}

        # We will return this
        result = {}

        # Set some standard values
        result['log'] = {'level': logging.DEBUG}
        result['rpc'] = {'url': AMPQ_URL}

        # Step through the data in the config
        for key in config_yaml:
            if key == 'database':
                
                if 'mysql' in config_yaml['database']:
                    result["database"] = {}
                    result["database"]["type"] = 'mysql'
                    result["database"]["host"] = config_yaml['database']['mysql']['host']
                    result["database"]["port"] = config_yaml['database']['mysql']['port']
                    result["database"]["database"] = config_yaml['database']['mysql']['database']
                    result["database"]["user"] = config_yaml['database']['mysql']['user']
                    result["database"]["password"] = config_yaml['database']['mysql']['password']
                elif 'sqlite' in config_yaml['database']:
                    result["database"] = {}
                    result["database"]["type"] = 'sqlite'
                    result["database"]["file"] = config_yaml['database']['sqlite']['file']
                elif 'postgresql' in config_yaml['database']:
                    result["database"] = {}
                    result["database"]["type"] = 'postgresql'
                    result["database"]["host"] = config_yaml['database']['postgresql']['host']
                    result["database"]["port"] = config_yaml['database']['postgresql']['port']
                    result["database"]["database"] = config_yaml['database']['postgresql']['database']
                    result["database"]["user"] = config_yaml['database']['postgresql']['user']
                    result["database"]["password"] = config_yaml['database']['postgresql']['password']

            elif key == 'log':
                if 'level' in config_yaml['log']:
                    if config_yaml['log']['level'] == 'DEBUG':
                        result['log']['level'] = logging.DEBUG
                    elif config_yaml['log']['level'] == 'WARN':
                        result['log']['level'] = logging.WARN
                    elif config_yaml['log']['level'] == 'INFO':
                        result['log']['level'] = logging.INFO

            elif key == 'rpc':
                if 'url' in config_yaml['rpc']:
                    result['rpc']['url'] = config_yaml['rpc']['url']

            else:  # some attribute for that we have no standard handling
                result[key] = config_yaml[key]

        return result

    def run(self):

        configuration_file = CONFIGFILE.format(self.file_name)
        log_file = LOGFILE.format(self.file_name)

        try:
            # Configure logging
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.DEBUG)
            fh = logging.FileHandler(log_file)

            # create console handler with a higher log level
            ch = logging.StreamHandler()
            ch.setLevel(logging.ERROR)

            # create formatter and add it to the handlers
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            fh.setFormatter(formatter)
            ch.setFormatter(formatter)
            logger.addHandler(fh)
            logger.addHandler(ch)

        except BaseException as e:
            print "Error while setting up logger:", e
            sys.exit(3)

        self.logger = logger
        self.logger.debug('start deamon...')

        config_yaml = None
        if configuration_file:
            self.logger.debug('read config...')
            config_yaml = self.load_configuration(configuration_file)
        self.config = self.configure(config_yaml)

        self.plugin = self.__init_plugin__(self.logger, self.config)

        self.logger.debug('finished init...')

        self.logger.debug('now running with PID %d' % os.getpid())
        try:

            self._before_connect()

            self.plugin.connect(url=config_yaml['rpc']['url'])

            self.logger.debug('Plugin connected')

        except (KeyboardInterrupt, SystemExit):
            print('User interrupt: cleaning up...')
            self.dispose()
        except BaseException as e:
            print "Error while running daemon:", e
            self.logger.exception(e)
            self.dispose()
        except:
            traceback.print_exc()
            print "All is lost"
            self.dispose()

        self.logger.info("I'm sleepingzz...")
        if self.in_foreground:
            while True:
                sleep(64000)
        else:
            self.wait_for_sigterm()
            self.dispose()

    def dispose(self):
        self.logger.debug('Disposing the Daemon...')

        self.logger.debug('Shutting down...')
        self._before_shutdown()

        if hasattr(self, 'plugin') and self.plugin is not None:
            self.plugin.dispose()
            self.plugin = None

        self.logger.debug('Daemon is down now. Goodbye!')
        #sys.exit(0)

    def ___del__(self):
        self.logger.debug("Nooo don't delete me!")
        self.dispose()


def make_generic_deamon_class(plugin_class):

    class GenericDeamon(BaseDaemon):

        def __init_plugin__(self, logger, config, **kwargs):
            return plugin_class(logger, config, **kwargs)

        def _before_connect(self):
            super(GenericDeamon, self)._before_connect()

        def _before_shutdown(self):
            super(GenericDeamon, self)._before_shutdown()

    return GenericDeamon


def usage():
    print "usage: ", sys.argv[0], "[arguments]\n"
    print "Arguments:"
    print "  start"
    print "  fg (to start in foreground)"
    print "  stop"
    print "  restart"
    print "  status"
    return


def version(Deamonclass):
    print sys.argv[0], Deamonclass.__version__, '(' + Deamonclass.__version_date__ + ')'
    return


def start_daemon(daemon_class, file_name=None, command='fg'):
    """

    :param command:
    :param daemon_class: A subclass of BasicDaemon
    :param file_name:
    :return:
    """

    import sys

    if len(sys.argv) != 2 and not command:
        usage()

    #Python magic !!! Prefer commandline over paramter
    cmd = sys.argv[1].lower() or command

    try:
        global service
        service = daemon_class(file_name, pid_dir=PIDDIR)
        service.file_name = file_name
        service.in_foreground = False

        if cmd == 'start':
            print "Starting Service %s" % daemon_class.__name__
            service.start()
        elif cmd == 'stop':
            service.stop()
        elif cmd == 'restart':
            try:
                print 'stopping'
                service.stop()
            except BaseException as e:
                print e
            sleep(2)
            print 'starting...'
            service.start()
        elif cmd == 'fg':
            def signal_handler(signal, frame):
                print('User interrupt: cleaning up...')
                service.dispose()

                # release pid
                sys.exit(0)

            signal.signal(signal.SIGTERM, signal_handler)
            signal.signal(signal.SIGINT, signal_handler)

            # aquire pid
            #_PIDFile(os.path.join(pid_dir, name + '.pid')
            #PIDLockFile

            print 'starting class in foreground'
            service.in_foreground = True
            service.run()

        elif cmd == 'status':
            if service.is_running():
                print "Service is running."
            else:
                print "Service is not running."
        else:
            print 'Unknown command "%s".' % cmd
            usage()

    except BaseException as e:
        print "Exception:", e
        sys.exit(3)


def daemonize(plugin_class, file_name=None):
    """
    Starts an instance of the given class as background daemon

    :param plugin_class: A subclass of BasePlugin
    :param file_name: The name for the .cfg, .log and .pid files.
        Default is: "{0}d".format(_underscore_name(plugin_class.__name__))
         e.g. deploymentd.log
    :return:
    """

    if not file_name:
        file_name = "{0}d".format(_underscore_name(plugin_class.__name__))

    assert issubclass(plugin_class, BasePlugin)
    clazz = make_generic_deamon_class(plugin_class)
    start_daemon(clazz, file_name)
    pass


def _underscore_name(name):
    """
    converts CamelCase to camel_case

    Example:
    calculate_tablename('HTTPResponseCodeXYZ')
    'http_response_code_xyz'
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

