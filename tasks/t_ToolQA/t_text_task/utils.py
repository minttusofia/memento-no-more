import json
import string
import re

from core import TOOLQA_PATH

def read_qa(file_path):
    data = []
    with open(file_path, "r") as f:
        for line in f:
            data.append(json.loads(line))
    questions = []
    answers = []
    types = []
    for d in data:
        questions.append(d['question'])
        answers.append(d['answer'])
        types.append(d['type'])
    return questions, answers, types

DATA_BASE_DIR = TOOLQA_PATH / "data/questions/"
CHROMA_DB_BASE_DIR = TOOLQA_PATH / "data/chroma_db"

def normalize_answer(agent_answer, true_answer, type) -> bool:
    def remove_articles(text):
        return re.sub(r"\b(a|an|the|minutes|USD|usd)\b", " ", text)
  
    def white_space_fix(text):
        return " ".join(text.split())

    def remove_punc(text):
        exclude = set(string.punctuation)
        return "".join(ch for ch in text if ch not in exclude)

    def lower(text):
        return text.lower()

    def standardize_answer(text):
        text = white_space_fix(remove_articles(remove_punc(lower(text))))
        return text.strip()
    
    if type == 'all events':
        true_answer_list = true_answer.split(',')
        agent_answer_list = agent_answer.split(',')
        if len(true_answer_list) == 2:
            if len(agent_answer_list) != 2:
                return False
            else:
                if standardize_answer(true_answer_list[0]) in standardize_answer(agent_answer_list[0]) or standardize_answer(true_answer_list[0]) in standardize_answer(agent_answer_list[1]):
                    if standardize_answer(true_answer_list[1]) in standardize_answer(agent_answer_list[0]) or standardize_answer(true_answer_list[1]) in standardize_answer(agent_answer_list[1]):
                        return True
                else:
                    return False

    true_answer_list = true_answer.split('//')
    if len(true_answer_list) > 0:
        for a in true_answer_list:
            if standardize_answer(a) in standardize_answer(agent_answer):
                return True
    else:
        agent_answer = standardize_answer(agent_answer)
        true_answer = standardize_answer(true_answer)
        if true_answer in agent_answer:
            return True
    
    if_correct = (standardize_answer(agent_answer) == standardize_answer(true_answer))

    return if_correct