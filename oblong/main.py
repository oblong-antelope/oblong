#!/usr/bin/env python3
"""Handles command line argument parsing and environment variables."""
import argparse
import os

import database
import server

HEROKU_PORT = int(os.getenv('PORT', 5000))

database.init(os.getenv("DATABASE_URL"))

parser = argparse.ArgumentParser(description='Oblong eexpertise mining.')
parser.add_argument('--host', metavar='IP', default='localhost',
        help='The host to pass to `Flask.run()`')
parser.add_argument('--port', metavar='PORT', type=int,
        default=HEROKU_PORT, help='The port to pass to `Flask.run()`')
args = parser.parse_args()

server.app.run(host=args.host, port=args.port)
