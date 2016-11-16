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

    >>> session.query(Profile).filter_by(name='John').all()
    [<Profile id=... name=John>]
    >>> Profile.query.filter_by(name='John').all()
    [<Profile id=... name=John>]
    >>> Keyword.query.filter_by(name='hello').one_or_none()
    <Keyword id=... name=hello>

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
        ARRAY, Enum, Integer, Float, Text, String, ForeignKey)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
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

def get_one_or_create(model, create_method='', create_method_kwargs=None, 
        **kwargs):
    """Attempts to get an object, or creates one if it doesn't exist.

    Code is cribbed from `here`_.

    Args:
        model (Base): The model to query.
        create_method (Callable): A method on the model that, when 
            supplied with the union of ``kwargs`` and 
            ``create_method_kwargs``, creates a new instance of the 
            model.
        create_method_kwargs (Dict[str, Any]): A dictionary that will
            be supplied along with ``kwargs`` to the ``create_method``.
        **kwargs: These arguements will be supplied to
            ``session.query(model).filter_by`` to select an instance of
            the model if one exists. If not, these will be passed to
            the ``create_method`` along with ``create_method_kwargs``.

    Returns:
        (model, bool) an instance of the model that matches the query,
        such that if one doesn't exist in the database it is created,
        and a boolean representing whether or not the object already
        existed.

    .. _here: http://skien.cc/blog/2014/02/06/sqlalchemy-and-race-conditions-follow-up/
    
    """
    try:
        return session.query(model).filter_by(**kwargs).one(), True
    except NoResultFound:
        kwargs.update(create_method_kwargs or {})
        created = getattr(model, create_method, model)(**kwargs)
        try:
            session.add(created)
            session.flush()
            return created, False
        except IntegrityError:
            session.rollback()
            return session.query(model).filter_by(**kwargs).one(), True

class ProfileKeywordAssociation(Base):
    __tablename__ = 'profile_keyword_association'
    left_id = Column(Integer, ForeignKey('profile.id'), primary_key=True)
    right_id = Column(Integer, ForeignKey('keyword.id'), primary_key=True)
    weight = Column(Float)

    profile = relationship('Profile', 
            backref=backref(
                'keywords_',
                collection_class=attribute_mapped_collection('keyword'),
                cascade='all, delete-orphan'
                )
            )
    keyword_ = relationship('Keyword', back_populates='profiles_')
    keyword = association_proxy('keyword_', 'name',
            creator=lambda name: get_one_or_create(Keyword, name=name)[0])

class Profile(Base):
    """Table to contain user profiles."""
    __tablename__ = 'profile'
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    #kw_associations = relationship(ProfileKeywordAssociation)
    #keywords = relationship(ProfileKeywordAssociation, back_populates='profile')
    keywords = association_proxy('keywords_', 'weight',
            creator=lambda k, v: ProfileKeywordAssociation(keyword=k, weight=v)
            )
    papers = Column(MutableList.as_mutable(ARRAY(Text)), default=[])
    awards = Column(MutableList.as_mutable(ARRAY(Text)), default=[])

    def __repr__(self):
        return '<Profile id={} name={}>'.format(self.id, self.name)

class Keyword(Base):
    """Table to contain keywords for profile lookup."""
    __tablename__ = 'keyword'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True)
    profiles_ = relationship(ProfileKeywordAssociation)
    profiles = association_proxy('profiles_', 'profile',
            creator=None)

    def __repr__(self):
        return '<Keyword id={} name={}>'.format(self.id, self.name)

class Query(Base):
    """Table to contain queries."""
    __tablename__ = 'queries'
    id = Column(Integer, primary_key=True)
    status = Column(Status)
    results = relationship(Profile, secondary=query_association)

    def __repr__(self):
        return '<Keyword id={} status={}>'.format(self.id, self.status)

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
