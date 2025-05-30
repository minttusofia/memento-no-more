

prompt_ToolQA_Text_num_docs = '''
You are provided with the trajectory from an AI agent. The agent's task is to answer a question about an agenda by querying a large database. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.
The agent can use `retrieve_agenda(query: str, number_of_docs: int)` to retrieve a certain number of relevant documents for analysis. The agent can use `retrieve_agenda()` multiple times. If the answer is not found in the initial set, the agent can increase the number of documents retrieved.

However, for the following types of questions, the number of retrieved documents should be limited to a reasonable amount (i.e., not more than 10) in the agent's first call of `retrieve_agenda()`:
- Where did Art Exhibition that Paul attended take place on 2022/01/01?
- How long did Paul attend the Art Exhibition on 2022/01/01?
- Who attended the Art Exhibition between 7:00 AM and 10:00 AM on 2022/01/01 in Central Museum?
- What did Paul do from 12:30 PM to 1:30 PM on 2022/01/21?
- When did Paul attend the Art Exhibition on 2022/01/01?

These types of questions are not limit the number of retrieved documents to 10., which are asking for more general information:
- What events does Paul have on 2022/06/10 in the agenda table?
- When should I schedule a meeting with Paul from 9:00 AM to 6:00 PM on 2022/01/21 in the agenda table?

Your task is to determine whether, in the last step of the agent's trajectory, the agent retrieve no more than 10 documents in the first call of `retrieve_agenda()`, if the last step is related to the first use of `retrieve_agenda()`.
Consider only the last step when making your judgment. Earlier steps are provided for additional context but should not influence your decision.

Here is the format of the response you should strictly follow:
    ----
    <reasoning>
    Write down your reasoning here.
    </reasoning>
    <answer>
    Write down your answer here.
    Your answer should be either True or False.
    </answer>
    ----
Answer False only if the last step explicitly indicates that in the first call of `retrieve_agenda()`, the agent retrieves more than 10 documents.
Answer True if: the agent retrieves 10 or fewer documents in the first call of `retrieve_agenda()`; the last step is not related to the first use of `retrieve_agenda()`; the question is not limited to 10 documents.

Here is an example showing that the agent retrieves more than 10 documents in the first call of `retrieve_agenda()` for the question "Where did Art Exhibition that Paul attended take place on 2022/01/01?":
<example>
    <status>
    Current date and time: 2025-01-05 18:59:05
    Time elapsed since the project beginning: 0:00:00
    You are on step 1
    Resources spent so far: 0
    Number of input tokens remaining: 7989
    <status>
    <inner_monologue>
    To answer the question, I need to find the location of the Art Exhibition that Paul attended on 2022/01/01. I will use the provided tool to retrieve a subset of relevant documents for analysis. I will write an appropriate query to retrieve documents containing the keywords "Paul", and "2022/01/01".
    </inner_monologue>
    retrieved_docs = retrieve_agenda("Paul 2022/01/01", 1000)
    print(retrieved_docs)   
</example>
The expected output for this example is:
    ----
    <reasoning>
    The last step of the agent's trajectory explicitly indicates that the agent retrieves more than 10 documents in the first call of `retrieve_agenda()`. The agent retrieves 1000 documents, which exceeds the limit of 10 documents. Therefore, the answer should be False.
    </reasoning>
    <answer>
    False
    </answer>
    ----

When the last step is not related to the first use of `retrieve_agenda()`, your answer should 'False', no matter how many documents it retrieved in the previous call. Here is an example:
<example>
    <status>
    Current date and time: 2025-01-05 19:05:42
    Time elapsed since the project beginning: 0:00:00
    You are on step 1
    Resources spent so far: 0
    Number of input tokens remaining: 7991
    </status>
    <inner_monologue>
    To answer the question, I need to find the duration of Faith's visit to the Brewery tasting room on 2022/12/06. I will start by retrieving a large number of documents related to Faith and the Brewery tasting room. I will use a simple query with only the key information: "Faith attend Brewery tasting room on 2022/12/06". I will retrieve 1000 documents to ensure I have enough information to find the answer.
    </inner_monologue>
    retrieved_docs = retrieve_agenda("Faith attend Brewery tasting room on 2022/12/06", 1000)
    <status>
    Current date and time: 2025-01-05 19:06:15
    Time elapsed since the project beginning: 0:00:33
    You are on step 2
    Resources spent so far: 2
    Number of input tokens remaining: 7723
    </status>
    <inner_monologue>
    I will try once again using another query. I will use a list comprehension to filter the documents and then print the remaining documents to review them manually.
    </inner_monologue>
    retrieved_docs = retrieve_agenda("Faith Brewery tasting room on 12/06", 1000)
    docs_with_faith = [doc for doc in retrieved_docs if 'Faith' in doc]
    docs_with_brewery = [doc for doc in docs_with_faith if 'Brewery tasting room' in doc]
    docs_with_date = [doc for doc in docs_with_brewery if '2022/12/06' in doc]
    print(docs_with_date)
</example>
The expected output for this example is:
    ----
    <reasoning>
    The last step is only related to the second use of `retrieve_agenda()` and the analysis, so the answer should be True.
    </reasoning>
    <answer>
    True
    </answer>
    ----

Note that for the questions like "What events does Paul have on 2022/06/10 in the agenda table?", and "When should I schedule a meeting with Paul from 9:00 AM to 6:00 PM on 2022/01/21 in the agenda table?", the agent should not limit the number of retrieved documents to 10. Therefore, the answer should always be 'True' for these types of question.

Below is the agent's trajectory. Please make your judgment based on the last step only. The earlier steps are included as additional context.
'''


