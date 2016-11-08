#!/usr/bin/python
# -*- coding: utf8 -*-
from nltk import pos_tag, word_tokenize
from nltk.stem import WordNetLemmatizer
import string
import collections
import utils
import ast
from handlers import database_handlers as dbh

#Francesca Toni's publications from 2016
papers = [ {"title"   : "Argumentation-based multi-agent decision making with privacy preserved",
            "authors" : "Y. Gao, F. Toni, H. Wang, and F. Xu",
            "date"    : "2016"},
           {"title"   : "On the interplay between games, argumentation and dialogues",
            "authors" : "X. Fan and F. Toni",
            "date"    : "2016"},
           {"title"   : "Discontinuity-free decision support with quantitative argumentation debates",
            "authors" : "A. Rago, F. Toni, M. Aurisicchio, and P. Baroni",
            "date"    : "2016"},
           {"title"   : "Abstract argumentation for case-based reasoning",
            "authors" : "K. Cyras, K. Satoh, and F. Toni",
            "date"    : "2016"},
           {"title"   : "ABA+: assumption-based argumentation with preferences",
            "authors" : "K. Cyras and F. Toni",
            "date"    : "2016"},
           {"title"   : "Properties of ABA+ for non-monotonic reasoning",
            "authors" : "K. Cyras and F. Toni",
            "date"    : "2016"},
           {"title"   : "Smarter electricity and argumentation theory",
            "authors" : "M. Makriyiannis, T. Lung, R. Craven, F. Toni, and J. Kelly",
            "date"    : "2016"},
           {"title"   : "Online Argumentation-Based Platform for Recommending Medical Literature",
            "authors" : "A. Mocanu, X. Fan, F. Toni, M. Williams, and J. Chen",
            "date"    : "2016"},
           {"title"   : "Justifying Answer Sets using Argumentation",
            "authors" : "C. Schulz, F. Toni",
            "date"    : "2016"},
           {"title"   : "Argument Graphs and Assumption-Based Argumentation",
            "authors" : "R. Craven and F. Toni",
            "date"    : "2016"}
         ]


papers3 = [ {"title"   : "Argumentation-based multi-agent decision making with privacy preserved",
            "authors" : "F. Toni",
            "date"    : "2016"},
           {"title"   : "On the interplay between games, argumentation and dialogues",
            "authors" : "F. Toni",
            "date"    : "2016"},
           {"title"   : "Discontinuity-free decision support with quantitative argumentation debates",
            "authors" : "F. Toni",
            "date"    : "2016"},
           {"title"   : "Abstract argumentation for case-based reasoning",
            "authors" : "F. Toni",
            "date"    : "2016"},
           {"title"   : "ABA+: assumption-based argumentation with preferences",
            "authors" : "F. Toni",
            "date"    : "2016"},
           {"title"   : "Properties of ABA+ for non-monotonic reasoning",
            "authors" : "F. Toni",
            "date"    : "2016"},
           {"title"   : "Smarter electricity and argumentation theory",
            "authors" : "F. Toni",
            "date"    : "2016"},
           {"title"   : "Online Argumentation-Based Platform for Recommending Medical Literature",
            "authors" : "F. Toni",
            "date"    : "2016"},
           {"title"   : "Justifying Answer Sets using Argumentation",
            "authors" : "F. Toni",
            "date"    : "2016"},
           {"title"   : "Argument Graphs and Assumption-Based Argumentation",
            "authors" : "F. Toni",
            "date"    : "2016"}
         ]


remove = ['for', 'and', 'a', 'the', 'with', 'of', 'using', 'on','between','based','non',',','.',':',';'] #boring stuff to get rid of

def augment_profile(paper):
    """Given a single paper, augments the author of that paper.

       Creates or refines the profiles of all authors of the paper
       in the profile database.

       Args:
           paper (dict): a single paper of which to augment the author
              the paper will be of the format:
                 {'authors':['Toni F.'],
                  'title':'Paper title',
                  'date':'2016-11-27T14:27:34.35+00:00'}
    """
    print("INSERTING PAPER", paper)
    word_list = split_title(paper['title'])
    authors = split_authors(paper['authors'])
    date = paper['date']
    for author in authors:
        augment_author(author, word_list, date)

