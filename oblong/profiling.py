"""Algorithms that profile users based on paper metadata."""
import datetime
from os import linesep
import os.path
from time import gmtime

from nltk import pos_tag, word_tokenize, RegexpParser
from nltk.stem import WordNetLemmatizer
from sqlalchemy.orm.exc import NoResultFound

from . import database as db

from .ontology import *

onto = Ontology() #import the ACM ontology

#find the names of people, departments, campuses and faculties in the database
names    = Set([w.lower() for w in db.session.name.query()])
deps     = Set([w.lower() for w in db.session.department.query()])
campuses = Set([w.lower() for w in db.session.campus.query()])
facs     = Set([w.lower() for w in db.session.faculty.query()])

def fulfill_query(text):
    """Fulfills a query by searching the database.

    Args:
        text (str): This string will be searched for keywords,
            and profiles containing those keywords will be returned.

    """
    global names, deps, facs, campuses

    profiles = db.Profile.query

    print("text of query: ", text)

    keywords = get_keywords(text)
    print(keywords)

    #check for names in keywords
    name = ''
    dep = ''
    camp = ''
    fac = ''
    for k in keywords:
        if k.lower() in names:
            name = k
        if k.lower() in deps:
            dep = k
        if k.lower() in campuses:
            camp = k
        if k.lower() in facs:
            fac = k

    if name:
        profiles = profiles.filter_by(name=name)
    if camp:
        profiles = profiles.filter_by(campus=camp)
    if dep:
        profiles = profiles.filter_by(department=dep)
    if fac:
        profiles = profiles.filter_by(faculty=fac)

    for k in keywords:
        profiles = profiles.filter(db.Profile.keywords_.any(
                db.ProfileKeywordAssociation.keyword == k
                ))

    results = profiles.all()
    def sort_function(profile):
        for k in keywords:
            print(dict(profile.keywords))
        return sum(profile.keywords[k] for k in keywords)
    for p in results:
        print(p.firstname, sort_function(p))
    results.sort(key=sort_function, reverse=True) 
    return results

def update_authors_profiles(title, abstract, authors, date):
    """Updates the profiles of the authors of a new paper.

    Args:
        title (str): The title of the new paper.
        authors: Data about the authors of the paper.
        date (str): The date of the new paper in XML datetime format.

    """
    #date = datetime.date(int(date[:4]), int(date[5:7]), int(date[8:10]))
    publication, _ = db.get_one_or_create(db.Publication, 
            create_method_kwargs={ 'abstract': abstract, 'date': date },
            title=title)

    keywords = get_keywords(title)
    if abstract:
        keywords += get_keywords(abstract)
    
    #create lists of concepts from the ontology
    keyword_classes = [onto.find_superclasses(w) for w in keywords]

    #create a list of weightings of keywords
    weightings = {}
    for kw_class in keyword_classes:
        dist = 0
        for word in kw_class:
            weightings[word] = weighting(word, keywords, date, dist)
            dist += 1

    keywords = [w for c in keyword_classes for w in c] #flatten keyword_classes

    for author in authors:
        profile, _ = db.get_one_or_create(db.Profile, 
                create_method_kwargs={ 'title': author['name']['title']
                                     , 'initials': author['name']['initials']
                                     , 'alias': author['name']['alias']
                                     , 'email': author['email']
                                     , 'department': author['department']
                                     , 'campus': author['campus']
                                     , 'building': author['building']
                                     , 'room': author['room']
                                     , 'website': author['website']
                                     },
                firstname=author['name']['first'],
                lastname=author['name']['last'],
                faculty=author['faculty'])
        
        #update weightings
        for word in keywords:
            if word not in profile.keywords:
                profile.keywords[word] = 0
            profile.keywords[word] += weightings[word]

        profile.publications.append(publication)
    db.session.commit()

