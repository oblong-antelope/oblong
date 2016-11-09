"""A database for storing profiles and queries.

Attributes:
    engine (sqlalchemy.Engine): The database engine. You shouldn't need
        to interact with this object.
    db_session (sqlalchemy.scoped_session): A thread-safe session that
        can be used to access the database, see above examples.

Examples:
    Create a profile:

    >>> p = Profile(name='John', keywords={'hello': 7, 'world': 1})
    >>> db_session.add(p)
    >>> db_session.commit()

    Retrieve profiles:

    >>> db_session.query(Profile).filter(Profile.name == 'John').all()
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
    >>> db_session.commit()

    Remove a profile:

    >>> p = Profile.query.first()
    >>> db_session.delete(p)
    >>> db_session.commit()

"""
from sqlalchemy import (create_engine, Table, Column,
    Enum, Integer, Text, ForeignKey)
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.dialects.postgresql import JSON, JSONB

__author__ = 'Blaine Rogers <br1314@ic.ac.uk>'

#: Enumeration type for query status.
Status = Enum("in_progress", "finished", "deleted", name="Status")

#: The database engine.
engine = create_engine('postgresql://postgres:oblong@localhost/postgres')

#: A thread-safe session.
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

#: The declarative base class.
Base = declarative_base()
Base.query = db_session.query_property()

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

Base.metadata.create_all(bind=engine)
