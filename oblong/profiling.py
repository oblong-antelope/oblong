"""Algorithms that profile users based on paper metadata."""
import datetime
from os import linesep
import os.path
from time import gmtime

from nltk import pos_tag, word_tokenize, RegexpParser
from nltk.stem import WordNetLemmatizer
from sqlalchemy.orm.exc import NoResultFound

from . import database as db


def fulfill_query(text):
    """Fulfills a query by searching the database.

    Args:
        text (str): This string will be searched for keywords,
            and profiles containing those keywords will be returned.

    """
    profiles = db.Profile.query

    print("text of query: ", text)

    keywords = get_keywords(text)
    print(keywords)
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
    weightings = dict((w, weighting(w, keywords, date)) for w in keywords)

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

def weighting(word, words, date):
    """Weights the importance of a keyword.

    The function used currently is linear deprecation up to a time gap
    of fifty years.

    Parameters:
        FUNC (Callable[[int], Number]): Function to produce a weighting
            given time diff in years.
        CUTOFF (int): lowest time diff after which the lowest weighting
            will be given.
        BASE (Number): the lowest possible weighting.

    Args:
        word (str): The word to weight.
        words (Sequence[str]): All keywords in the text.
        date (str): Date the paper was written, in XML format.

    Returns:
        (int): a number representing how important this occurence of
        the word is.

    """
    def FUNC(d): return -.09 * d + 5
    CUTOFF = 50
    BASE = .5

    year = int(date[:4])
    current_year = gmtime()[0]
    time_diff = current_year - year
    return FUNC(time_diff) if time_diff <= CUTOFF else BASE