prompt_ToolQA_Text_hard_question_solution = '''You are provided with the trajectory from an AI agent. The agent's task is to answer a question about an agenda by querying a large database. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.
The agent use `retrieve_agenda(query: str, number_of_docs: int)` to retrieve a specified number of relevant documents for analysis. For complex questions, the agent must follow specific steps to find the correct answer.
Here are examples of complex questions and the required solution for retrival and filtering for relevant documents:

Questions: When should I schedule a meeting with Paul from 9:00 AM to 6:00 PM on 2023/01/01? / What events does Paul have on 2023/01/01?
    Solution:
        - `retrieved_docs = retrieve_agenda("Paul", 1000)` # Retrieve a large number of documents related to Paul.
        - `docs_with_paul = [doc for doc in retrieved_docs if 'Paul' in doc]` # Filter again to make sure these documents are related to the person 'Paul';
        - `docs = [doc for doc in docs_with_paul if 'January 1' in doc]` # Filter for documents that mention the date 'January 1'
        - `print(docs)` # Print the remaining documents to review them manually.

Your task is to determine whether the agent has followed the correct solution in the agent's last step.
Some common mistakes the agent might make include:
    1. Not retrieving a large enough number (e.g., 1000) of documents related to the person in question.
    2. Forgetting to filter the documents again to ensure relevance to the specific person (e.g., 'Paul'), which is the most frequent mistake.
    3. Incorrect Date Format: Dates must strictly follow the format "January 1". (e.g., not "January 1st," "January 1, 2022," or "2022/01/01")


Here is the format of the response you should strictly follow:
    ----
    <reasoning>
    Write down your reasoning here.
    </reasoning>
    <answer>
    Write down your answer here.
    Your answer should be either True or False.
    </answer>
    ----

Answer True if the agent has strictly followed the correct solution, or the last step is not related to retrival and filtering for relevant documents, e.g., the last step is related to the analyzing retrieved documents, etxtracting information from the document or the completion of the task.
Answer False if the agent has made any mistakes in its last step, no matter whether the agent has completed the retrival and filtering for relevant documents or not.

Below is the agent's trajectory. Please make your judgment based on the last step only. The earlier steps are included as additional context.
'''

prompt_ToolQA_yelp_appointment = """You are provided with the trajectory from an AI agent. The agent's task is to answer a question by retrieve and analysis information from a tabular database. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.
The agent's task is to check if provided business requires appointments. 
The agent can solve it by: 1. Print the attributes to view. 2. Check if "ByAppointmentOnly" is in attributes: If it does and 'ByAppointmentOnly' is 'True', the answer should be 'Yes'; If it does not have 'ByAppointmentOnly', or 'ByAppointmentOnly' is 'False', the answer should be 'No'.

Your task is to determine whether the agent has followed the correct solution and did not made this mistake in its last step: If there is no 'ByAppointmentOnly' attribute, the agent sometimes incorrectly determine its answer by viewing other attributes.

Here is the format of the response you should strictly follow:
    ----
    <reasoning>
    Write down your reasoning here.
    </reasoning>
    <answer>
    Write down your answer here.
    Your answer should be either True or False.
    </answer>
    ----

Answer True if the agent has strictly followed the correct solution, or the last step is not related to checking the values of attributes.
Answer False if the agent has made the above mistakes in its last step.

Below is the agent's trajectory. Please make your judgment based on the last step only. The earlier steps are included as additional context.
"""

