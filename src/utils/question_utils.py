"""
sequence_id: integer in the range of [0, 99] (refers to a sequence in sequences.csv)
    sequence_id = 19
    sequence = 5,14,10,24,29,30,0,16,8,20,22,False,False,False,False,False,False,True,True,True,True,True

question_id: integer in the range of [0, 30] (refers to a question in questions.csv)
    self.order = 0
    question_id = 5
    In the phrase 'Y2K' what does 'K' stand for?,millennium,computer code,catastrophe,thousand,D

question_type: string value based on question_id and sequence
    'attn': if question_id = 30
    'ctrl': if sequence[self.order + 11] = False (no LM use)
    'lm': lm use

    question_type = 'ctrl'
category: string value based on question_id
    'misc' for question_id [0, 5]
    'global_facts' for question_id [6, 11]
    'us_fp' for question_id [12, 17]
    'nutrition' for question_id [18, 23]
    'college_chem' for question_id [24, 29]
    'attention' for question_id = 30

    category = 'misc'
"""
import numpy as np
import pandas as pd
from thefuzz import fuzz

attention_check = [30]

category_map = {
    'Miscellany': [i for i in range(6)],
    'Global facts': [i + 6 for i in range(6)],
    'US foreign policy': [i + 12 for i in range(6)],
    'Nutrition': [i + 18 for i in range(6)],
    'College chemistry': [i + 24 for i in range(6)],
    'attention': attention_check,
}
category_map = {vi: k for k, v in category_map.items() for vi in v}

path_sequence = 'data/raw/question/sequences.txt'
sequences = pd.read_csv(path_sequence)

path_question = 'data/raw/question/questions.csv'
questions = pd.read_csv(path_question)

question_start_words = ["who", "what", "where", "how", "which", "why", "when", "whose", "do", "does", "did", "can", "could", "has", "have", "is", "was", "are", "were", "should", "what's", "whats"]
meaning_words = ["synonym", "antonym", "opposite of", "define", "words for", "definition of", "word for", "name for", "names for", "words that mean", "other terms", "a word that means", "word meaning", "another term", "means what", "mean", "is the same as", "a verb for", "term for", "synonyn", "names of"]
completion_words = ["is", "was", "by", "may", "cause", "are", "of", "about", "the", "to", "their", "on", "in"]
completion_phrases = ["is called a", "is called an", "is called", "finish the phrase", "finish the sentence"]
command_start_words = ["list", "examples", "define", "describe", "finish the phrase", "name a", "name me", "finish the sentence", "name some", "give me", "tell me", "please name"]


def get_prompt_type(user_prompt, test_question, test_choices):
    clean_prompt = user_prompt.lower().replace("\n", "").strip()
    clean_test_question = test_question.lower().replace("\n", "")
    clean_test_choices = [c.lower().replace("\n", "") for c in test_choices]
    similarity = fuzz.ratio(clean_prompt, clean_test_question)
    prompt_types = []
    if(similarity == 100):
        prompt_types.append("exact")
    if(similarity > 70 and similarity < 100):
        prompt_types.append("close")
    if(np.sum([m in clean_prompt for m in meaning_words]) > 0):
        prompt_types.append("meaning")
    if("?" in clean_prompt or clean_prompt.split(" ")[0] in question_start_words):
        prompt_types.append("question")
    elif(clean_prompt.split(",")[-1].split(" ")[0] in question_start_words):
        prompt_types.append("question")
    elif(clean_prompt.split(" ")[-1] in completion_words or np.sum([p in clean_prompt for p in completion_phrases]) > 0):
        prompt_types.append("completion")
    elif(np.sum([p in clean_prompt for p in command_start_words]) > 0):
        prompt_types.append("command")
    elif(len(clean_prompt.split()) <= 5):
        prompt_types.append("keyword")
    elif(clean_test_choices[0] in clean_prompt or clean_test_choices[1] in clean_prompt or clean_test_choices[2] in clean_prompt or clean_test_choices[3] in clean_prompt):
        prompt_types.append("choices")
    else:
        prompt_types.append("others")
    return prompt_types
