# %%
# split data
from utils import read_qa, DATA_BASE_DIR
from core import TOOLQA_PATH
import random

def split_data(data, ratio_easy_question=7/10, ratio_hard_question=9/14, n_easy = 80, n_hard = 98, n_easy_t = 10, n_hard_t = 14):
    random.seed(0)
    
    def process_data(questions, answers, ratio, n_total, n_template):
        question_train = []
        answer_train = []
        question_test = []
        answer_test = []
        for i in range(n_total // n_template):
            question = questions[i * n_template:(i + 1) * n_template]
            answer = answers[i * n_template:(i + 1) * n_template]
            qa_pairs = list(zip(question, answer))
            random.shuffle(qa_pairs)
            question, answer = zip(*qa_pairs)
            question_train += question[:int(ratio * n_template)]
            answer_train += answer[:int(ratio * n_template)]
            question_test += question[int(ratio * n_template):]
            answer_test += answer[int(ratio * n_template):]
        return question_train, answer_train, question_test, answer_test

    question_easy = data[0][:n_easy]
    answer_easy = data[1][:n_easy]
    question_hard = data[0][n_easy:]
    answer_hard = data[1][n_easy:]
    
    question_train_easy, answer_train_easy, question_test_easy, answer_test_easy = process_data(
        question_easy, answer_easy, ratio_easy_question, n_easy, n_easy_t)
    question_train_hard, answer_train_hard, question_test_hard, answer_test_hard = process_data(
        question_hard, answer_hard, ratio_hard_question, n_hard, n_hard_t)

    question_train = question_train_easy + question_train_hard
    answer_train = answer_train_easy + answer_train_hard
    question_test = question_test_easy + question_test_hard
    answer_test = answer_test_easy + answer_test_hard

    return (question_train, answer_train), (question_test, answer_test)

# %%
import pandas as pd
data = read_qa(DATA_BASE_DIR / "all/dblp-all.jsonl")
train_data, test_data = split_data(data)
df_train_data = pd.DataFrame(list(zip(train_data[0], train_data[1])), columns=['question', 'answer'])
df_test_data = pd.DataFrame(list(zip(test_data[0], test_data[1])), columns=['question', 'answer'])
with open(TOOLQA_PATH / "data/questions/train/dblp-train.jsonl", 'w') as f:
        f.write(df_train_data.to_json(orient="records", lines=True, force_ascii=False))
with open(TOOLQA_PATH / "data/questions/test/dblp-test.jsonl", 'w') as f:
        f.write(df_test_data.to_json(orient="records", lines=True, force_ascii=False))
# %%