prompt_ToolQA_yelp_categories = """You are provided with the trajectory from an AI agent. The agent's task is to answer a question by retrieve and analysis information from a tabular database. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.
For some questions, the agent needs to filter the rows by "categories" column. To do so, the agent shouldn't use some provided tools like `data_filter()`. Instead, the agent should use the following codes: `data_business = data[data['categories'].str.contains('Restaurants')] # keep rows related to Restaurants business`.  

Your task is to determine whether the agent has followed the correct solution in its last step.

Here is the format of the response you should strictly follow:
    ----
    <reasoning>
    Write down your reasoning here.
    </reasoning>
    <answer>
    Write down your answer here.
    Your answer should be either True or False.
    </answer>
    ----

Answer True if the agent has strictly followed the correct solution, or the last step is not related to do filtering by "categories".
Answer False if the agent has made the above mistakes in its last step.

Below is the agent's trajectory. Please make your judgment based on the last step only. The earlier steps are included as additional context.
"""

prompt_ToolQA_flights_airtime = """You are provided with the trajectory from an AI agent. The agent's task is to answer a question by retrieve and analysis information from a tabular database. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.
For some questions, the agent needs to do calculations on "AirTime". To do so, the agent should first remove the nan value from the list of airtime. The agent should do it strictly by: `air_times_list_nonnan = [air_times_list[i] for i in range(len(air_times_list)) if air_times_list[i] >= 0]`.

Your task is to determine whether the agent has followed the correct solution in its last step.

Here is the format of the response you should strictly follow:
    ----
    <reasoning>
    Write down your reasoning here.
    </reasoning>
    <answer>
    Write down your answer here.
    Your answer should be either True or False.
    </answer>
    ----

Answer True if the agent has strictly followed the correct solution, or the last step is not related to process values of airtime.
Answer False if the agent has made the above mistakes in its last step.

Below is the agent's trajectory. Please make your judgment based on the last step only. The earlier steps are included as additional context.
"""

prompt_ToolQA_graph_citations = """You are provided with the trajectory from an AI agent. The agent's task is to answer a question by retrieving information from Graph data. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.
The agent needs to determine how many papers have cited a specific paper mentioned in the question. The correct way to solve this is to check the "number of citations" attribute for the paper in question.

Your task is to determine whether the agent has followed the correct solution or if it has made a mistake in the last step. Specifically, the agent may sometimes overcomplicate the solution and fail to directly return the value of "number of citations" as the final answer.

Here is the format of the response you should strictly follow:
    ----
    <reasoning>
    Write down your reasoning here.
    </reasoning>
    <answer>
    Write down your answer here.
    Your answer should be either True or False.
    </answer>
    ----

Answer True if the agent has strictly followed the correct solution (i.e., directly returning the "number of citations for this paper"); or the last step is not related to the task (for example, graph loading or calling `complete_task()` to end the task).
Answer False if the agent made a mistake in the last step (i.e., overcomplicating the solution or failing to return the citation count directly).

Below is the agent's trajectory. Please make your judgment based on the last step only. The earlier steps are included as additional context.
"""

prompt_ToolQA_table_column_name = """You are provided with the trajectory from an AI agent. The agent's task is to answer a question by retrieve and analysis information from a tabular database. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.
When the agent needs to get a value of a column, the agent should use `get_value` method and provide the database and the correct column name as the argument. For example, `get_value(filtered_db, 'reviews per month')`.
The agent sometimes makes mistakes by using the wrong column name, e.g., ``get_value(filtered_db, 'reviews_per_month') # using a incorrect column name 'reviews_per_month' instead of 'reviews per month'``

Your task is to determine whether the agent uses `get_value` method with the correct column name in its last step.

Here is the format of the response you should strictly follow:
    ----
    <reasoning>
    Write down your reasoning here.
    </reasoning>
    <answer>
    Write down your answer here.
    Your answer should be either True or False.
    </answer>
    ----

Answer True if the agent has strictly followed the correct solution (i.e., using the correct column name in the `get_value` method); or the last step is not related to get value of a column.
Answer False if the agent has made the above mistakes in its last step.

Below is the agent's trajectory. Please make your judgment based on the last step only. The earlier steps are included as additional context.
"""

prompt_ToolQA_airbnb_load_db = """
You are provided with the trajectory from an AI agent. The agent's task is to answer a question by retrieve and analysis information from a tabular database. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.
The agent needs to load the airbnb database to start the task, e.g., `airbnb_db = load_db('airbnb')`. Sometimes, the agent makes mistakes by loading the wrong database.

Your task is to determine whether the agent has loaded the correct database in its last step.

Here is the format of the response you should strictly follow:
    ----
    <reasoning>
    Write down your reasoning here.
    </reasoning>
    <answer>
    Write down your answer here.
    Your answer should be either True or False.
    </answer>
    ----

Answer True if the agent has strictly followed the correct solution (i.e., loading the correct database); or the last step is not related to loading the database.
Answer False if the agent has made the above mistakes in its last step.

Below is the agent's trajectory. Please make your judgment based on the last step only. The earlier steps are included as additional context.
"""

