# %%
import copy
import time
from dotenv import load_dotenv
import nest_asyncio
import numpy as np
from pathlib import Path
from datetime import datetime

from agent.clients import get_client
from core.steps import StepMessages
from core.tags import Tag
from core.messages import Message, Role

from .conversion_utils import prepare_step_for_exercise, save_steps_as_exercises
from .apply_filter import filter_steps, load_filtered_steps_subset
from .filters import EVAL_FILTERS
from .reprompting import call_client_on_monologue_and_ipython_steps
from .xml_trajectory import save_steps_dataset, load_history_xml_dataset, monologue_prompt_from_step

from agent import BASE_PATH, AGENT_BATCH_RUNS_PATH


def insert_hint_before_monologue(steps: list[StepMessages], hint: str) -> list[StepMessages]:
    steps_with_hints = copy.deepcopy(steps)
    for i, step_messages in enumerate(steps_with_hints):
        step_messages = monologue_prompt_from_step(step_messages)
        assert len(step_messages) > 0 and Tag.MONOLOGUE_INSTRUCTION in step_messages[-1].tags
        step_messages.append(Message(content=hint, role=Role.USER, tags={Tag.FEEDBACK, Tag.STUDENT_DROPOUT}))
        steps_with_hints[i] = step_messages
    return steps_with_hints


def steps_to_exercises(steps: list[StepMessages], out_path: Path):
    processed_steps: list[StepMessages] = []
    for step_messages in steps:
        try:
            processed_steps.append(prepare_step_for_exercise(step_messages, inplace=False))
        except RuntimeError as e:
            print(f"Error preparing step for exercise:\n{e}")

    save_steps_as_exercises(processed_steps, out_path)


def create_train_val_split(n_examples: int, seed: int = None) -> np.ndarray:
    n_train = int(0.9 * n_examples)
    n_val = n_examples - n_train
    split = np.array(["train"] * n_train + ["val"] * n_val)
    np_random = np.random.RandomState()
    if seed:
        np_random.seed(seed)
    np_random.shuffle(split)
    return split


def add_ipython_tags(steps: list[StepMessages]) -> list[StepMessages]:
    steps = copy.deepcopy(steps)
    for i, step_messages in enumerate(steps):
        for j, message in enumerate(step_messages):
            if Tag.TOOL_CALL in message.tags:
                if not message.content.startswith("<run_ipython>\n"):
                    steps[i][j].content = "<run_ipython>\n" + message.content.removeprefix("<run_ipython>")
                if not message.content.endswith("\n</run_ipython>"):
                    steps[i][j].content = message.content.removesuffix("</run_ipython>") + "\n</run_ipython>"
    return steps

