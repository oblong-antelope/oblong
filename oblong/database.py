"""A database for storing profiles and queries.

Attributes:
    engine (sqlalchemy.Engine): The database engine. You shouldn't need
        to interact with this object.
    session (sqlalchemy.scoped_session): A thread-safe session that
        can be used to access the database, see above examples.

Examples:
    Intialise the module:

    >>> import testing.postgresql
    >>> postgresql = testing.postgresql.Postgresql()
    >>> init(postgresql.url())

    Create a profile:

    >>> p = Profile(title='Mr', firstname='John', lastname='Smith',
    ...             keywords={'hello': 7, 'world': 1})
    >>> session.add(p)
    >>> session.commit()

    Retrieve profiles:

    >>> session.query(Profile).filter_by(firstname='John').all()
    [<Profile id=... name=Mr John Smith>]
    >>> Profile.query.filter_by(firstname='John').all()
    [<Profile id=... name=Mr John Smith>]
    >>> Keyword.query.filter_by(name='hello').one_or_none()
    <Keyword id=... name=hello>

    Change a profile:

    >>> p = Profile.query.first()
    >>> p.firstname = 'Harry'
    >>> p.keywords['face'] = 12
    >>> session.commit()

    Remove a profile:

    >>> p = Profile.query.first()
    >>> session.delete(p)
    >>> session.commit()

    >>> session.remove()
    >>> postgresql.stop()

"""
from sqlalchemy import (create_engine, Table, Column, 
        Enum, Integer, Float, Text, String, Date, ForeignKey,
        func, exists, desc, or_)
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.orm.exc import (NoResultFound, MultipleResultsFound)
from sqlalchemy.dialects.postgresql import JSON, JSONB

import operator
from functools import reduce

__author__ = 'Blaine Rogers <br1314@ic.ac.uk>'

#: The database engine.
engine = None
#: A thread-safe session.
session = None
#: The declarative base class.
Base = declarative_base()
Base.get = classmethod(lambda cls, uid: cls.query.get(uid))
Base.count = classmethod(lambda cls: cls.query.count())
Base.get_page = classmethod(lambda cls, page_no, size: \
        cls.query.slice(page_no * size, (page_no + 1) * size))

def find(cls, **kwargs):
    try:
        return cls.query.filter_by(**kwargs).all()
    except InvalidRequestError:
        raise AttributeError('at least one of ' + str(list(kwargs.keys()))
                + ' is not a valid field of ' + cls.__name__)

Base.find = classmethod(find)

#: Enumeration type for query status.
Status = Enum("in_progress", "finished", "deleted", name="Status")

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

#: Association table for many-to-many link between papers and profiles.
profile_publication_association = Table(
    'profile_publication_association', Base.metadata,
    Column('profile_id', Integer, ForeignKey('profile.id')),
    Column('publication_id', Integer, ForeignKey('publication.id'))
)

class ProfileKeywordAssociation(Base):
    __tablename__ = 'profile_keyword_association'
    left_id = Column(Integer, ForeignKey('profile.id'), primary_key=True)
    right_id = Column(Integer, ForeignKey('keyword.id'), primary_key=True)
    weight = Column(Float)

    profile = relationship('Profile', 
            backref=backref(
                'keywords_',
                collection_class=attribute_mapped_collection('keyword'),
                cascade='all, delete'
                )
            )
    keyword_ = relationship('Keyword', 
            back_populates='profiles_',
            cascade='all, delete')
    keyword = association_proxy('keyword_', 'name',
            creator=lambda name: get_one_or_create(Keyword, name=name)[0])

