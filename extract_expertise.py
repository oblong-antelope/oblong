#!/usr/bin/python
# -*- coding: utf8 -*-
from nltk.stem import *
from nltk import pos_tag
import nltk
import string
'''Notes: Possible stemmers: porter, lancaster, snowball, wordnet lemmatization (may require verb/noun POS tagger) all in NLTK - which is best?'''

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


papers2 = [
           {"title"   : "Making make makes maker made",
            "authors" : " F. Toni",
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

papers4 = [
           {"title"   : "Do you really think it is weakness that yields to temptation? I tell you that there are terrible temptations which it requires strength, strength and courage to yield to",
            "authors" : " F. Toni",
            "date"    : "2016"}
          ]

remove = ['for', 'and', 'a', 'the', 'with', 'of', 'using', 'on','between','based','non',',','.',':',';'] #boring stuff to get rid of

def build_profiles(papers):
    """Produces a dictionary of name:profile pairs. The profiles are a
       prioritised list of keywords.
       
       papers : a list of papers to build profiles from

       returns : a dictionary of name:profile pairs
    """
    profiles = {}
    for paper in papers:
        author_list = split_authors(paper['authors'])
        word_list = split_title(paper['title'])
        for author in author_list:
            profiles = augment_author(author, profiles, word_list)
    return profiles

def split_authors(authors):
    """Produces a list of strings containing the authors' names.

    authors : a string containing an author list

    returns : a list of author names

     split_authors("K. Cyras, K. Satoh, and F. Toni")
    ['K. Cyras', 'K. Satoh', 'F. Toni']
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

#testing purposes
'''wl2 = WordNetLemmatizer()
text=nltk.word_tokenize("Online Argumentation-Based Platform for Recommending Medical Literature")
text1 = [word.lower() for word in text]
list1 = [(x,get_lemma_pos(y)) for (x,y) in list]
list2 = [wl2.lemmatize(x,pos=y) for (x,y) in list1]
print list2'''

'''text="Online Argumentation-Based Platform for Recommending Medical Literature"
text1 = string.replace(text,'-',' ')
print(text1)'''



def split_title(title):
    """Produces a list of keywords from the paper title with
       boring words removed.

    title : a title to analyse

    returns : a list of keywords

     split_title("ABA+: assumption-based argumentation with preferences")
    ['aba+', 'assumption-based', 'argumentation', 'preferences']
    """
    text = string.replace(title,'-',' ')                                       #replacing hyphens with spaces
    tokens = nltk.word_tokenize(text)                                           #tokenizing the title
    lowertokens = [word.lower() for word in tokens]                             #converting all words to lowercase
    taggedwords = nltk.pos_tag(lowertokens)                                    #tagging words as verb, noun etc to help lemmatizer
    list1 = [(x,get_lemma_pos(y)) for (x,y) in taggedwords if x not in remove] #converts those to format lemmatizer understands
    wl = WordNetLemmatizer()                                                    #initialising the lemmatizer
    list2 = [wl.lemmatize(x,pos=y) for (x,y) in list1]                          #lemmatizing each word in list
    return list2

def augment_author(author, profiles, words):
    """Given a dict of profiles, an author name, and a list of words
       increase the word counts for the given author appropriately

       author : author name to augment
       profiles : dict of author:word_count pairs
       words : a list of words

       returns : the augmented profile

       augment_author('F. Toni', {'F. Toni':{'argumentation':2}}, ['argumentation', 'preferences'])
       {'F. Toni': {'argumentation': 3, 'preferences': 1}}
    """
    if author not in profiles:
        profiles[author] = {}
    for word in words:
        author_words = profiles[author]
        if word not in author_words:
            author_words[word] = 1
        else:
            author_words[word] += 1
    return profiles

	
if __name__ == "__main__":
    import doctest
    doctest.testmod()
