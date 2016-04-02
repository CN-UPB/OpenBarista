__author__ = 'krijan'

from decaf_deployment.deploymentd import DeploymentDaemon
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
logger.addHandler(ch)

daemon = DeploymentDaemon(logger)
daemon.run()