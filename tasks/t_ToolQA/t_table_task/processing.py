# write information of question types into .jsonl
# %%
import json
import pandas as pd

from core import TOOLQA_PATH

DATA_BASE_DIR = TOOLQA_PATH / 'data/questions'
QA_EASY_DIR = {
    'flights': DATA_BASE_DIR / "easy/flight-easy.jsonl",
    'coffee': DATA_BASE_DIR / "easy/coffee-easy.jsonl",
    'yelp': DATA_BASE_DIR / "easy/yelp-easy.jsonl",
    'airbnb': DATA_BASE_DIR / "easy/airbnb-easy.jsonl",
}
QA_DIFFICULT_DIR = {
    'flights': DATA_BASE_DIR / "hard/flights-hard.jsonl",
    'coffee': DATA_BASE_DIR / "hard/coffee-hard.jsonl",
    'yelp': DATA_BASE_DIR / "hard/yelp-hard.jsonl",
    'airbnb': DATA_BASE_DIR / "hard/airbnb-hard.jsonl",

}

question_type_easy = {
    'flights': ['flight departure time', 'yes or no', 'flight number', 'time difference', 'delay of arrival time', 'extra minutes', 'local arrival time', 'CRS-recorded arrival time', 'flight duration', 'minutes taking to taxi in' ],
    'coffee': ['opening price', 'lowest price', 'highest price', 'closing price', 'volume', 'percentage change', 'A or B', 'range of coffee price'],
    'yelp': ['address', 'city', 'state', 'postal code', 'star rating', 'how many reviews', 'yes or no - openning', 'yes or no - appointment', 'hours of operation', 'categories', 'coordinates'],
    'airbnb': ["host's name", 'days available', 'room type', 'price', 'minimum number of nights', 'when constructed', 'how many reviews', 'last review date', 'review rate number', 'average reviews per month']
}

question_type_difficult = {
    'flights': ['percentage', 'average delay time', 'diverted flights', 'flights with long distance', 'average airtime', 'flights from A to B', 'average flight time', 'fastest flight', 'average speed', 'total number' ],
    'airbnb': ['total price', 'how many airbnbs', 'average price', 'average review rates', 'proporion of airbnbs', 'cost per night', 'airbnb with high rate', 'room with the lowest price', 'room with the highest review rate', 'shared room with the lowest price'],
    'coffee': ['highest coffee price', 'lowest coffee price', 'average coffee price', 'coffee price change', 'percentage change', 'day with the greatest price change', 'average daily volume', 'day with the highset increase', 'times of coffee price', 'percentage increase', 'coffee price range', 'day with the higher close price', 'average percentage change'],
    'yelp': ['how many business', 'business in total', 'highest star rating', 'highest review count', 'average review counts', 'nearest business', 'business recommendation', 'business not open', 'average star rating', 'postal code region']

}
def add_type_info_easy(variant, file_path):
    data = []
    questions_types = []
    # number of questions for each type
    #number_of_questions = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10]  # flights, airbnb
    #number_of_questions = [13, 13, 13, 13, 12, 12, 12, 12]  # coffee
    number_of_questions = [10, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9] # yelp
    for i, t in enumerate(question_type_easy[variant]):
        for j in range(number_of_questions[i]):
            questions_types.append(t)
    with open(QA_EASY_DIR[variant], "r") as f:
        for line in f:
            data.append(json.loads(line))
    for i, d in enumerate(data):
        d['type'] = questions_types[i]
    df_data = pd.DataFrame(data)
    with open(file_path, 'w') as f:
        f.write(df_data.to_json(orient="records", lines=True, force_ascii=False))

def add_type_info_diffcult(variant, file_path):
    data = []
    questions_types = []
    number_of_questions = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10] # for airbnb, yelp, flights
    #number_of_questions = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10] # for coffee
    for i, t in enumerate(question_type_difficult[variant]):
        for j in range(number_of_questions[i]):
            questions_types.append(t)
    with open(QA_DIFFICULT_DIR[variant], "r") as f:
        for line in f:
            data.append(json.loads(line))
    for i, d in enumerate(data):
        d['type'] = questions_types[i]
    df_data = pd.DataFrame(data)
    with open(file_path, 'w') as f:
        f.write(df_data.to_json(orient="records", lines=True, force_ascii=False))
#%%
add_type_info_diffcult('flights', 'flights-hard.jsonl')


# %%