# %%
if __name__ == "__main__":
    nest_asyncio.apply()
    load_dotenv()
    
    FILTERS_OUT_DIR = BASE_PATH / "filtered_steps"

    #filter_descr = "ToolQA_Graph_tool_parameters"
    #filter_descr = "ToolQA_Text_time_window"
    # filter_descr = "ToolQA_Coffee_lowest_highest_price"
    # filter_descr = "ToolQA_Yelp_appointment"
    # filter_descr = "ToolQA_Yelp_categories"
    #filter_descr = "ToolQA_Yelp_duplicate_cities"
    #filter_descr = "ToolQA_Yelp_radius"
    # filter_descr = "ToolQA_Airbnb_column_name"
    # filter_descr = "ToolQA_Airbnb_load_db"
    filter_descr = "ToolQA_Airbnb_price"
    # filter_descr = "ToolQA_Airbnb_review_rate"
    # filter_descr = "ToolQA_Flights_distance"
    # filter_descr = "ToolQA_Flights_avg_delay"
    #filter_descr = "ToolQA_Flights_time_format"
    model_name = "0114_plastic-pot"


    eval_filter = EVAL_FILTERS[filter_descr]
    filter_model_name = 'vm-ToolQA/0114_plastic-pot'
    filter_model = get_client(filter_model_name, base_url="http://localhost:8000/v1")


    if hasattr(eval_filter, "model"):
        eval_filter.model = filter_model
        eval_filter.model.extra_body["temperature"] = 0.0

    dir_patterns = [AGENT_BATCH_RUNS_PATH / '0114_plastic-pot/*']
    #dir_patterns = [AGENT_BATCH_RUNS_PATH / '0114_plastic-pot/graph-tool_parameters/*']
    #dir_patterns = [AGENT_BATCH_RUNS_PATH / '0114_plastic-pot/text-time_window/*']
    #dir_patterns = [AGENT_BATCH_RUNS_PATH / '0114_plastic-pot/coffee-lowest_highest_price/*']
    # dir_patterns = [AGENT_BATCH_RUNS_PATH / '0114_plastic-pot/yelp-appointment/*']
    # dir_patterns = [AGENT_BATCH_RUNS_PATH / '0114_plastic-pot/yelp-categories/*']
    # dir_patterns = [AGENT_BATCH_RUNS_PATH / '0114_plastic-pot/yelp-duplicate_cities/*']
    #dir_patterns = [AGENT_BATCH_RUNS_PATH / '0114_plastic-pot/yelp-radius/*']
    # dir_patterns = [AGENT_BATCH_RUNS_PATH / '0114_plastic-pot/airbnb-column_name/*']
    # dir_patterns = [AGENT_BATCH_RUNS_PATH / '0114_plastic-pot/airbnb-load_db/*']
    #dir_patterns = [AGENT_BATCH_RUNS_PATH / '0114_plastic-pot/airbnb-price/*']
    # dir_patterns = [AGENT_BATCH_RUNS_PATH / '0114_plastic-pot/airbnb-wrong_solution_review_rate/*']
    # dir_patterns = [AGENT_BATCH_RUNS_PATH / '0114_plastic-pot/flights_distance/*']
    # dir_patterns = [AGENT_BATCH_RUNS_PATH / '0114_plastic-pot/flights-delay/*']
    # dir_patterns = [AGENT_BATCH_RUNS_PATH / '0114_plastic-pot/flights-avg_delay/*']
    #dir_patterns = [AGENT_BATCH_RUNS_PATH / '0114_plastic-pot/flights-incorrect_time_format/*']

    steps = load_history_xml_dataset(dir_patterns)
    # %%
    # APPLY FILTER
    ts = time.strftime("%Y%m%d-%H%M%S")
    dataset_date = datetime.now().strftime("%m%d")
    filter_out_dir = (
        Path(FILTERS_OUT_DIR / f'{model_name}/{dataset_date}_steps_{filter_descr}')
    )
    filtered_steps_dir = filter_out_dir / "affected_steps"

    affected_steps, affected_reasons, accept_reasons = await filter_steps(steps, eval_filter)
    save_steps_dataset(affected_steps, filtered_steps_dir)
    print(len(affected_steps), "steps saved to", filtered_steps_dir)



# %%
# ToolQA
client = get_client('vm-ToolQA/0114_plastic-pot', base_url="http://localhost:8000/v1")
call_client_fn = call_client_on_monologue_and_ipython_steps
n_trials = 2

