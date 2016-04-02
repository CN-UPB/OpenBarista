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

import json
import sys

import argparse
import argcomplete
import yaml
import os.path
import logging
from decaf_cli import __version__
from decaf_cli import version_date
from decaf_cli.bunnyconnector import BunnyConnector

__author__ = "Andreas Krakau"
__date__ = "$08-oct-2015 11:48:24$"

CONFIGFILE = '/etc/decaf/cli.cfg'
LOGFILE = '/var/log/decaf/cli.log'


class ArgumentParserError(Exception):
    pass


class ThrowingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        print "Error: %s" % message
        print
        self.print_usage()
        print
        print "Type 'decaf-cli -h' for help"
        raise ArgumentParserError


def get_logger(log_file=LOGFILE):
    """
    Creates a new logger.

    :param log_file: The log file name.
    :return: A logger.
    """
    logger = logging.getLogger('DECaF-CLI')
    fh = logging.FileHandler(log_file)
    # fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)
    return logger


def load_configuration(configuration_file):
    """
    Loads the configuration from a file.

    :param configuration_file: The configuration file name.
    :return: A Dictionary which contains the configuration values.
    """
    result = dict()
    # config = {'rpc': {'url': 'amqp://fg-cn-decaf-head1.cs.upb.de:5672'}}
    # Set default config
    config = {'rpc': {'url': 'amqp://127.0.0.1'}}
    # Load config from file and overwrite default
    if os.path.isfile(configuration_file):
        try:
            f = open(configuration_file)
            config = yaml.safe_load(f)
            f.close()
        except yaml.YAMLError, err:
            if hasattr(err, 'problem_mark'):
                mark = err.problem_mark
                print(
                    "Error in configuration file at position: (%s:%s)" % (mark.line + 1, mark.column + 1))
            else:
                print("Error in configuration file: %s" % err.message)
    result['url'] = None
    if 'rpc' in config:
        if 'url' in config['rpc']:
            result['url'] = config['rpc']['url']
    return result


def call(args):
    """
    Calls a remote function over RabbitMQ

    :param args:
    :return:
    """
    if args.name and args.function:
        logger = get_logger()
        logger.debug('Loading configuration')
        config = load_configuration(CONFIGFILE)
        logger.debug('Configuration loaded')
        arguments = []
        keywordarguments = {}
        if args.json and len(args.arguments) > 0:
            keywordarguments = json.loads(' '.join(args.arguments))
        else:
            for arg in args.arguments:
                if "=" in arg:
                    arg = arg.split("=", 1)
                    keywordarguments[arg[0]] = arg[1]
                else:
                    arguments.append(arg)

        connector = BunnyConnector(config['url'], logger)
        logger.debug('Call %s.%s with %r and %r' % (args.name[0], args.function[0], arguments, keywordarguments))
        try:
            print "RESULT: {0}".format(connector.call(args.name[0], args.function[0], arguments, keywordarguments))
        except:
            del connector


def component_list(args):
    logger = get_logger()
    logger.debug('Loading configuration')
    config = load_configuration(CONFIGFILE)
    logger.debug('Configuration loaded')
    connector = BunnyConnector(config['url'], logger)
    print connector.call('decaf_componentmanager', 'component_list', [], {})


def cli():
    main_parser = ThrowingArgumentParser(description=' DECaF CLI')
    main_parser.add_argument('-v', '--version', action='version',
                             version='%(prog)s ' + __version__ + ' (' + version_date + ')')

    subparsers = main_parser.add_subparsers(help='commands')

    call_parser = subparsers.add_parser('call', help='call a function on a component')
    call_parser.add_argument('--json', action='store_true', help='args specified in json')
    call_parser.add_argument('name', nargs=1, help='component name')
    call_parser.add_argument('function', nargs=1, help='function name')
    call_parser.add_argument('arguments', nargs="*", help='function arguments')
    call_parser.set_defaults(func=call)

    component_list_parser = subparsers.add_parser('component-list', help='list available components')

    component_list_parser.set_defaults(func=component_list)

    argcomplete.autocomplete(main_parser)

    try:
        args = main_parser.parse_args()
        result = args.func(args)
        if result is not None:
            result = 0

    except KeyboardInterrupt:
        print 'Exiting decaf cli'
        result = -2
    except (SystemExit, ArgumentParserError):
        result = -3

    exit(result)

if __name__ == '__main__':
    cli()
