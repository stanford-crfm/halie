from thefuzz import fuzz
import numpy as np

question_start_words = ["who", "what", "where", "how", "which", "why", "when", "whose", "do", "does", "did", "can", "could", "has", "have", "is", "was", "are", "were", "should", "what's", "whats"]
lexical_words = ["letter word", "prefix", "letters", "with the letter", "beginning with", "begin with", "begins with", "starts with",  "staring with", "a as the first and 3rd letter", "starting with", "lettered word", "start with", "ends with", "stars with", "ends in"]
meaning_words = ["synonym", "antonym", "opposite of", "define", "words for", "definition of", "word for", "name for", "names for", "words that mean", "other terms", "a word that means", "word meaning", "another term", "means what", "mean", "is the same as", "a verb for", "term for", "synonyn", "names of"]
completion_words = ["is", "was", "by", "may", "cause", "are", "of", "about", "the", "to", "their", "on", "in"]
completion_phrases = ["is called a", "is called an", "is called", "finish the phrase", "finish the sentence"]
command_start_words = ["list", "examples", "define", "finish the phrase", "name a", "name me", "finish the sentence", "name some", "give me", "tell me", "please name"]


def get_query_type(query, clues_list):
    query = query.lower().replace("\n", "").replace('"', '')[1:]
    max_similarity = (0, "")
    for clue in clues_list:
        similarity = fuzz.ratio(query, clue.replace('"', '').replace("'", ""))
        if (similarity > max_similarity[0]):
            max_similarity = (similarity, query)

    query_types = []
    if(max_similarity[0] == 100):
        query_types.append("exact")
    if(max_similarity[0] > 70 and max_similarity[0] < 100):
        query_types.append("close")
    if(np.sum([word in query for word in lexical_words]) > 0):
        query_types.append("lexical")
    if(np.sum([word in query for word in meaning_words]) > 0):
        query_types.append("meaning")
    if("?" in query or query.split(" ")[0] in question_start_words):
        query_types.append("question")
    elif(query.split(",")[-1].split(" ")[0] in question_start_words):
        query_types.append("question")
    elif(query.split(" ")[-1] in completion_words or np.sum([phrase in query for phrase in completion_phrases]) > 0):
        query_types.append("completion")
    elif(np.sum([p in query for p in command_start_words]) > 0):
        query_types.append("command")
    elif(len(query.split()) < 5):
        query_types.append("keyword")
    else:
        query_types.append("phrase")
    return query_types