hint_graph_tool_parameter = """After loading the graph by `GRAPH_DATA = load_graph()` you can use these tools to check nodes / neighbours:
`check_nodes(GRAPH_DATA, graph_type: str, node: str)`
    Don't forget any argument: 1. graph data; 2. graph type, which is either either 'PaperNet' or 'AuthorNet'; 3. node name.
`check_neighbours(GRAPH_DATA, graph_type: str, node: str)`
    Don't forget any argument: 1. graph data; 2. graph type, which is either either 'PaperNet' or 'AuthorNet'; 3. node name.
"""
hint_text_time_window = """To determine available time windows from 9:00 AM to 6:00 PM for a meeting:
1. Read the retrieved document carefully to identify event(s) between 9:00 AM and 6:00 PM. Focus on identifying any time slots where events conflict with the potential meeting time.
2. Use reasoning in your monologue to determine available time windows. The answer should be all time slots within 9:00 AM to 6:00 PM where no event is scheduled. 
    Note: Do not use programmatic solutions to calculate or extract the answer. Consider only available time windows within 9:00 AM to 6:00 PM. 
    Example:
    If an event is from 9:30 AM to 1:00 PM, the answer would be: 9:00 AM-9:30 AM, 1:00 PM-6:00 PM.
    If an event is from 4:00 PM to 6:00 PM, the answer would be: 9:00 AM-4:00 PM.
    If an event is from 7:00 AM to 10:00 AM, the answer would be: 10:00 AM-6:00 PM.
    If an event is from 6:00 PM to 7:00 PM, the answer would be: 9:00 AM-6:00 PM. (Events beyond the range of 9:00 AM to 6:00 PM should not affect the answer.)
3. Check your answer. If you are sure that your answer is correct in both value and format, you can call `complete_task(final_report: str, return_value)` to finish the task.
"""
hint_coffee_lowest_highest_price = """After you get the value of "Low" or "High" price for filtered days, you should then find the lowest or highest price among prices of these days. For example:
`lowest_price = min([float(price) for price in low_prices.split(', ')])` or `highest_price = max([float(price) for price in high_prices.split(', ')])`.
"""
hint_yelp_appointment = """Check if "ByAppointmentOnly" is in attributes: If it does and 'ByAppointmentOnly' is 'True', the answer should be 'Yes'; If it does not have 'ByAppointmentOnly', or 'ByAppointmentOnly' is 'False', the answer should be 'No'.
Do not make your judgement based on other attributes.
"""
hint_yelp_categories = """When keeping only rows with 'categories' containing a certain business, for example Restaurants business, do not use `data_filter()`.
Instead, always remember to use the following codes: `data_business = data[data['categories'].str.contains('Restaurants')]`.  

When filter the data by 'city'/'name', you can use `data_filter()`.
"""
hint_yelp_duplicate_cities = """View these city names, and check if there are any duplicates. Your final answer should not contain duplicate city names. Do not removing duplicates programmatically.
"""
hint_yelp_radius = """
Hint on solution:
- Calculate the maximum and minimum latitude and longitude within a 5-mile radius from the business mentioned in the question, you should strictly follow these steps:
- Get the value of 'latitude', 'longitude' and 'review_count' for all businesses into variables `lats`, `lons` and `review_counts`;
- 
`lats_list = [float(lat) for lat in lats.split(', ')]` # convert to float
`lons_list = [float(lon) for lon in lons.split(', ')]` # convert to float
`review_counts_list = [int(review_count) for review_count in review_counts.split(', ')]` # convert to int
- keep only the review counts of businesses within a 5-mile radius from 'Perenn in Bay'. Remember you should not use `data_filter()` for this step.
Strictly follow this: `review_counts_within_5 = [review_counts_list[i] for i in range(len(review_counts_list)) if (lats_list[i]<=max_lat and lats_list[i] >= min_lat and lons_list[i] <= max_lon and lons_list[i] >= min_lon)]`
- Calculate the average review counts. Make sure the final answer is in a correct format.
"""
hint_airbnb_column_name = """Always remember to get the value of the column "reviews per month", not "reviews_per_month": `reviews = get_value(filtered_db, 'reviews per month')`.
"""
hint_airbnb_load_db = """This question is related to accomendation. You should load the airbnb database.
"""
hint_airbnb_price = """
Hint1: When filtering the data to get rows where 'room type' is 'Shared room', remember the column name used to filter is 'room type'.
Hint2:
After you get values of prices of filtered rows, strictly follow this step to process them:
```
prices = prices.replace('$','').replace(',','') # you must first remove ',' and '$'
prices_list = [float(price) for price in prices.split()]` # then convert to a list of float
```
"""
hint_airbnb_review_rate = """To answer this question, strictly follow these steps:
1. Filter the data only by 'neighbourhood'. Do not do it by any other columns. Then, get values of 'review rate number' of filtered rows: `rates = get_value(filtered_db, 'review rate number')`
3. Convert to a list of floating-point numbers: `rates_list = [float(rate) for rate in rates.split(', ')]`.
4. Calculate the number of reviews with a rate greater than 4.5: `num = sum([1 for i in range(len(rates_list)) if rates_list[i] >= 4])`.
"""
hint_flights_distance = """To answer this question, strictly follow these steps:
1. Filter the data only by 'FlightData'. Do not do it by any other columns.
2. Get the value of 'Distance' for filtered rows: `distances = get_value(filtered_db, 'Distance')`
3. Convert to a list of floating-point numbers: `distances_list = [float(dist) for dist in distances.split(', ')]`.
4. Calculate the number of flights with a distance greater than 300 miles: `num = sum([1 for i in range(len(distances_list)) if distances_list[i] > 300.0])`.

Solve this question in this cell.
"""
hint_flights_delay = """You should get the value of 'ArrDelayMinutes'.
"""
hint_flights_avg_delay = """Note that you should get the value of 'DepDelayMinutes'. In this cell, you should get the correct and calculate average delay time.
"""
hint_flights_incorrect_time_format = """After you get the time, do not programmatically convert the value. Instead, directly write the answer in the correct format.
For example:
- If you get '820.0', then the answer is '8:20'. (Note: Do not write as '08:20')
- If you get '1042.0', then the answer is '10:42'.
"""
# %%
# GRAPH
steps_with_hints_reponses_n_trials = []
filter_out_dir = (
    FILTERS_OUT_DIR / '0114_plastic-pot/0115_steps_ToolQA_Graph_tool_parameters'
)
affected_steps = load_filtered_steps_subset(filter_out_dir / "affected_steps")
steps_with_hints = insert_hint_before_monologue(affected_steps, hint_graph_tool_parameter)