class Profile(Base):
    """Table to contain user profiles."""
    __tablename__ = 'profile'
    id = Column(Integer, primary_key=True)
    title = Column(String(20))
    firstname = Column(String(80))
    lastname = Column(String(80))
    initials = Column(String(20))
    alias = Column(String(80))
    email = Column(String(80))
    faculty = Column(String(80))
    department = Column(String(80))
    campus = Column(String(80))
    building = Column(String(80))
    room = Column(String(80))
    website = Column(String(160))

    keywords = association_proxy('keywords_', 'weight',
            creator=lambda k, v: ProfileKeywordAssociation(keyword=k, weight=v)
            )
    publications = relationship('Publication',
            secondary=profile_publication_association,
            back_populates='authors',
            cascade='all, delete')

    @property
    def name(self):
        return { 'title': self.title
               , 'first': self.firstname
               , 'last': self.lastname
               , 'initials': self.initials
               , 'alias': self.alias
               }

    @name.setter
    def name(self, value):
        if hasattr(value, '__getitem__'):
            self.title = value['title']
            self.firstname = value['first']
            self.lastname = value['last']
            self.initials = value['initials']
            self.alias = value['alias']
        elif isinstance(value, str):
            raise ValueError('String name parsing not yet implemented.')
        else:
            raise ValueError('name must be dict or string')

    def __repr__(self):
        name = "{} {} {}".format(self.title, self.firstname, self.lastname)
        return '<Profile id={} name={}>'.format(self.id, name)

class Keyword(Base):
    """Table to contain keywords for profile lookup."""
    __tablename__ = 'keyword'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True)
    profiles_ = relationship(ProfileKeywordAssociation,
            cascade='all, delete, delete-orphan')
    profiles = association_proxy('profiles_', 'profile',
            creator=None)

    def __repr__(self):
        return '<Keyword id={} name={}>'.format(self.id, self.name)

class Publication(Base):
    __tablename__ = 'publication'
    id = Column(Integer, primary_key=True)
    title = Column(Text)
    abstract = Column(Text)
    date = Column(Date)
    authors = relationship('Profile',
            secondary=profile_publication_association,
            back_populates='publications',
            cascade='all, delete')

    def __repr__(self):
        title = self.title if len(self.title) > 20 else self.title[:17] + '...'
        return '<Publication id={} title={}>'.format(self.id, title)

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
                                          expire_on_commit=False,
                                          bind=engine))
    Base.query = session.query_property()
    Base.metadata.create_all(bind=engine)

def get_profiles_by_keywords(keywords, page_no, page_size):
    """Gets a list of profiles that have any of the keywords.

    The weighting of a profile is calculated as the sum of the
    weghtings of the links between the profile and any relevant
    keywords.

    Args:
        keywords (Sequence[str]): The keywords to search for.

    Returns:
        (int, List[Tuple[Profile, float]]): The number of results
        and a list of profiles and weightings, 
        sorted by weighting in descending order, corresponding to
        the requested page.

    """
    keywords = [k.lower() for k in keywords]

    weight_sum = (func
                 .sum(ProfileKeywordAssociation.weight)
                 .label('weight_sum')
                 )

    searched_columns = [ Profile.firstname
                       , Profile.lastname
                       , Profile.department
                       , Profile.campus
                       , Profile.faculty
                       ]

    searched_columns = [func.lower(s) for s in searched_columns]

    q = (session.query(Profile, weight_sum)
        .join(ProfileKeywordAssociation)
        .join(Keyword)
        )

    notkeywords = set()
    cond = None
    for col in searched_columns:
        matches = session.query(col).filter(col.in_(keywords)).distinct().all()
        matches = [m[0] for m in matches]
        notkeywords |= set(matches)
        if matches:
            if cond is None:
                cond = col.in_(matches)
            cond |= col.in_(matches)
    
    if cond is not None:
        q = q.filter(cond)

    for k in notkeywords:
        keywords.remove(k)

    if keywords:
        q = q.filter(or_(*[Keyword.name.like("%"+k+"%") for k in keywords]))

    q = q.group_by(Profile.id).order_by(desc('weight_sum'))
    count = q.count()
    return count, q.slice(page_no * page_size, (page_no + 1) * page_size)