prompt_ToolQA_airbnb_price = """
You are provided with the trajectory from an AI agent. The agent's task is to answer a question by retrieve and analysis information from a tabular database. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.
For some questions, the agent needs to get the value of 'price', process it, and split it into a list of float. The correct way is: 
```
prices = prices.replace('$','').replace(',','') # the agent must first remove ',' and '$'
prices_list = [float(price) for price in prices.split()]` # then convert to a list of float
```

Your task is to determine whether the agent has followed the correct solution in its last step.

Here is the format of the response you should strictly follow:
    ----
    <reasoning>
    Write down your reasoning here.
    </reasoning>
    <answer>
    Write down your answer here.
    Your answer should be either True or False.
    </answer>
    ----

Answer True if the agent has strictly followed the correct solution (i.e., processing the 'price' correctly); or the last step is not related to processing the 'price'.
Answer False if the last step is related to processing the 'price', but the agent has not followed the correct solution in its last step.

Below is the agent's trajectory. Please make your judgment based on the last step only. The earlier steps are included as additional context.
"""

prompt_ToolQA_airbnb_review_rate = """
You are provided with the trajectory from an AI agent. The agent's task is to answer a question by retrieve and analysis information from a tabular database. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.
For the question about the number of airbnbs that have a review rate not lower than 4, the agent needs to:
1. Get values of 'review rate number' of filtered rows: `rates = get_value(filtered_db, 'review rate number')`
2. Convert to a list of floating-point numbers: `rates_list = [float(rate) for rate in rates.split(', ')]`.
3. Calculate the number of reviews with a rate greater than 4: `num = sum([1 for i in range(len(rates_list)) if rates_list[i] >= 4])`.

Your task is to determine whether the agent has strictly followed the correct solution in its last step.

Here is the format of the response you should strictly follow:
    ----
    <reasoning>
    Write down your reasoning here.
    </reasoning>
    <answer>
    Write down your answer here.
    Your answer should be either True or False.
    </answer>
    ----

Answer True if the agent has strictly followed the correct solution (i.e., calculating the number of airbnbs with a review rate greater than 4); or the last step is not related to this calculation.
Answer False if the last step is related to this calculation, but the agent has not followed the correct solution in its last step.

Below is the agent's trajectory. Please make your judgment based on the last step only. The earlier steps are included as additional context.
"""

prompt_ToolQA_coffee_lowest_highest_price = """
You are provided with the trajectory from an AI agent. The agent's task is to answer a question by retrieve and analysis information from a tabular database. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.
For the question about the highest or lowest price of coffee, the agent needs to get values of 'High' or 'Low'. Then, it should identify the lowest or highest price among these values.
However, the agent sometimes makes an error by returning a value from the 'High' or 'Low' column without actually determining the highest or lowest price.

Your task is to determine whether the agent correctly identified the lowest or highest price of coffee in its last step.

Here is the format of the response you should strictly follow:
    ----
    <reasoning>
    Write down your reasoning here.
    </reasoning>
    <answer>
    Write down your answer here.
    Your answer should be either True or False.
    </answer>
    ----

Answer True if the agent correctly determined the lowest or highest price of coffee OR if the last step is unrelated to this calculation.
Answer False if the agent's last step was related to this calculation but failed to determine the lowest or highest price.
"""

prompt_ToolQA_flights_distance = """
You are provided with the trajectory from an AI agent. The agent's task is to answer a question by retrieve and analysis information from a tabular database. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.

For the question about the number of flights with a distance greater than 300 miles, after getting the value of 'Distance', the agent should:
1. Convert to a list of floating-point numbers: `distances_list = [float(dist) for dist in distances.split(', ')]`.
2. Calculate the number of flights with a distance greater than 300 miles: `num = sum([1 for i in range(len(distances_list)) if distances_list[i] > 300.0])`.
However, the agent sometimes incorrectly uses `data_filter()` to filter rows where distance is greater than 300 miles. This is not the correct approach for this calculation.

Your task is to determine whether the agent has strictly followed the correct solution in its last step.

Here is the format of the response you should strictly follow:
    ----
    <reasoning>
    Write down your reasoning here.
    </reasoning>
    <answer>
    Write down your answer here.
    Your answer should be either True or False.
    </answer>
    ----

Answer True if the agent has strictly followed the correct solution (i.e., calculating the number of flights with a distance greater than 300 miles); or the last step is not related to this calculation.
Answer False if the last step is related to this calculation, but the agent has not followed the correct solution in its last step.

Below is the agent's trajectory. Please make your judgment based on the last step only. The earlier steps are included as additional context.
"""

