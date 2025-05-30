#%%
import pandas as pd
import json
import re
import string

from core import TOOLQA_PATH

CORPUS_BASE_DIR = TOOLQA_PATH / "data/external_corpus"
CORPUS_DIR = {
    'flights': CORPUS_BASE_DIR / "flights/Combined_Flights_2022.csv",
    'coffee': CORPUS_BASE_DIR / "coffee/coffee_price.csv",
    'yelp': CORPUS_BASE_DIR / "yelp/yelp_academic_dataset_business.json",
    'airbnb': CORPUS_BASE_DIR / "airbnb/Airbnb_Open_Data.csv",
}
DATA_BASE_DIR = TOOLQA_PATH / "data/questions"

def read_qa(file_path):
    data = []
    with open(file_path, "r") as f:
        for line in f:
            data.append(json.loads(line))
    questions = []
    answers = []
    question_types = []
    for d in data:
        questions.append(d['question'])
        answers.append(d['answer'])
        question_types.append(d['type'])
    return questions, answers, question_types

def db_loader(file_path, target_db):
    print(f"Loading {target_db} data")
    if target_db == 'yelp':
        with open(file_path) as data_file:
            data = pd.DataFrame([json.loads(line) for line in data_file]).astype(str)
    else:
        # astype will significantly increase the memory usage up to 10x times.
        data = pd.read_csv(file_path).astype(str)

    column_names = ', '.join(data.columns.tolist())
    return (data, column_names)

