#!/usr/bin/env python3
"""Handles command line argument parsing and environment variables."""
import argparse
import os

import database
import server


DATABASE_URL = os.getenv("OBLONG_DATABASE_URL")
database.init(DATABASE_URL)

parser = argparse.ArgumentParser(description='Oblong eexpertise mining.')
parser.add_argument('--host', metavar='IP', default='localhost',
        help='The host to pass to `Flask.run()`')
parser.add_argument('--port', metavar='PORT', type=int,
        default=5000, help='The port to pass to `Flask.run()`')
args = parser.parse_args()

server.app.run(host=args.host, port=args.port)
