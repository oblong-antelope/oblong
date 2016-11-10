#!/usr/bin/env python3
"""Handles command line argument parsing and environment variables."""
import argparse
import os
import urlparse

import database
import server

HEROKU_PORT = int(os.environ.get('PORT', 5000))

urlparse.uses_netloc.append("postgres")
DB_URL = urlparse.urlparse(os.environ["DATABASE_URL"])

database.init(DB_URL.hostname)

parser = argparse.ArgumentParser(description='Oblong eexpertise mining.')
parser.add_argument('--host', metavar='IP', default='localhost',
        help='The host to pass to `Flask.run()`')
parser.add_argument('--port', metavar='PORT', type=int,
        default=HEROKU_PORT, help='The port to pass to `Flask.run()`')
args = parser.parse_args()

server.app.run(host=args.host, port=args.port)