prompt_ToolQA_flights_delay_minutes = """
You are provided with the trajectory from an AI agent. The agent's task is to answer a question by retrieve and analysis information from a tabular database. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.

For the question about the average delay time of all the flights, or the question about how long did a flight delay when arrival on a specific date, the agent must get the value of 'DepDelayMinutes' or 'ArrDelayMinutes'. 
However, the agent sometimes incorrectly attempts to get the value of other columns, such as 'DepDelay' or 'ArrDelay', which are not the correct columns.

Your task is to determine whether the agent accessed 'DepDelayMinutes' or 'ArrDelayMinutes' in its last step.

Here is the format of the response you should strictly follow:
    ----
    <reasoning>
    Write down your reasoning here.
    </reasoning>
    <answer>
    Write down your answer here.
    Your answer should be either True or False.
    </answer>
    ----

Answer True if the agent has strictly followed the correct solution (i.e., getting the value of 'DepDelayMinutes' or 'ArrDelayMinutes'); or the last step is not related to use `get_value()`.
Answer False if the agent incorrectly retrieves other incorrect columns in its last step.

Below is the agent's trajectory. Please make your judgment based on the last step only. The earlier steps are included as additional context.
"""

prompt_ToolQA_flights_incorret_time_format = """
You are provided with the trajectory from an AI agent. The agent's task is to answer a question by retrieve and analysis information from a tabular database. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.

For the question about local arrival time/CRS-recorded arrival time/departure time, after getting the corresponding value, the agent should not programmatically convert the time format. Instead, the agent must directly write the answer in the correct format.
For example,
- If the agent gets '820.0', then the answer is '8:20'. (Note: Do not write as '08:20')
- If the agent gets '1042.0', then the answer is '10:42'.

Your task is to determine, in the last step, whether the agent has followed the correct solution and not made the following mistakes:
1. Converting the time format programmatically.
2. Writing the time in the wrong format (e.g., '08:20' instead of '8:20').

Here is the format of the response you should strictly follow:
    ----
    <reasoning>
    Write down your reasoning here.
    </reasoning>
    <answer>
    Write down your answer here.
    Your answer should be either True or False.
    </answer>
    ----

Answer True if the agent has strictly followed the correct solution and not made above mistakes; or the last step is not related to time format.
Answer False if the agent has made the above mistakes in its last step.

Below is the agent's trajectory. Please make your judgment based on the last step only. The earlier steps are included as additional context.
"""

prompt_ToolQA_graph_tool_parameters = """
You are provided with the trajectory from an AI agent. The agent's task is to answer a question by retrieving information from a graph data structure. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.

The agent should first load the graph data using the `load_graph()` method. Then, use the following tools to check nodes / neighbours:
`check_nodes(GRAPH_DATA, graph_type: str, node: str)`
    input arguments: 1. graph data; 2. graph type, which is either either 'PaperNet' or 'AuthorNet'; 3. node name.
`check_neighbours(GRAPH_DATA, graph_type: str, node: str)`
    input arguments: 1. graph data; 2. graph type, which is either either 'PaperNet' or 'AuthorNet'; 3. node name.

Some common mistakes the agent might make include:
1. Forgetting to load the graph data before checking nodes or neighbours.
2.
```
GRAPH_DATA = load_graph()
paper_attributes = check_nodes(GRAPH_DATA, 'Paper', 'Machine Learning')  # Incorrect argument 'Paper'; should be 'PaperNet'
```
3.
```
GRAPH_DATA = load_graph()
check_nodes(GRAPH_DATA, 'Machine Learning') # Missing the graph type argument
```

Your task is to determine whether the agent has not made the above mistakes.

Here is the format of the response you should strictly follow:
    ----
    <reasoning>
    Write down your reasoning here.
    </reasoning>
    <answer>
    Write down your answer here.
    Your answer should be either True or False.
    </answer>
    ----

Answer True if the agent has not made the above mistakes; or the last step is not related to checking nodes or neighbours.
Answer False if the agent has made the above mistakes in its last step.

Below is the agent's trajectory. Please make your judgment based on the last step only. The earlier steps are included as additional context.
"""

