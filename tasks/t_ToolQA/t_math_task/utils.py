#%%
import json
import pickle
import os
import string

from core import TOOLQA_PATH


def read_qa(file_path):
    data = []
    with open(file_path, "r") as f:
        for line in f:
            data.append(json.loads(line))
    questions = []
    answers = []
    for d in data:
        questions.append(d['question'])
        answers.append(d['answer'].split('\n#### ')[1])
    return questions, answers


def remove_punc(text):
        exclude = set(string.punctuation)
        return "".join(ch for ch in text if ch not in exclude)

# %%
QUESTION_ANSWER = read_qa(TOOLQA_PATH, "data/questions/test/gsm8k-test.jsonl")
# %%
