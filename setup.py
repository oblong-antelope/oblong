#!/usr/bin/env python3
from setuptools import setup

setup( name='oblong'
     , version='0.3'
     , description='Backend server for Oblong text mining.'
     , install_requires=[ 'flask>=0.11'
                        , 'flask-cors'
                        , 'sqlalchemy>=1.1'
                        , 'psycopg2>=2.6.2'
                        , 'nltk>=3.1'
                        , 'rdflib'
                        ]
     , tests_require=[ 'testing.postgresql' ]
     )
