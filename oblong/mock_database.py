from collections.abc import MutableMapping, Sequence, MutableSequence
from functools import partial
import unittest.mock

session = None

class Column:
    def __init__(self, coltype, unique=False, default=None):
        self.coltype = coltype
        self.unique = unique
        self.default = default
        self._attr_name = '_Column__{}'.format(id(self))

    def __get__(self, obj, type=None):
        """Gets the column value."""
        if not hasattr(obj, self._attr_name):
            setattr(obj, self._attr_name, self.coltype(self.default))
        return getattr(obj, self._attr_name)

    def __set__(self, obj, value):
        """Sets the column value."""
        if self.unique:
            assert all(not getattr(o, self._attr_name) == value 
                       for o in obj.rows if o is not obj), 'uniqueness check'
        setattr(obj, self._attr_name, self.coltype(value))

class Base:
    def __init__(self, **kwargs):
        if 'id' in kwargs:
            raise AttributeError('cannot manually assign id')
            
        for k, v in kwargs.items():
            if self._has_column(k):
                setattr(self, k, v)
            else:
                raise AttributeError('table {} has no column {}'
                        .format(self.__class__.__name__, k))

        self.id = len(self.rows)
        self.rows.append(self)

    @classmethod
    def get(cls, uid):
        try:
            return cls.rows[uid]
        except IndexError:
            return None

    @classmethod
    def count(cls):
        return len(cls.rows)

    @classmethod
    def get_page(cla, page_no, size):
        return cls.rows[page * size : (page + 1) * size]

    @classmethod
    def _has_column(cls, name):
        return name in cls.__dict__ and isinstance(cls.__dict__[name], Column)

class ProfileKeywordAssociation(Base):
    rows = []
    weight = Column(float)
    def __init__(self, profile, keyword, weight):
        Base.__init__(self, weight=weight)
        self.profile = profile
        self.keyword = keyword

class KeywordDictColumn(Column):
    class KeywordDict(MutableMapping):
        def __init__(self, mapping):
            for k, v in mapping.items():
                self[k] = v

        def getmatches(self, key):
            def match(ass):
                return ass.profile is self.obj and ass.keyword.name == key
            return list(filter(match, ProfileKeywordAssociation.rows))

        def __getitem__(self, key):
            matches = self.getmatches(key)
            assert len(matches) == 1
            return matches[0].weight

        def __setitem__(self, key, value):
            value = float(value)
            matches = self.getmatches(key)
            if len(matches) == 1:
                matches[0].weight = value
            else:
                keyword, _ = get_one_or_create(Keyword, name=key)
                ProfileKeywordAssociation(self.obj, keyword, value)

        def __delitem__(self, key):
            matches = self.getmatches(key)
            assert len(matches) == 1
            ProfileKeywordAssociation.rows.remove(matches[0])

        def __iter__(self):
            def match(ass):
                return ass.profile is self.obj
            a = list(filter(match, ProfileKeywordAssociation.rows))
            return iter([ass.keyword.name for ass in a])

        def __len__(self):
            def match(ass):
                return ass.profile is self.obj
            return len(list(filter(match, ProfileKeywordAssociation.rows)))

        def __repr__(self):
            return repr({k: v for k, v in self.items()})

    def __init__(self):
        Column.__init__(self, coltype=self.KeywordDict, default={})

    def __get__(self, obj, type=None):
        d = Column.__get__(self, obj, type)
        d.obj = obj
        return d

    def __set__(self, obj, value):
        super().__set__(self, obj, value)
        getattr(obj, self._attr_name).obj = obj

class KeywordProfileColumn(Column):
    class ProfileList(Sequence):
        def __init__(self, init):
            assert init is None

        def getmatches(self):
            def match(ass):
                return ass.keyword is self.obj 
            return list(filter(match, ProfileKeywordAssociation.rows))

        def __getitem__(self, key):
            matches = self.getmatches()
            return matches[key].profile

        def __delitem__(self, key):
            matches = self.getmatches()
            ProfileKeywordAssociation.rows.remove(matches[key])

        def __len__(self):
            return len(self.getmatches())

        def __repr__(self):
            return repr(self.getmatches())

    def __init__(self):
        Column.__init__(self, coltype=self.ProfileList, default=None)

    def __get__(self, obj, type=None):
        d = Column.__get__(self, obj, type)
        d.obj = obj
        return d

    def __set__(self, obj, value):
        super().__set__(self, obj, value)
        getattr(obj, self._attr_name).obj = obj

class ProfilePublicationAssociation(Base):
    rows = []
    def __init__(self, profile, publication):
        self.profile = profile
        self.publication = publication

