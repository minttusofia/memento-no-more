# %%
# split data

from core import TOOLQA_PATH

import random
import json

def read_qa(file_path):
    data = []
    with open(file_path, "r") as f:
        for line in f:
            data.append(json.loads(line))
    questions = []
    answers = []
    qid = []
    question_type = []
    for d in data:
        questions.append(d['question'])
        answers.append(d['answer'])
        qid.append(d['qid'])
        question_type.append(d['type'])
    return questions, answers, qid, question_type

def process_data(questions, answers, qids, question_types, ratio):
        question_train = []
        answer_train = []
        qid_train = []
        question_type_train = []

        question_test = []
        answer_test = []
        qid_test = []
        question_type_test = []

        # index_question_t = [0,13,26,39,52,64,76,88,100,110,120,130,140,150,160,170,180,190,200,210,220,230]
        # index_question_t = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200]
        #index_question_t = [0, 10, 19, 28, 37, 46, 55, 64, 73, 82, 91, 100, 110, 120, 130, 140, 147, 155, 160, 170, 180]
        index_question_t = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 139, 149, 158, 168]
        for i in range(len(index_question_t) - 1):
            question = questions[index_question_t[i]:index_question_t[i+1]]
            answer = answers[index_question_t[i]:index_question_t[i+1]]
            qid = qids[index_question_t[i]:index_question_t[i+1]]
            question_type = question_types[index_question_t[i]:index_question_t[i+1]]

            qa_pairs = list(zip(question, answer, qid, question_type))
            random.shuffle(qa_pairs)
            question, answer, qid, question_type = zip(*qa_pairs)
            n_template = len(question)

            question_train += question[:int(ratio * n_template)]
            answer_train += answer[:int(ratio * n_template)]
            qid_train += qid[:int(ratio * n_template)]
            question_type_train += question_type[:int(ratio * n_template)]

            question_test += question[int(ratio * n_template):]
            answer_test += answer[int(ratio * n_template):]
            qid_test += qid[int(ratio * n_template):]
            question_type_test += question_type[int(ratio * n_template):]

        return question_train, answer_train, qid_train, question_type_train, question_test, answer_test, qid_test, question_type_test

        # for i in range(n_total // n_template):
        #     question = questions[i * n_template:(i + 1) * n_template]
        #     answer = answers[i * n_template:(i + 1) * n_template]
        #     qid = qids[i * n_template:(i + 1) * n_template]
        #     question_type = question_types[i * n_template:(i + 1) * n_template]

        #     qa_pairs = list(zip(question, answer, qid, question_type))
        #     random.shuffle(qa_pairs)

        #     question, answer, qid, question_type = zip(*qa_pairs)

        #     question_train += question[:int(ratio * n_template)]
        #     answer_train += answer[:int(ratio * n_template)]
        #     qid_train += qid[:int(ratio * n_template)]
        #     question_type_train += question_type[:int(ratio * n_template)]

        #     question_test += question[int(ratio * n_template):]
        #     answer_test += answer[int(ratio * n_template):]
        #     qid_test += qid[int(ratio * n_template):]
        #     question_type_test += question_type[int(ratio * n_template):]

        # return question_train, answer_train, qid_train, question_type_train, question_test, answer_test, qid_test, question_type_test


def split_data(data, ratio_question=7/10, n_question = 180, n_question_t = 21):
    random.seed(0)

    question = data[0]
    answer = data[1]
    qid = data[2]
    question_type = data[3]

    question_train, answer_train, qid_train, question_type_train, question_test, answer_test, qid_test, question_type_test = process_data(
        question, answer, qid, question_type, ratio_question)

    return (qid_train, question_train, answer_train, question_type_train), (qid_test, question_test, answer_test, question_type_test)

# %%
import pandas as pd
DATA_BASE_DIR = TOOLQA_PATH / "data/questions/"
data = read_qa(DATA_BASE_DIR / "all/airbnb-all.jsonl")
train_data, test_data = split_data(data)
df_train_data = pd.DataFrame(list(zip(train_data[0], train_data[1], train_data[2], train_data[3])), columns=['qid', 'question', 'answer', 'type'])
df_test_data = pd.DataFrame(list(zip(test_data[0], test_data[1], test_data[2], test_data[3])), columns=['qid', 'question', 'answer', 'type'])
with open(TOOLQA_PATH / "data/questions/train/airbnb-train.jsonl", 'w') as f:
        f.write(df_train_data.to_json(orient="records", lines=True, force_ascii=False))
with open(TOOLQA_PATH / "data/questions/test/airbnb-test.jsonl", 'w') as f:
        f.write(df_test_data.to_json(orient="records", lines=True, force_ascii=False))
# %%
