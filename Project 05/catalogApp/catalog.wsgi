#!/usr/bin/python
import logging, sys

logging.basicConfig(stream=sys.stderr)

from application import app as application
import config

application.secret_key = config.SECRET_KEY