def split_authors(authors):
    """Produces a list of strings containing the authors' names.

       Args:
           authors (string): the authors' names

       Returns:
           author_list (list): a list of author names
    """
    split = authors.split(', ')
    author_list = split[:-1]
    author_list.extend(author for author in split[-1].split('and ') if author != '')
    return author_list

def get_lemma_pos(tag):  #needed to for part of speech tagging for lemmatizer

    if tag.startswith('J'):
        return 'a'
    elif tag.startswith('V'):
        return 'v'
    elif tag.startswith('N'):
        return 'n'
    elif tag.startswith('R'):
        return 'r'
    else:
        return 'n'


def split_title(title):
    """Produces a list of keywords from the paper title with
       boring words removed.

       Args:
          title (string): a title to analyse

       Returns:
           list2 (list): a list of keywords
    """
    text = title.replace('-',' ')                                       #replacing hyphens with spaces
    tokens = word_tokenize(text)                                           #tokenizing the title
    lowertokens = [word.lower() for word in tokens]                             #converting all words to lowercase
    taggedwords = pos_tag(lowertokens)                                    #tagging words as verb, noun etc to help lemmatizer
    list1 = [(x,get_lemma_pos(y)) for (x,y) in taggedwords if x not in remove] #converts those to format lemmatizer understands
    wl = WordNetLemmatizer()                                                    #initialising the lemmatizer
    list2 = [wl.lemmatize(x,pos=y) for (x,y) in list1]                          #lemmatizing each word in list
    return list2

def augment_author(author, words, date):
    """Augments the author profiles given words

       Given a dict of an author name and a list of words
       increase the word counts for the given author appropriately

       Args:
           author (string): author name to augment
           words (list): a list of wordds
           date (string): date paper was written
    """
    (profiles, status) = dbh.find_profiles({'name':author}) #find profiles
    author_profile = {}
    if not status:
        author_profile = dbh.add_new_profile({'name':author, 'keywords':repr({})}) #if none, insert new
    else:
        author_profile = profiles[0]
    

    print("FOUND PROFILES", author_profile, status)

    author_words = ast.literal_eval(author_profile['keywords']) #find author's keywords

    for word in words:    
        if word not in author_words:
            author_words[word] = weighting(word, words, date) #add new word
        else:
            author_words[word] += weighting(word, words, date) #augment old word

    # x = sorted(author_words.items(), key=lambda t: t[1], reverse=True)   #sorting the words from lowest to highest freq in list
    # author_profile['keywords'] = repr(x) #update the word list in profile (dict converted to string for db)
    author_profile['keywords'] = repr(author_words)
    print("FINAL AUTHOR_PROFILE", author_profile)
    dbh.update_profile(author_profile['id'], author_profile) #update row in db 

def find_author_profile(author, profiles):
    """Finds a given author in a profile list

       Args:
           author (string): author name to find
           profiles (list): list of profiles to search

       Returns:
           p (dict): a dictionary representing an author profile
    """
    for p in profiles:
        if p['name'] == author:
            return p
    return {}

def weighting(word, words, date):
    """A weighting function based on words and date.

       The function used currently is linear deprecation up
       to a time gap of fifty years.

       Parameters:
           FUNC : function to produce weight given time diff
           CUTOFF : cutoff for gradual weighting
           BASE : lowest weighting. time_diffs after the CUTOFF
                  get this weight by default

       Args:
           word (string): the word we're weighting
           words (list): other words in the title
           date (string): date the paper was written

       Returns:
           weighting (int): a weighted number representing
               how important this occurence of the word is
    """
    FUNC = (lambda d: -0.09*d + 5)
    CUTOFF = 50
    BASE = 0.5
    import time
    year = int(date[:4])
    current_year = time.gmtime()[0]
    time_diff = current_year - year
    weighting = FUNC(time_diff) if time_diff <= CUTOFF else BASE
    return weighting


if __name__ == "__main__":
    import doctest
    doctest.testmod()