for _ in range(n_trials):
    steps_with_hints_responses = await call_client_fn(steps_with_hints, client)
    steps_with_hints_responses_clean = add_ipython_tags(steps_with_hints_responses)
    print(steps_with_hints_responses_clean)
    steps_with_hints_reponses_n_trials += steps_with_hints_responses_clean

# %%
split_assignment = create_train_val_split(len(steps_with_hints_reponses_n_trials), seed=1)
train_steps = [step for split, step in zip(split_assignment, steps_with_hints_reponses_n_trials) if split == "train"]
val_steps = [step for split, step in zip(split_assignment, steps_with_hints_reponses_n_trials) if split == "val"]
steps_to_exercises(train_steps,  FILTERS_OUT_DIR / "0114_plastic-pot/train_exercises_with_hints_graph.xml")
steps_to_exercises(val_steps,  FILTERS_OUT_DIR / "0114_plastic-pot/val_exercises_with_hints_graph.xml")


# %%
# TEXT
steps_with_hints_reponses_n_trials = []
filter_out_dir = (
    FILTERS_OUT_DIR / '0114_plastic-pot/0115_steps_ToolQA_Text_time_window'
)
affected_steps = load_filtered_steps_subset(filter_out_dir / "affected_steps")
steps_with_hints = insert_hint_before_monologue(affected_steps, hint_text_time_window)

for _ in range(n_trials):
    steps_with_hints_responses = await call_client_fn(steps_with_hints, client)
    steps_with_hints_responses_clean = add_ipython_tags(steps_with_hints_responses)
    print(steps_with_hints_responses_clean)
    steps_with_hints_reponses_n_trials += steps_with_hints_responses_clean

# %%
split_assignment = create_train_val_split(len(steps_with_hints_reponses_n_trials), seed=1)
train_steps = [step for split, step in zip(split_assignment, steps_with_hints_reponses_n_trials) if split == "train"]
val_steps = [step for split, step in zip(split_assignment, steps_with_hints_reponses_n_trials) if split == "val"]
steps_to_exercises(train_steps,  FILTERS_OUT_DIR / "0114_plastic-pot/train_exercises_with_hints_text.xml")
steps_to_exercises(val_steps,  FILTERS_OUT_DIR / "0114_plastic-pot/val_exercises_with_hints_text.xml")



