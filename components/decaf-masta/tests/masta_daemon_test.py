__author__ = 'krijan'

from decaf_masta.mastad import MastaDaemon
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
logger.addHandler(ch)

configuration_file = "./config/masta_local.cfg"

daemon = MastaDaemon(logger,configuration_file)
daemon.run()