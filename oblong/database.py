"""A database for storing profiles and queries.

Attributes:
    engine (sqlalchemy.Engine): The database engine. You shouldn't need
        to interact with this object.
    session (sqlalchemy.scoped_session): A thread-safe session that
        can be used to access the database, see above examples.

Examples:
    Intialise the module:

    >>> init("postgresql://postgres:oblong@localhost/postgres")

    Create a profile:

    >>> p = Profile(name='John', keywords={'hello': 7, 'world': 1})
    >>> session.add(p)
    >>> session.commit()

    Retrieve profiles:

    >>> session.query(Profile).filter(Profile.name == 'John').all()
    [<Profile ... John>]
    >>> Profile.query.filter(Profile.name == 'John').all()
    [<Profile ... John>]
    >>> Profile.query.filter(Profile.keywords.has_key('hello')).all()
    [<Profile ... John>]

    Change a profile:

    >>> p = Profile.query.first()
    >>> p.name = 'John Smith'
    >>> p.keywords['face'] = 12
    >>> p.awards.append('An Award')
    >>> session.commit()

    Remove a profile:

    >>> p = Profile.query.first()
    >>> session.delete(p)
    >>> session.commit()

"""
from sqlalchemy import (create_engine, Table, Column,
    Enum, Integer, Text, ForeignKey)
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.dialects.postgresql import JSON, JSONB

__author__ = 'Blaine Rogers <br1314@ic.ac.uk>'

#: The database engine.
engine = None
#: A thread-safe session.
session = None
#: The declarative base class.
Base = declarative_base()
#: Enumeration type for query status.
Status = Enum("in_progress", "finished", "deleted", name="Status")

#: Association table for many-to-many link between queries and profiles.
query_association = Table(
    'query_association', Base.metadata,
    Column('query_id', Integer, ForeignKey('queries.id')),
    Column('profile_id', Integer, ForeignKey('profile.id'))
)

class Profile(Base):
    """Table to contain user profiles."""
    __tablename__ = 'profile'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    keywords = Column(MutableDict.as_mutable(JSONB))
    papers = Column(JSON)
    awards = Column(JSON)

    def __repr__(self):
        return ('<Profile {id:d} {name:s}>'
                .format(id=self.id, name=self.name))

class Query(Base):
    """Table to contain queries."""
    __tablename__ = 'queries'
    id = Column(Integer, primary_key=True)
    status = Column(Status)
    results = relationship(Profile, secondary=query_association)

    def __repr__(self):
        return ('<Query {id:d} {status:s}>'
                .format(id=self.id, status=self.status))

def init(connection_url):
    """Intialises the module by setting up an engine and session.
    
    Args:
        connection_url (str): The url of the database to connect to.
            From the `SQLAlchemy docs`_:
                
                The string form of the URL is 
                ``dialect[+driver]://user:password@host/dbname[?key=value..]``,
                where ``dialect`` is a database name such as ``mysql``,
                ``oracle``, ``postgresql``, etc., and ``driver`` the 
                name of a DBAPI, such as ``psycopg2``, ``pyodbc``, 
                ``cx_oracle``, etc. Alternatively, the URL can be an 
                instance of ``sqlalchemy.engine.url.URL``.

    .. _SQLAlchemy docs: http://docs.sqlalchemy.org/en/rel_1_1/core/engines.html?highlight=create_engine#sqlalchemy.create_engine

    """
    global Base, engine, session
    engine = create_engine(connection_url)
    session = scoped_session(sessionmaker(autocommit=False,
                                             autoflush=False,
                                             bind=engine))
    Base.query = session.query_property()
    Base.metadata.create_all(bind=engine)