prompt_ToolQA_yelp_duplicate_cities = """
You are provided with the trajectory from an AI agent. The agent's task is to answer a question by retrieve and analysis information from a tabular database. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.

For this question, before returning the final answer using `complete_task()`, the agent should check if there are duplicate cities in the answer, and remove duplicates if there are any.

Your task is to determine whether the agent's final answer contains duplicate cities or not.

Here is the format of the response you should strictly follow:
    ----
    <reasoning>
    Write down your reasoning here.
    </reasoning>
    <answer>
    Write down your answer here.
    Your answer should be either True or False.
    </answer>
    ----

Answer True if the agent's final answer does not contain duplicate cities; or the last step is not related to return the final answer using `complete_task()`.
Answer False if the agent's final answer contains duplicate cities.

Below is the agent's trajectory. Please make your judgment based on the last step only. The earlier steps are included as additional context.
"""
prompt_ToolQA_yelp_radius = """
You are provided with the trajectory from an AI agent. The agent's task is to answer a question by retrieve and analysis information from a tabular database. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.

For the question about the average review counts of businesses within a 5-mile radius from a given business, the agent should:
1. Calculate the maximum and minimum latitude and longitude within a 5-mile radius from the business mentioned in the question.
2. Get values of 'latitude', 'longitude' and 'review_count' for all businesses, and convert them into lists of float or integer, respectively, e.g., `lats_list`, ``longs_list` and `review_counts_list`.
3. Keep only the review counts of businesses within a 5-mile radius by: `review_counts_within_5 = [review_counts_list[i] for i in range(len(review_counts_list)) if (lats_list[i]<=max_lat and lats_list[i] >= min_lat and lons_list[i] <= max_lon and lons_list[i] >= min_lon)]`.
4. Calculate the average review counts.

The agent sometimes incorrectly uses `data_filter()` to filter the review counts of businesses within a 5-mile radius, e.g., `filtered_db = data_filter(yelp_db, f'latitude<=max_lat; latitude>=min_lat; longitude<=max_lon; longitude>=min_lon')`.
This is not the correct approach.

Your task is to determine whether the agent has strictly followed the correct solution in its last step, where the agent should not use `data_filter()` to filter the review counts of businesses within a 5-mile radius.

Here is the format of the response you should strictly follow:
    ----
    <reasoning>
    Write down your reasoning here.
    </reasoning>
    <answer>
    Write down your answer here.
    Your answer should be either True or False.
    </answer>
    ----

Answer True if the agent has strictly followed the correct solution (i.e., not using `data_filter()` to filter the review counts of businesses within a 5-mile radius); or the last step is not related to this calculation.
Answer False if the last step is related to this calculation, but the agent has not followed the correct solution in its last step, i.e., using `data_filter()` to filter the review counts of businesses within a 5-mile radius.

Below is the agent's trajectory. Please make your judgment based on the last step only. The earlier steps are included as additional context.
"""

prompt_ToolQA_format_conversion = """
You are provided with the trajectory from an AI agent. The agent's task is to answer a question by retrieve and analysis information from a tabular database. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.

For some questions, the agent needs to convert the format of the answer. For example,  converting the 'time' to 'HH:mm'; converting the 'price' to a string representing an integer.
However, the agent should not perform this formatting programmatically. Instead, it must directly write the final answer in the required format.

Your task is to determine, in the last step, whether the agent correctly wrote the answer in the required format without applying formatting programmatically.

Here is the format of the response you should strictly follow:
    ----
    <reasoning>
    Write down your reasoning here.
    </reasoning>
    <answer>
    Write down your answer here.
    Your answer should be either True or False.
    </answer>
    ----

Answer True if the agent correctly wrote the answer in the required format and did not format it programmatically, or if the final step is unrelated to formatting.
Answer False if the agent formatted the answer programmatically in its last step.

Below is the agent's trajectory. Please make your judgment based on the last step only. The earlier steps are included as additional context.
"""

prompt_ToolQA_airbnb_id = """
You are provided with the trajectory from an AI agent. The agent's task is to answer a question by retrieve and analysis information from a tabular database. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.

If a question explicitly mentions the 'id' of an Airbnb listing, the agent must ensure that it filters the data by the 'id' column when using `data_filter()`.
For example, for the question 'How many reviews does Modern Manhattan Living Suite 2A (id: 3654033) in Harlem have?', the agent should use `data_filter(airbnb_db, 'NAME=Modern Manhattan Living Suite 2A; neighbourhood=Harlem'; id=3654033)`.
However, the agent sometimes forgets to filter by the 'id' column, which leads to incorrect results.

Your task is to determine whether the agent has correctly filtered the row by the 'id' column in its last step if needed.

Here is the format of the response you should strictly follow:
    ----
    <reasoning>
    Write down your reasoning here.
    </reasoning>
    <answer>
    Write down your answer here.
    Your answer should be either True or False.
    </answer>
    ----

Answer True if the agent has correctly filtered the row by the 'id' column in its last step if needed; or the last step is not related to filtering.
Answer False if the agent forgot to filtered by the 'id' column in its last step when needed.

Below is the agent's trajectory. Please make your judgment based on the last step only. The earlier steps are included as additional context.
"""

