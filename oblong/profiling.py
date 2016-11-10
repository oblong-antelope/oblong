"""Algorithms that profile users based on paper metadata."""
from os import linesep
import os.path
from time import gmtime

from nltk import pos_tag, word_tokenize
from nltk.stem import WordNetLemmatizer
from sqlalchemy.orm.exc import NoResultFound

import database as db


def fulfill_query(query, name=None, expertise=None):
    """Fulfills a query by searching the database.

    Args:
        query (database.Query): The query to fulfill.
        name (str): Only profiles with this name will be returned.
        expertise (str): This string will be searched for keywords,
            and profiles containing those keywords will be returned.

    """
    if not (name or expertise):
        query.status = "finished"
        db.session.commit()
        return

    profiles = db.Profile.query

    if name:
        profiles = profiles.filter(db.Profile.name == name)

    if expertise:
        keywords = get_keywords(expertise)
        keywords = '{{"{}"}}'.format('","'.join(keywords))
        profiles = profiles.filter(db.Profile.keywords.has_any(keywords))
    
    query.results = profiles.all()
    query.status = "finished"
    db.session.commit()

def update_authors_profiles(title, author_names, date):
    """Updates the profiles of the authors of a new paper.

    Args:
        title (str): The title of the new paper.
        author_names (Sequence[str]): The names of the authors of the
            new paper.
        date (str): The date of the new paper in XML datetime format.

    """
    keywords = get_keywords(title)
    for name in author_names:
        try:
            profile = db.Profile.query.filter(db.Profile.name == name).one()
        except NoResultFound:
            profile = db.Profile(name=name, keywords={}, papers=[], awards=[])
            db.session.add(profile)
        
        for word in keywords:
            if word not in profile.keywords:
                profile.keywords[word] = 0
            profile.keywords[word] += weighting(word, keywords, date)

        profile.papers.append(title)
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
    patterns = """NP: {<VBG>*?<NN>*}
                      {<VBG>*?<NNS>*}
                      {<JJ>*?<NN>*}
                      {<JJ>*?<NNS>*}
                      {<JJR>*?<NN>*}
                      {<JJR>*?<NNS>*}
                      {<VBD>*?<NN>*}
                      {<VBD>*?<NNS>*}"""  
    chunker = nltk.RegexpParser(patterns)
    chunks = chunker.parse(taggedwords)

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
    return [lemmatizer.lemmatize(x) for x in lemmatizables if x not in stopwords]

 

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
