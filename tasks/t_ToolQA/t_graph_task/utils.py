#%%
import re
import json
import pickle
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
        answers.append(d['answer'])
    return questions, answers

def load_graph(file_path):
    print("Loading DBLP data...")
    with open('{}/paper_net.pkl'.format(file_path), 'rb') as f:
        paper_net = pickle.load(f)

    with open('{}/author_net.pkl'.format(file_path), 'rb') as f:
        author_net = pickle.load(f)
    
    with open("{}/title2id_dict.pkl".format(file_path), "rb") as f:
        title2id_dict = pickle.load(f)
    with open("{}/author2id_dict.pkl".format(file_path), "rb") as f:
        author2id_dict = pickle.load(f)
    with open("{}/id2title_dict.pkl".format(file_path), "rb") as f:
        id2title_dict = pickle.load(f)
    with open("{}/id2author_dict.pkl".format(file_path), "rb") as f:
        id2author_dict = pickle.load(f)
    print("DBLP data is loaded, including two graphs: AuthorNet and PaperNet.")
    return (paper_net, author_net, title2id_dict, author2id_dict, id2author_dict, id2title_dict)

DATA_BASE_DIR = TOOLQA_PATH / "data/questions/"
graph_path = TOOLQA_PATH / "data/external_corpus/dblp"
GRAPH_DATA = load_graph(graph_path)

def normalize_answer(agent_answer: str, true_answer: str) -> bool:
    if true_answer.isdigit():
        true_answer = int(true_answer)
        try:
            agent_answer = int(float(agent_answer))
        except ValueError:
            return False
    elif len(true_answer.split('; ')) > 0:
        true_answer = true_answer.split('; ')
        agent_answer = agent_answer.split('; ')
        if len(true_answer) != len(agent_answer):
            return False
        for i in range(len(true_answer)):
            if true_answer[i] not in agent_answer:
                return False
        return True
    return (agent_answer==true_answer)


# %%