def normalize_answer(agent_answer: str, true_answer: str, level: str = 'easy', db_variant: str='flights', type: str=None) -> str:
    def remove_articles(text):
        return re.sub(r"\b(a|an|the|minutes|USD|usd)\b", " ", text)
  
    def white_space_fix(text):
        return " ".join(text.split())

    def remove_punc(text):
        exclude = set(string.punctuation)
        return "".join(ch for ch in text if ch not in exclude)

    def lower(text):
        return text.lower()
  
    def yes_or_no(text):
        if text == 'false':
            text = 'no'
        elif text == 'true':
            text = 'yes'
        return text

    def standardize_answer(text):
        text = white_space_fix(remove_articles(remove_punc(lower(text))))
        return text.strip()
    
    if level == 'easy' and db_variant == 'flights':
        if type == 'yes or no':
            if_correct = (yes_or_no(lower(agent_answer)) == yes_or_no(lower(true_answer)))
        else:
            # e.g., '443.0' -> '443'; '11:53' -> '1153' 
            agent_answer = agent_answer.split('.')[0]
            true_answer = true_answer.split('.')[0]
            if_correct = (remove_punc(agent_answer) == remove_punc(true_answer))
    
    elif level == 'easy' and db_variant == 'coffee':
        if type == 'percentage change':
            agent_answer = agent_answer.split('%')[0]
            agent_answer = str(round(float(agent_answer), 2))
            true_answer = true_answer.split('%')[0]
            true_answer = str(round(float(true_answer), 2))
            agent_answer = standardize_answer(agent_answer)
            true_answer = standardize_answer(true_answer)
            len_answer = len(true_answer)
            if len(agent_answer) >= len_answer:
                if_correct = (agent_answer[:len_answer] == true_answer)
            else:
                if_correct = False
            if_correct = (agent_answer == true_answer)
        elif type == 'range of coffee price':
            agent_answer = str(round(float(agent_answer), 1))
            true_answer = str(round(float(true_answer), 1))
            agent_answer = standardize_answer(agent_answer)
            true_answer = standardize_answer(true_answer)
            if_correct = (agent_answer == true_answer)
        else:
            if_correct = (standardize_answer(agent_answer) == standardize_answer(true_answer))
    
    elif level == 'easy' and db_variant == 'yelp':
        if type == 'yes or no - openning':
            agent_answer = yes_or_no(lower(agent_answer))
            if agent_answer != lower(true_answer):
                if agent_answer == '1':
                    agent_answer = 'yes'
                elif agent_answer == '0':
                    agent_answer = 'no'
            if_correct = (agent_answer == lower(true_answer))
        
        elif type == 'yes or no - appointment':
            if 'no' in lower(agent_answer):
                agent_answer = 'no'
            if_correct = (lower(agent_answer) == lower(true_answer))
        else:
            if_correct = (standardize_answer(agent_answer) == standardize_answer(true_answer))

    elif level == 'easy' and db_variant == 'airbnb':
        if type in ["days available", "minimum number of nights", 'how many reviews', 'when constructed']:
            agent_answer = str(int(float(agent_answer)))
            if_correct = (agent_answer == true_answer)
        elif type == "last review date":
            if agent_answer == 'nan' or agent_answer == 'None' or "no" in lower(agent_answer):
                agent_answer = 'null'
                if_correct = (agent_answer == true_answer)
            else:
                if_correct = (standardize_answer(agent_answer) == standardize_answer(true_answer))
        else:
            if_correct = (standardize_answer(agent_answer) == standardize_answer(true_answer))
    
    elif level == 'hard' and db_variant == 'coffee':
        if type in ["average coffee price", "coffee price change", "coffee price range"]:
            true_answer = true_answer.split('-')[-1]
            true_answer = remove_articles(true_answer).strip()
            true_answer = float(true_answer)
            agent_answer = agent_answer.split('-')[-1]
            agent_answer = remove_articles(agent_answer).strip()
            agent_answer = round(float(agent_answer), 1)
            if_correct = (agent_answer == true_answer)
        elif type in ['percentage change comparison', 'percentage increase', 'average percentage change']:
            true_answer = true_answer.split('-')[-1]
            true_answer = true_answer.split('%')[0]
            true_answer = float(true_answer)
            agent_answer = agent_answer.split('-')[-1]
            agent_answer = agent_answer.split('%')[0]
            agent_answer = round(float(agent_answer), 1)
            if_correct = (agent_answer == true_answer)
        elif type == 'average daily volume':
            true_answer = float(true_answer)
            agent_answer = round(float(agent_answer),1)
            if_correct = (agent_answer == true_answer)
        else:
            if_correct = (standardize_answer(agent_answer) == standardize_answer(true_answer))
    
    elif level == 'hard' and db_variant == 'airbnb':
        if type in ['total price', 'average price']:
            true_answer = true_answer.split('$')[-1]
            true_answer = float(true_answer)
            agent_answer = agent_answer.split('$')[-1]
            agent_answer = round(float(agent_answer), 1)
            if_correct = (agent_answer == true_answer)
        elif type == 'cost per night':
            true_answer = true_answer.split('$')[-1]
            true_answer = int(true_answer)
            agent_answer = agent_answer.split('$')[-1]
            if agent_answer.isdigit():
                agent_answer = int(agent_answer)
                if_correct = (agent_answer == true_answer)
            else:
                try:
                    agent_answer = int(float(agent_answer))
                    if_correct = (agent_answer == true_answer)
                except ValueError:
                    if_correct = False
        elif type == 'average review rates':
            true_answer = float(true_answer)
            agent_answer = round(float(agent_answer), 2)
            if_correct = (agent_answer == true_answer)
        elif type == 'proporion of airbnbs':
            true_answer = float(true_answer)
            agent_answer = round(float(agent_answer), 1)
            if_correct = (agent_answer == true_answer)
        else:
            if_correct = (standardize_answer(agent_answer) == standardize_answer(true_answer))
    
    else:
        if_correct = (standardize_answer(agent_answer) == standardize_answer(true_answer))

    return if_correct


def basic_normalize_answer(agent_answer: str, true_answer: str, level: str, db_variant: str, question_variant: int) -> str:
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
    
    if level == 'test' and db_variant == 'flights': # information not matche between data and data generation process
        if question_variant == 15:
            if standardize_answer(agent_answer) == '230' or standardize_answer(agent_answer) == '160':
                return True
        if question_variant == 16:
            if standardize_answer(agent_answer) == '130' or standardize_answer(agent_answer) == '00':
                return True
        if question_variant == 17:
            if standardize_answer(agent_answer) == '280' or standardize_answer(agent_answer) == '00':
                return True
            
    if level == 'test' and db_variant == 'yelp' and question_variant == 5: # no requirement on the order in the question
        true_answer_set = set(true_answer.split(', '))
        agent_answer_set = set(agent_answer.split(', '))
        if true_answer_set==agent_answer_set:
            return True
    
    if_correct = (standardize_answer(agent_answer) == standardize_answer(true_answer))
    return if_correct


# %%
# normalize_answer('0.0%', '0.0%', 'easy', 'coffee', 'percentage change')