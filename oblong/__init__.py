"""Oblong back-end webserver.

Fields submissions of papers from various scrapers, and requests from
various front ends.

"""
__version__ = 0.2
__authors__ = [ 'Aran Dhaliwal <aran.dhaliwal14@imperial.ac.uk>'
              , 'Blaine Rogers <blaine.rogers14@imperial.ac.uk>'
              , 'Jonathan Sutton <jonathan.sutton14@imperial.ac.uk>'
              , 'Mickey Li <mickey.li14@imperial.ac.uk>'
              , 'Peng Peng <peng.peng14@imperial.ac.uk>'
              , 'Zichen Liu <zichen.liu14@imperial.ac.uk>'
              ]
__status__ = 'Development'

from .database import init as db_init
from .server import app

def init(database_url):
    db_init(database_url)

def run(*args, **kwargs):
    app.run(*args, **kwargs)
