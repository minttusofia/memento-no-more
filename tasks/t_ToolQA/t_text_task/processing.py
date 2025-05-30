# write information of question types into .jsonl
# %%
import json
import pandas as pd

from core import TOOLQA_PATH

DATA_BASE_DIR = TOOLQA_PATH / 'data/questions'

def add_type_info(level, variant):
    data = []
    with open(DATA_BASE_DIR+f"/{level}/{variant}-{level}.jsonl", "r") as f:
        for line in f:
            data.append(json.loads(line))
    if level == 'easy':
        for _, d in enumerate(data):
            q = d['question']
            if q.split(' ')[0] == 'What':
                d['type'] = 'what'
            elif q.split(' ')[0] == 'When':
                d['type'] = 'when'
            elif q.split(' ')[0] == 'Where':
                d['type'] = 'where'
            elif q.split(' ')[0] == 'Who':
                d['type'] = 'who'
            elif q.split(' ')[0] == 'How':
                d['type'] = 'how'
            else:
                raise ValueError(f"Question type not found: {q}")
    elif level == 'hard':
        for i, d in enumerate(data):
            if i < 20:
                d['type'] = 'how many events'
            elif i < 40 and i >= 20:
                d['type'] = 'how many people'
            elif i < 60 and i >= 40:
                d['type'] = 'schedule'
            elif i < 80 and i >= 60:
                d['type'] = 'all events'
            elif i < 100 and i >= 80:
                d['type'] = 'all dates'
    df_data = pd.DataFrame(data)
    with open(f"{variant}-{level}.jsonl", 'w') as f:
        f.write(df_data.to_json(orient="records", lines=True, force_ascii=False))

# %%
add_type_info('hard', 'agenda')
# %%