#%%
#COFFEE
steps_with_hints_reponses_n_trials = []
filter_out_dir = (
    FILTERS_OUT_DIR / '0114_plastic-pot/0115_steps_ToolQA_Coffee_lowest_highest_price'
)
affected_steps = load_filtered_steps_subset(filter_out_dir / "affected_steps")
steps_with_hints = insert_hint_before_monologue(affected_steps, hint_coffee_lowest_highest_price)
n_trials = 3
for _ in range(n_trials):
    steps_with_hints_responses = await call_client_fn(steps_with_hints, client)
    steps_with_hints_responses_clean = add_ipython_tags(steps_with_hints_responses)
    print(steps_with_hints_responses_clean)
    steps_with_hints_reponses_n_trials += steps_with_hints_responses_clean

# %%
split_assignment = create_train_val_split(len(steps_with_hints_reponses_n_trials), seed=1)
train_steps = [step for split, step in zip(split_assignment, steps_with_hints_reponses_n_trials) if split == "train"]
val_steps = [step for split, step in zip(split_assignment, steps_with_hints_reponses_n_trials) if split == "val"]
steps_to_exercises(train_steps,  FILTERS_OUT_DIR / "0114_plastic-pot/train_exercises_with_hints_coffee.xml")
steps_to_exercises(val_steps,  FILTERS_OUT_DIR / "0114_plastic-pot/val_exercises_with_hints_coffee.xml")




#%%
#Yelp
n_trials = 2
steps_with_hints_reponses_n_trials = []
filter_out_dir = (
    FILTERS_OUT_DIR / '0114_plastic-pot/0115_steps_ToolQA_Yelp_appointment'
)
affected_steps = load_filtered_steps_subset(filter_out_dir / "affected_steps")
steps_with_hints = insert_hint_before_monologue(affected_steps, hint_yelp_appointment)

for _ in range(n_trials):
    steps_with_hints_responses = await call_client_fn(steps_with_hints, client)
    steps_with_hints_responses_clean = add_ipython_tags(steps_with_hints_responses)
    print(steps_with_hints_responses_clean)
    steps_with_hints_reponses_n_trials += steps_with_hints_responses_clean
#%%
filter_out_dir = (
    FILTERS_OUT_DIR / '0114_plastic-pot/0115_steps_ToolQA_Yelp_categories'
)
affected_steps = load_filtered_steps_subset(filter_out_dir / "affected_steps")
steps_with_hints = insert_hint_before_monologue(affected_steps, hint_yelp_categories)

for _ in range(n_trials):
    steps_with_hints_responses = await call_client_fn(steps_with_hints, client)
    steps_with_hints_responses_clean = add_ipython_tags(steps_with_hints_responses)
    print(steps_with_hints_responses_clean)
    steps_with_hints_reponses_n_trials += steps_with_hints_responses_clean
#%%
filter_out_dir = (
    FILTERS_OUT_DIR / '0114_plastic-pot/0115_steps_ToolQA_Yelp_duplicate_cities'
)
affected_steps = load_filtered_steps_subset(filter_out_dir / "affected_steps")
steps_with_hints = insert_hint_before_monologue(affected_steps, hint_yelp_duplicate_cities)

for _ in range(n_trials):
    steps_with_hints_responses = await call_client_fn(steps_with_hints, client)
    steps_with_hints_responses_clean = add_ipython_tags(steps_with_hints_responses)
    print(steps_with_hints_responses_clean)
    steps_with_hints_reponses_n_trials += steps_with_hints_responses_clean
#%%
n_trials = 3
filter_out_dir = (
    FILTERS_OUT_DIR / '0114_plastic-pot/0115_steps_ToolQA_Yelp_radius'
)
affected_steps = load_filtered_steps_subset(filter_out_dir / "affected_steps")
steps_with_hints = insert_hint_before_monologue(affected_steps, hint_yelp_radius)