def get_keywords(text):
    """Gets the keywords from a text excerpt.

    The text is split into words and the boring words are removed.

    Args:
        text (str): The text to get keywords from.

    Returns:
        (Sequence[str]): The keywords of the text.

    """
    tokens = [word.lower() for word in word_tokenize(text)]

    # tag words as verb, noun etc
    tagged_words = pos_tag(tokens)

    # retrieve list of boring words from file
    basedir = os.path.dirname(__file__)
    with open(os.path.join(basedir, 'data', 'stopwords.txt'), 'r') as f:
        stopwords = [line.rstrip(linesep) for line in f]

    # NLTK Chunking - detects noun phrases and phrases of form verb noun or adj noun
    patterns = """NP: {<JJ>*<NN><NNS>}
                      {<JJR><NNS>}
                      {<JJ>*<NNS>}
                      {<NN><NNS>} 
                      {<JJ><NNS>}
                      {<JJ>*<NN>*}
                      {<NN>*}
                      {<NNS>*}"""
    chunker = RegexpParser(patterns)
    chunks = chunker.parse(tagged_words)

    #these are the phrases we want, as lists within a list
    validphrases = []
    for t in chunks.subtrees():
        if t.label() == 'NP':
            validphrases.append([x for x,y in t.leaves()])

    #turning lists within lists into actual noun phrases i.e [[radiation], [breast,cancer]] becomes [radiation, breast cancer]
    #sorry for my horrible code
    #trees suck
    lemmatizables = []
    for sublist in validphrases:
        lemmatizables.append(' '.join(sublist))

    lemmatizer = WordNetLemmatizer()
    lems = [lemmatizer.lemmatize(x) for x in lemmatizables]

    #removing stopwords after lemmatizing
    lems = filter(lambda lem: lem not in stopwords, lems)

    return tuple(lems)

'''def get_lemma_pos(tag):
    """Magic function, speak to Aran Dhaliwal.""" Not needed right now
    mapping = { 'J': 'a'
              , 'V': 'v'
              , 'N': 'n'
              , 'R': 'r'
              }
    return mapping.get(tag[0], 'n')'''

def weighting(word, words, date, distance=0):
    """Weights the importance of a keyword.

    The functions used currently are linear deprecation up to a time gap
    of fifty years and ontology distance of ten layers.

    Parameters:
        FUNC_D (Callable[[int], Number]): Function to produce a weighting
            given time diff in years.
        CUTOFF_D (int): lowest time diff after which the lowest weighting
            will be given.
        BASE_D (Number): the lowest possible weighting (time diff).
        FUNC_DS (Callable[[int], Number]): Function to produce a weighting
            given distance in levels of the ontology.
        CUTOFF_DS (int): lowest distance after which the lowest weighting
            will be given.
        BASE_DS (Number): the lowest possible weighting (distance).

    Args:
        word (str): The word to weight.
        words (Sequence[str]): All keywords in the text.
        date (str): Date the paper was written, in XML format.
        distance (int): The distance of this concept from the original.

    Returns:
        (int): a number representing how important this occurence of
        the word is.

    """
    CUTOFF_D = 50
    BASE_D = .5
    def FUNC_D(d): return -.09 * d + 5 if f <= CUTOFF_D else BASE_D

    CUTOFF_DS = 10
    BASE_DS = .5
    def FUNC_DS(d): return -.45 * d + 5 if f <= CUTOFF_DS else BASE_DS

    year = int(date[:4])
    current_year = gmtime()[0]
    time_diff = current_year - year
    return FUNC_D(time_diff) + FUNC_DS(distance)

def update_names_and_orgs():
    """Updates the names, fauclties, departments and campuses sets
    """
    global names, deps, campuses, facs
    names    = Set([w.lower() for w in db.session.name.query()])
    deps     = Set([w.lower() for w in db.session.department.query()])
    campuses = Set([w.lower() for w in db.session.campus.query()])
    facs     = Set([w.lower() for w in db.session.faculty.query()])
