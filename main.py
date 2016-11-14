#!/usr/bin/env python3
"""Handles command line argument parsing and environment variables."""
import argparse
import logging
import os

from oblong import database, server

HEROKU_PORT = int(os.getenv('PORT', 5000))

database.init(os.getenv("DATABASE_URL"))

parser = argparse.ArgumentParser(description='Oblong eexpertise mining.')
parser.add_argument('--host', metavar='IP', default='localhost',
        help='The host to pass to `Flask.run()`')
parser.add_argument('--port', metavar='PORT', type=int,
        default=HEROKU_PORT, help='The port to pass to `Flask.run()`')
parser.add_argument('--log-file', metavar='FILE',
        help='The file to log to.')
parser.add_argument('--log-level', default='INFO',
        choices=['critical', 'error', 'warning', 'info', 'debug'],
        help='The minimum level for displayed log messages.')
args = parser.parse_args()

kwargs = { 'level': getattr(logging, args.log_level.upper()) }
if args.log_file:
    kwargs['filename'] = args.log_file
logging.basicConfig(**kwargs)

server.app.run(host=args.host, port=args.port)