for _ in range(n_trials):
    steps_with_hints_responses = await call_client_fn(steps_with_hints, client)
    steps_with_hints_responses_clean = add_ipython_tags(steps_with_hints_responses)
    print(steps_with_hints_responses_clean)
    steps_with_hints_reponses_n_trials += steps_with_hints_responses_clean
# %%
split_assignment = create_train_val_split(len(steps_with_hints_reponses_n_trials), seed=1)
train_steps = [step for split, step in zip(split_assignment, steps_with_hints_reponses_n_trials) if split == "train"]
val_steps = [step for split, step in zip(split_assignment, steps_with_hints_reponses_n_trials) if split == "val"]
steps_to_exercises(train_steps,  FILTERS_OUT_DIR / "0114_plastic-pot/train_exercises_with_hints_yelp.xml")
steps_to_exercises(val_steps,  FILTERS_OUT_DIR / "0114_plastic-pot/val_exercises_with_hints_yelp.xml")



#%%
#AIRBNB
steps_with_hints_reponses_n_trials = []
filter_out_dir = (
    FILTERS_OUT_DIR / '0114_plastic-pot/0115_steps_ToolQA_Airbnb_column_name'
)
affected_steps = load_filtered_steps_subset(filter_out_dir / "affected_steps")
steps_with_hints = insert_hint_before_monologue(affected_steps, hint_airbnb_column_name)

for _ in range(n_trials):
    steps_with_hints_responses = await call_client_fn(steps_with_hints, client)
    steps_with_hints_responses_clean = add_ipython_tags(steps_with_hints_responses)
    print(steps_with_hints_responses_clean)
    steps_with_hints_reponses_n_trials += steps_with_hints_responses_clean
#%%
filter_out_dir = (
    FILTERS_OUT_DIR / '0114_plastic-pot/0115_steps_ToolQA_Airbnb_load_db'
)
affected_steps = load_filtered_steps_subset(filter_out_dir / "affected_steps")
steps_with_hints = insert_hint_before_monologue(affected_steps, hint_airbnb_load_db)

for _ in range(n_trials):
    steps_with_hints_responses = await call_client_fn(steps_with_hints, client)
    steps_with_hints_responses_clean = add_ipython_tags(steps_with_hints_responses)
    print(steps_with_hints_responses_clean)
    steps_with_hints_reponses_n_trials += steps_with_hints_responses_clean
#%%
filter_out_dir = (
    FILTERS_OUT_DIR / '0114_plastic-pot/0115_steps_ToolQA_Airbnb_price'
)
affected_steps = load_filtered_steps_subset(filter_out_dir / "affected_steps")
steps_with_hints = insert_hint_before_monologue(affected_steps, hint_airbnb_price)

for _ in range(n_trials):
    steps_with_hints_responses = await call_client_fn(steps_with_hints, client)
    steps_with_hints_responses_clean = add_ipython_tags(steps_with_hints_responses)
    print(steps_with_hints_responses_clean)
    steps_with_hints_reponses_n_trials += steps_with_hints_responses_clean
#%%
filter_out_dir = (
    FILTERS_OUT_DIR / '0114_plastic-pot/0115_steps_ToolQA_Airbnb_review_rate'
)
affected_steps = load_filtered_steps_subset(filter_out_dir / "affected_steps")
steps_with_hints = insert_hint_before_monologue(affected_steps, hint_airbnb_review_rate)

for _ in range(n_trials):
    steps_with_hints_responses = await call_client_fn(steps_with_hints, client)
    steps_with_hints_responses_clean = add_ipython_tags(steps_with_hints_responses)
    print(steps_with_hints_responses_clean)
    steps_with_hints_reponses_n_trials += steps_with_hints_responses_clean