prompt_ToolQA_coffee_date_missing = """
You are provided with the trajectory from an AI agent. The agent's task is to answer a question by retrieve and analysis information from a tabular database. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.

For the question about the average coffee price from Date1 to Date2, the agent should filter the data by "Date>=Date1; Date<=Date2: `data_filter(coffee_db, 'Date>=Date1; Date<=Date2')`.
However, the agent sometimes forgets to filter the data incorrectly, e.g., `data_filter(coffee_db, 'Date>Date1; Date<Date2')`.

Your task is to determine whether the agent has correctly filtered the data by the date range and not made the above mistake in its last step.

Here is the format of the response you should strictly follow:
    ----
    <reasoning>
    Write down your reasoning here.
    </reasoning>
    <answer>
    Write down your answer here.
    Your answer should be either True or False.
    </answer>
    ----

Answer True if the agent has correctly filtered the data by the date range and not made the above mistake in its last step; or the last step is not related to filtering by the date range.
Answer False if the agent has made the above mistake in its last step.

Below is the agent's trajectory. Please make your judgment based on the last step only. The earlier steps are included as additional context.
"""

prompt_ToolQA_printing = """
You are provided with the trajectory from an AI agent. The agent's task is to answer a question by retrieve and analysis information from a tabular database. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.

The agent can use `get_value()` method to get the value of a specific column. After getting the value, the agent should print the value to check if it is correct. The agent sometimes forgets to print the value after getting it.

Your task is to determine whether the agent has printed the value after getting it in its last step.

Here is the format of the response you should strictly follow:
    ----
    <reasoning>
    Write down your reasoning here.
    </reasoning>
    <answer>
    Write down your answer here.
    Your answer should be either True or False.
    </answer>
    ----

Answer True if the agent has printed the value after getting it in its last step; or the last step is not related to getting the value.
Answer False if the agent has not printed the value after getting it in its last step.

Below is the agent's trajectory. Please make your judgment based on the last step only. The earlier steps are included as additional context.
"""

prompt_ToolQA_flights_diverted = """
You are provided with the trajectory from an AI agent. The agent's task is to answer a question by retrieve and analysis information from a tabular database. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.

For the question about the number of flights that were diverted, the agent should:
1. Filter the data by 'Diverted' is 'True' and 'FlightDate', e.g., `filtered_db = data_filter(flights_db, 'Diverted=True; FlightDate=2020-01-01')`
2. Count the number of rows in the filtered data as the final answer.

Your task is to determine whether the agent has strictly followed the correct solution in its last step.

Here is the format of the response you should strictly follow:
    ----
    <reasoning>
    Write down your reasoning here.
    </reasoning>
    <answer>
    Write down your answer here.
    Your answer should be either True or False.
    </answer>
    ----

Answer True if the agent has strictly followed the correct solution; or the agent has not yet completed all required operations; or  its last step is unrelated to filtering/counting rows.
Answer False if the agent has not followed the correct solution in its last step.

Below is the agent's trajectory. Please make your judgment based on the last step only. The earlier steps are included as additional context.
"""

prompt_ToolQA_flights_speed = """
You are provided with the trajectory from an AI agent. The agent's task is to answer a question by retrieve and analysis information from a tabular database. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.

For the question about the average speed of flights, the agent should remember to remove the 'nan' values from the list of airtime, and corresponding values in the list of distance by using the following code:
```air_times_list_nonnan = [air_times_list[i] for i in range(len(air_times_list)) if air_times_list[i] >= 0]
distances_list_nonnan = [distances_list[i] for i in range(len(air_times_list)) if air_times_list[i] >= 0]
```

However, the agent sometimes made mistakes:
1. The agent forgets to remove 'nan' values from the list of airtime.
2. The agent forgets to remove corresponding values from the list of distance.
3. The agent attempts to remove the 'nan' values in an incorrect way which is different from the provided code.

Your task is to determine whether the agent has followed the correct solution in its last step.

Here is the format of the response you should strictly follow:
    ----
    <reasoning>
    Write down your reasoning here.
    </reasoning>
    <answer>
    Write down your answer here.
    Your answer should be either True or False.
    </answer>
    ----

Answer True if the agent has strictly followed the correct solution; or the last step is not related to processing values of airtime and distance.
Answer False if the agent has made the above mistakes in its last step.

Below is the agent's trajectory. Please make your judgment based on the last step only. The earlier steps are included as additional context.
"""