class ProfilePublicationColumn(Column):
    class PublicationList(MutableSequence):
        def __init__(self, init):
            for v in init:
                self.append(v)

        def getmatches(self):
            def match(ass):
                return ass.profile is self.obj 
            return list(filter(match, ProfilePublicationAssociation.rows))

        def __getitem__(self, key):
            matches = self.getmatches()
            return matches[key].publication

        def __setitem__(self, key, value):
            matches = self.getmatches()
            matches[key].publication = value
            
        def __delitem__(self, key):
            matches = self.getmatches()
            ProfilePublicationAssociation.rows.remove(matches[key])

        def insert(self, index, value):
            if not -len(self) <= index <= len(self):
                raise IndexError('out of bounds')

            ProfilePublicationAssociation(self.obj, None)

            matches = self.getmatches()
            for i, m in reversed(enumerate(matches[index + 1:])):
                m.publication = matches[i - 1].publication

            matches[index].publication = value

        def __len__(self):
            return len(self.getmatches())

        def __repr__(self):
            return repr(self.getmatches())

    def __init__(self):
        Column.__init__(self, coltype=self.PublicationList, default=None)

    def __get__(self, obj, type=None):
        d = Column.__get__(self, obj, type)
        d.obj = obj
        return d

    def __set__(self, obj, value):
        super().__set__(self, obj, value)
        getattr(obj, self._attr_name).obj = obj

class PublicationProfileColumn(Column):
    class ProfileList(MutableSequence):
        def __init__(self, init):
            for v in init:
                self.append(v)

        def getmatches(self):
            def match(ass):
                return ass.publication is self.obj 
            return list(filter(match, ProfilePublicationAssociation.rows))

        def __getitem__(self, key):
            matches = self.getmatches()
            return matches[key].profile

        def __setitem__(self, key, value):
            matches = self.getmatches()
            matches[key].profile = value
            
        def __delitem__(self, key):
            matches = self.getmatches()
            ProfilePublicationAssociation.rows.remove(matches[key])

        def insert(self, index, value):
            if not -len(self) <= index <= len(self):
                raise IndexError('out of bounds')

            ProfilePublicationAssociation(None, self.obj)

            matches = self.getmatches()
            for i, m in reversed(enumerate(matches[index + 1:])):
                m.profile = matches[i - 1].profile

            matches[index].profile = value

        def __len__(self):
            return len(self.getmatches())

        def __repr__(self):
            return repr(self.getmatches())

    def __init__(self):
        Column.__init__(self, coltype=self.ProfileList, default=None)

    def __get__(self, obj, type=None):
        d = Column.__get__(self, obj, type)
        d.obj = obj
        return d

    def __set__(self, obj, value):
        super().__set__(self, obj, value)
        getattr(obj, self._attr_name).obj = obj

class Profile(Base):
    rows = []
    id = Column(int)
    title = Column(str)
    firstname = Column(str)
    lastname = Column(str)
    initials = Column(str)
    alias = Column(str)
    email = Column(str)
    faculty = Column(str)
    department = Column(str)
    campus = Column(str)
    building = Column(str)
    room = Column(str)
    website = Column(str)

    keywords = KeywordDictColumn()
    publications = ProfilePublicationColumn()

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
    rows = []
    id = Column(int)
    name = Column(str, unique=True)
    profiles = KeywordProfileColumn()
    
    def __repr__(self):
        return '<Keyword id={} name={}>'.format(self.id, self.name)

    @classmethod
    def get(cls, name):
        matches = list(filter(lambda r: r.name == name, cls.rows))
        if len(matches) == 1:
            return matches[0]
        elif not matches:
            return None
        else:
            raise Exception('u wat m8')

class Publication(Base):
    rows = []
    id = Column(int)
    title = Column(str)
    abstract = Column(str)
    date = Column(str)
    authors = PublicationProfileColumn()

    def __repr__(self):
        title = self.title if len(self.title) > 20 else self.title[:17] + '...'
        return '<Publication id={} title={}>'.format(self.id, title)

def init(connection_url):
    """This is a dummy that sets the session to a mock."""
    session = unittest.mock.Mock()

def get_one_or_create(model, create_method='', create_method_kwargs=None,
        **kwargs):
    def filter_by(a, **kwargs):
        return all(getattr(a, k) == v for k, v in kwargs)

    matches = list(filter(partial(filter_by, **kwargs), model.rows))
    if len(matches) == 1:
        return matches[0], True
    else:
        kwargs.update(create_method_kwargs or {})
        created = getattr(model, create_method, model)(**kwargs)
        return created, False

def get_profiles_by_keywords(kwds):
    profiles = Profile.rows[:]

    searched_columns = [ (n, any(getattr(p, n) in kwds for p in profiles))
                         for n in [ 'firstname'
                                  , 'lastname'
                                  , 'department'
                                  , 'campus'
                                  , 'faculty'
                                  ]

    for col, exists in searched_columns:
        profiles = filter(lambda p: not exists or getattr(p, col) in kwds,
                          profiles)
    profiles = list(filter(lambda p: any(k in kwds for k in p.keywords),
                           profiles))
    weights = [sum(v for k, v in p.keywords.items() if k in kwds)
               for p in profiles]

    res = list(zip(profiles, weights))
    res.sort(lambda p: -p[1])

    return res

