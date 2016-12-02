#!/usr/bin/env python3
from setuptools import setup

setup( name='oblong'
     , packages=['oblong']
     , version='0.3'
     , description='Backend server for Oblong text mining.'
     , install_requires=[ 'flask>=0.11'
                        , 'flask-cors'
                        , 'sqlalchemy>=1.1'
                        , 'psycopg2>=2.6.2'
                        , 'nltk>=3.1'
                        , 'rdflib'
                        ]
     , tests_require=[ 'testing.postgresql'
                     , 'coverage'
                     ]
     , dependency_links=\
             [ # don't use the version of testing.postgresql in PyPI
               # because they haven't merged Windows support from here yet
               ('git+https://github.com/adelosa/testing.postgresql'
                '@fix-windows-support#egg=testing.postgresql')
             ]
     , setup_requires = ['nose']
     )