# %%
split_assignment = create_train_val_split(len(steps_with_hints_reponses_n_trials), seed=1)
train_steps = [step for split, step in zip(split_assignment, steps_with_hints_reponses_n_trials) if split == "train"]
val_steps = [step for split, step in zip(split_assignment, steps_with_hints_reponses_n_trials) if split == "val"]
steps_to_exercises(train_steps,  FILTERS_OUT_DIR / "0114_plastic-pot/train_exercises_with_hints_airbnb.xml")
steps_to_exercises(val_steps,  FILTERS_OUT_DIR / "0114_plastic-pot/val_exercises_with_hints_airbnb.xml")


#%%
#FLIGHTS
steps_with_hints_reponses_n_trials = []
filter_out_dir = (
    FILTERS_OUT_DIR / '0114_plastic-pot/0115_steps_ToolQA_Flights_distance'
)
affected_steps = load_filtered_steps_subset(filter_out_dir / "affected_steps")
steps_with_hints = insert_hint_before_monologue(affected_steps, hint_flights_distance)

for _ in range(n_trials):
    steps_with_hints_responses = await call_client_fn(steps_with_hints, client)
    steps_with_hints_responses_clean = add_ipython_tags(steps_with_hints_responses)
    print(steps_with_hints_responses_clean)
    steps_with_hints_reponses_n_trials += steps_with_hints_responses_clean

#%%
n_trials = 3

filter_out_dir = (
    FILTERS_OUT_DIR / '0114_plastic-pot/0115_steps_ToolQA_Flights_avg_delay'
)
affected_steps = load_filtered_steps_subset(filter_out_dir / "affected_steps")
steps_with_hints = insert_hint_before_monologue(affected_steps, hint_flights_avg_delay)

for _ in range(n_trials):
    steps_with_hints_responses = await call_client_fn(steps_with_hints, client)
    steps_with_hints_responses_clean = add_ipython_tags(steps_with_hints_responses)
    print(steps_with_hints_responses_clean)
    steps_with_hints_reponses_n_trials += steps_with_hints_responses_clean

#%%
n_trials = 2
filter_out_dir = (
    FILTERS_OUT_DIR / '0114_plastic-pot/0115_steps_ToolQA_Flights_delay'
)
affected_steps = load_filtered_steps_subset(filter_out_dir / "affected_steps")
steps_with_hints = insert_hint_before_monologue(affected_steps, hint_flights_delay)

for _ in range(n_trials):
    steps_with_hints_responses = await call_client_fn(steps_with_hints, client)
    steps_with_hints_responses_clean = add_ipython_tags(steps_with_hints_responses)
    print(steps_with_hints_responses_clean)
    steps_with_hints_reponses_n_trials += steps_with_hints_responses_clean
#%%
filter_out_dir = (
    FILTERS_OUT_DIR / '0114_plastic-pot/0115_steps_ToolQA_Flights_time_format'
)
affected_steps = load_filtered_steps_subset(filter_out_dir / "affected_steps")
steps_with_hints = insert_hint_before_monologue(affected_steps, hint_flights_incorrect_time_format)

for _ in range(n_trials):
    steps_with_hints_responses = await call_client_fn(steps_with_hints, client)
    steps_with_hints_responses_clean = add_ipython_tags(steps_with_hints_responses)
    print(steps_with_hints_responses_clean)
    steps_with_hints_reponses_n_trials += steps_with_hints_responses_clean
# %%
split_assignment = create_train_val_split(len(steps_with_hints_reponses_n_trials), seed=1)
train_steps = [step for split, step in zip(split_assignment, steps_with_hints_reponses_n_trials) if split == "train"]
val_steps = [step for split, step in zip(split_assignment, steps_with_hints_reponses_n_trials) if split == "val"]
steps_to_exercises(train_steps,  FILTERS_OUT_DIR / "0114_plastic-pot/train_exercises_with_hints_flights.xml")
steps_to_exercises(val_steps,  FILTERS_OUT_DIR / "0114_plastic-pot/val_exercises_with_hints_flights.xml")
# %%