prompt_ToolQA_graph_loading = """
You are provided with the trajectory from an AI agent. The agent's task is to answer a question by retrieving information from a graph data structure. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.

The agent should first load the graph data using the `load_graph()` method.
However, the agent sometimes forgets to load the graph data before performing other operations on the graph data.

Your task is to determine whether the agent has loaded the graph data in its last step.

Here is the format of the response you should strictly follow:
    ----
    <reasoning>
    Write down your reasoning here.
    </reasoning>
    <answer>
    Write down your answer here.
    Your answer should be either True or False.
    </answer>
    ----

Answer True if the agent has loaded the graph data in its last step; or the last step is not related to loading the graph data; or the agent has correctly loaded the graph data in an earlier step.
Answer False if the agent has not loaded the graph data in its last step.

Below is the agent's trajectory. Please make your judgment based on the last step only. The earlier steps are included as additional context.
"""

prompt_ToolQA_graph_name = """
You are provided with the trajectory from an AI agent. The agent's task is to answer a question by retrieving information from a graph data structure. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.

When the agent uses `check_node()` method to check the attributes of a node, the agent should provide the the exact same name of the author or paper as they are shown in the question in the last step.

Your task is to determine, when using `check_node()` method, whether the agent has provided the extact same name of the author or paper in its last step as they are shown in the question. 

Here is the format of the response you should strictly follow:
    ----
    <reasoning>
    Write down your reasoning here.
    </reasoning>
    <answer>
    Write down your answer here.
    Your answer should be either True or False.
    </answer>
    ----

Answer True if the agent has provided the exact name of the author or paper in its last step; or the last step is not related to checking the attributes of a node.
Answer False if the agent has not provided the exact same name of the author or paper as they are shown in the question in its last step.

Below is the agent's trajectory. Please make your judgment based on the last step only. The earlier steps are included as additional context.
"""

prompt_ToolQA_text_printing = """
You are provided with the trajectory from an AI agent. The agent's task is to answer a question about an agenda by querying a large database. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.

The agent use `retrieve_agenda(query: str, number_of_docs: int)` to retrieve a specified number of relevant documents for analysis.
If the agent retrieves only a small number of documents, e.g., 10, it should print them to view the content.

Your task is to determine whether the agent has printed the retrieved documents in its last step.

Here is the format of the response you should strictly follow:
    ----
    <reasoning>
    Write down your reasoning here.
    </reasoning>
    <answer>
    Write down your answer here.
    Your answer should be either True or False.
    </answer>
    ----

Answer True if the agent has printed the retrieved documents in its last step; or the last step is not related to printing the retrieved documents; or the agent has retrieved a large number of documents where it is not necessary to print them.
Answer False if the agent has not printed the retrieved documents in its last step.

Below is the agent's trajectory. Please make your judgment based on the last step only. The earlier steps are included as additional context.
"""

TOOLQA_PROMPTS = {
'ToolQA_Text_num_docs': prompt_ToolQA_Text_num_docs,
'ToolQA_Text_hard_question_solution': prompt_ToolQA_Text_hard_question_solution,
'ToolQA_yelp_appointment': prompt_ToolQA_yelp_appointment,
'ToolQA_yelp_categories': prompt_ToolQA_yelp_categories,
'ToolQA_flights_airtime': prompt_ToolQA_flights_airtime,
'ToolQA_graph_citations': prompt_ToolQA_graph_citations,
'ToolQA_table_column_name': prompt_ToolQA_table_column_name,
'ToolQA_airbnb_load_db': prompt_ToolQA_airbnb_load_db,
'ToolQA_airbnb_price': prompt_ToolQA_airbnb_price,
'ToolQA_airbnb_review_rate': prompt_ToolQA_airbnb_review_rate,
'ToolQA_coffee_lowest_highest_price': prompt_ToolQA_coffee_lowest_highest_price,
'ToolQA_flights_distance': prompt_ToolQA_flights_distance,
'ToolQA_flights_delay_minutes': prompt_ToolQA_flights_delay_minutes,
'ToolQA_flights_incorret_time_format': prompt_ToolQA_flights_incorret_time_format,
'ToolQA_graph_tool_parameters': prompt_ToolQA_graph_tool_parameters,
'ToolQA_yelp_duplicate_cities': prompt_ToolQA_yelp_duplicate_cities,
'ToolQA_yelp_radius': prompt_ToolQA_yelp_radius,
'ToolQA_format_conversion': prompt_ToolQA_format_conversion,
'ToolQA_airbnb_id': prompt_ToolQA_airbnb_id,
'ToolQA_coffee_date_missing': prompt_ToolQA_coffee_date_missing,
'ToolQA_printing': prompt_ToolQA_printing,
'ToolQA_flights_diverted': prompt_ToolQA_flights_diverted,
'ToolQA_flights_speed': prompt_ToolQA_flights_speed,
'ToolQA_graph_loading': prompt_ToolQA_graph_loading,  
'ToolQA_graph_name': prompt_ToolQA_graph_name,
'ToolQA_text_printing': prompt_ToolQA_text_printing
}   