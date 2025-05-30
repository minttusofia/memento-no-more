from agent.configs import AgentEngineConfig, PromptConfig
from agent.tips import GUIDELINES
from tasks.taskset import TaskSet

from tasks.t_ToolQA.combined_hints.hints import HINTS
from tasks.t_ToolQA.combined_hints.hints_deepseekv3 import HINTS as HINTS_DEEPSEEKV3
from tasks.t_ToolQA.combined_hints.hints_gpt4o import HINTS as HINTS_GPT4o


def graph_task(level: str = 'easy', all_tools: bool = True, question_index: int = 0, number_of_questions: int = 100, use_generic_task_description: bool = True, n_trials: int = 1) -> TaskSet:
    """
    level: ['easy', 'hard', 'all', 'train', 'val', 'test'],
    all_tools: True if all tools are provided to the agent; False if only the graph tools are provided
    use_generic_task_description: True if use generic task description; False if use specific task description
    """
    from agent.tools_python import complete_task
    from tasks.t_ToolQA.t_graph_task.t_graph_task import (
        GraphTask,
        action_tips,
        reasoning_tips,
        answer_tips,
        step_by_step_tips,
        finalization_tips,
        hint_paper,
        hint_citation,
        hint_most_cited,
        hint_collaborations,
        hint_all_collaborations,
        hint_institution,
    )
    from tasks.t_ToolQA.t_graph_task.utils import DATA_BASE_DIR, read_qa

    question_answer = read_qa(DATA_BASE_DIR / f'{level}/dblp-{level}.jsonl') # (questions, answers)
    tasks = GraphTask.generate_variants(question_answer, level, question_index, number_of_questions,)

    if use_generic_task_description:
        for task in tasks:
            task_descriptions = """In this task, you are asked to answer a question by retrieving information from an external database. You can use provided tools to assist in exploring the database.\n\nHere is the question:\n"""
            
            task.task = task_descriptions + task.task_question
    
    from tasks.t_ToolQA.tools import data_filter, get_value, check_edges, check_nodes, check_neighbours, mock_retrieve_agenda, mock_load_graph, mock_load_mock_db
    
    if all_tools:

        tool_docs = ["load_db", "data_filter", "get_value", "load_graph", "check_nodes", "check_neighbours", "check_edges", "retrieve_agenda", "complete_task",]
        
        tool_functions = {
                "load_db": mock_load_mock_db,
                "data_filter": data_filter,
                "get_value": get_value,
                "load_graph": mock_load_graph,
                "check_nodes": check_nodes,
                "check_neighbours": check_neighbours,
                "check_edges": check_edges,
                "retrieve_agenda": mock_retrieve_agenda,
                "complete_task" : complete_task,
                }

        from tasks.t_ToolQA.modify_agent import modify_agent
        
    else:
        tool_docs = ["load_graph", "check_nodes", "check_neighbours", "check_edges", "complete_task",]

        tool_functions = {
            "load_graph": mock_load_graph,
            "check_nodes": check_nodes,
            "check_neighbours": check_neighbours,
            "check_edges": check_edges,
            "complete_task" : complete_task,
        }
        from tasks.t_ToolQA.t_graph_task.t_graph_task import modify_agent

    prompt_config = []
    for task in tasks:
        guidelines = []
        guidelines.append(GUIDELINES["response_format"])
        guidelines.append(step_by_step_tips)
        if level == 'train':
            if task.question_variant >= 18 and task.question_variant < 24: # How many papers in the DBLP citation network cited 
                guidelines.append(hint_citation)
            if task.question_variant >= 30 and task.question_variant < 36: # How many papers did Xianhao Jin and Francisco Servant write together
                guidelines.append(hint_collaborations)
            if task.question_variant >= 36 and task.question_variant < 48: # What papers did Rama Syamala Sreepada write / How many papers did Yuheng Deng write
                guidelines.append(hint_paper)
            if task.question_variant >= 56 and task.question_variant < 64: # Which is/are the most cited paper(s) written by
                guidelines.append(hint_paper)
                guidelines.append(hint_most_cited)
            if task.question_variant >= 64 and task.question_variant < 72: # Which co-author of Moustafa H. Aly has the highest total citations
                guidelines.append(hint_paper)
            if task.question_variant >= 72 and task.question_variant < 80: # How many accumulated citations
                guidelines.append(hint_collaborations)
                #guidelines.append(hint_accumulation_citations)
            if task.question_variant >= 80 and task.question_variant < 88: # "What is the total number of papers authored by
                guidelines.append(hint_all_collaborations)
            if task.question_variant >= 88 and task.question_variant < 96: # Who collaborated with Jiaguo Liu most
                guidelines.append(hint_paper)
            if task.question_variant >= 96 and task.question_variant < 104: # What institutions participated in 
                guidelines.append(hint_institution)
        elif level == 'val':
            if task.question_variant == 3:
                guidelines.append(hint_citation)
            if task.question_variant == 5:
                guidelines.append(hint_collaborations)
            if task.question_variant == 6 or task.question_variant == 7:
                guidelines.append(hint_paper)
            if task.question_variant == 9:
                guidelines.append(hint_paper)
                guidelines.append(hint_most_cited)
            if task.question_variant == 10:
                guidelines.append(hint_paper)
            if task.question_variant == 11:
                guidelines.append(hint_collaborations)
            if task.question_variant == 12:
                guidelines.append(hint_all_collaborations)
            if task.question_variant == 13:
                guidelines.append(hint_paper)
            if task.question_variant == 14:
                guidelines.append(hint_institution)
        elif level == 'test':
            if task.question_variant >= 9 and task.question_variant < 12:
                guidelines.append(hint_citation)
            if task.question_variant >= 15 and task.question_variant < 18:
                guidelines.append(hint_collaborations)
            if task.question_variant >= 18 and task.question_variant < 24:
                guidelines.append(hint_paper)
            if task.question_variant >= 29 and task.question_variant < 34:
                guidelines.append(hint_paper)
                guidelines.append(hint_most_cited)
            if task.question_variant >= 34 and task.question_variant < 39:
                guidelines.append(hint_paper)
                # guidelines.append(hint_graph_duplicate_citations)
            if task.question_variant >= 39 and task.question_variant < 44:
                guidelines.append(hint_collaborations)
                #guidelines.append(hint_accumulation_citations)
            if task.question_variant >= 44 and task.question_variant < 49:
                guidelines.append(hint_all_collaborations)
            if task.question_variant >= 49 and task.question_variant < 54:
                guidelines.append(hint_paper)
            if task.question_variant >= 54 and task.question_variant < 59:
                guidelines.append(hint_institution)
        else:
            guidelines.append(hint_paper)

        guidelines.append(action_tips)
        guidelines.append(reasoning_tips)
        guidelines.append(answer_tips)
        guidelines.append(finalization_tips)
        
        prompt_config.append(PromptConfig(
            guidelines=guidelines,
            tool_docs="long",
            tool_docs_list=tool_docs,
        ))

    engine_config = AgentEngineConfig(
        tools=tool_functions,
        modify_agent=modify_agent,
    )

    taskset_name = f"graph_task_{level}" + ("_full_list" if all_tools else "") + ("_generic" if use_generic_task_description else "")

    return TaskSet(taskset_name, tasks, prompt_config, engine_config).repeat(n_trials)

def graph_task_test(level: str = 'test', tools: str = 'none', question_index: int = 0, number_of_questions: int = 100, use_combined_guidelines: bool = True, combined_hints_model: str = 'llama3.1-70b', n_trials: int = 1) -> TaskSet:
    """
    Use this function to test models on graph task without guidelines
    
    level: 'test'
    tools: ['none', 'relevant', 'relevant-long', 'all', 'all-long']
            'none': none of tools' names/documentation is provided;
            'relevant': only the relevant tools' names are provided;
            'relevant-long': only the relevant tools' names and docs are provided;
            'all': all tools' names are provided 
            'all-long': all tools' names are provided with long documentation
    use_combined_guidelines: True if combined guidelines are used; False otherwise
        False: without guidelines
        True: with combined guidelines + all tools' documentation
    combined_hints_model: ['llama3.1-70b', 'deepseek-chat', 'gpt-4o']
        if combined hints is True, the model whose optimized hints to use
    """
    from agent.tools_python import complete_task
    from tasks.t_ToolQA.t_graph_task.t_graph_task import (
        GraphTask,
    )
    from tasks.t_ToolQA.t_graph_task.utils import DATA_BASE_DIR, read_qa

    question_answer = read_qa(DATA_BASE_DIR / f'{level}/dblp-{level}.jsonl') # (questions, answers)
    tasks = GraphTask.generate_variants(question_answer, level, question_index, number_of_questions,)

    for task in tasks:
        task_descriptions = """In this task, you are asked to answer a question by retrieving information from an external database. You can use provided tools to assist in exploring the database.\n\nHere is the question:\n"""
        task.task = task_descriptions + task.task_question
    
    from tasks.t_ToolQA.tools import data_filter, get_value, check_edges, check_nodes, check_neighbours, mock_retrieve_agenda, mock_load_graph, mock_load_mock_db

    tool_functions = {
                "load_db": mock_load_mock_db,
                "data_filter": data_filter,
                "get_value": get_value,
                "load_graph": mock_load_graph,
                "check_nodes": check_nodes,
                "check_neighbours": check_neighbours,
                "check_edges": check_edges,
                "retrieve_agenda": mock_retrieve_agenda,
                "complete_task" : complete_task,
                }

    from tasks.t_ToolQA.modify_agent import modify_agent

    engine_config = AgentEngineConfig(
        tools=tool_functions,
        modify_agent=modify_agent,
    )

    if use_combined_guidelines:
        tools = 'all-long'
        if combined_hints_model == "llama3.1-70b":
            hints_list = list(HINTS.values())
        elif combined_hints_model == "gpt-4o":
            hints_list = list(HINTS_GPT4o.values())
        elif combined_hints_model == "deepseek-chat":
            hints_list = list(HINTS_DEEPSEEKV3.values())
        else:
            raise ValueError(f"Unknown model: {combined_hints_model}")

    if tools == 'none':
        prompt_config = PromptConfig(
                guidelines=None,
                tool_docs="none",
                monologue_format=False,
                tool_call_format=False,
            )

    else:
        tool_docs_list = ["load_graph", "check_nodes", "check_neighbours", "check_edges", "complete_task",] if (tools == 'relevant' or tools == 'relevant-long') else ["load_db", "data_filter", "get_value", "load_graph", "check_nodes", "check_neighbours", "check_edges", "retrieve_agenda", "complete_task",]

        if use_combined_guidelines:
            prompt_config = PromptConfig(
                guidelines=hints_list,
                tool_docs="long",
                tool_docs_list=tool_docs_list,
                monologue_format=True,
                tool_call_format=True,
            )
        else:
            if tools == 'all' or tools == 'relevant':
                prompt_config = PromptConfig(
                    guidelines=None,
                    tool_docs="short", # only show the tool names
                    tool_docs_list=tool_docs_list,
                    monologue_format=False,
                    tool_call_format=False,
                )
            elif tools == 'all-long' or tools == 'relevant-long':
                prompt_config = PromptConfig(
                    guidelines=None,
                    tool_docs="long", 
                    tool_docs_list=tool_docs_list,
                    monologue_format=False,
                    tool_call_format=False,
                )

    taskset_name = f"graph_task_{level}_{tools}_tools{'+combined_guidelines' if use_combined_guidelines else ''}" 

    return TaskSet(taskset_name, tasks, prompt_config, engine_config).repeat(n_trials)



def table_task(db_variant: str = 'flights', level: str = 'easy', all_tools: bool = True, question_index: int = 0, number_of_questions: int = 100, format_tips: bool = True, custom_init_script: bool = False, basic_normalization: bool = True, use_generic_task_description: bool = True, n_trials: int = 1) -> TaskSet:
    """
    This function is used to generate evaluation records as training data for the student agent.

    db_variant: ['flights', 'coffee', 'airbnb', 'yelp']
    level: ['easy', 'hard', 'all', 'train', 'val', 'test']
    all_tools: True if all tools are provided to the agent; False if only the table tools are provided
    format_tips: True if format tips are provided; False otherwise
    custom_init_script: True if custom init script is used as format hints; False otherwise
    basic_normalization: True if only apply basic normalization on agent answers; False if apply full normalization
    use_generic_task_description: True if use generic task description; False if use specific task description
    """
    from agent.tools_python import complete_task
    from tasks.t_ToolQA.t_table_task.t_table_task import (
        TableTask, step_by_step_tips, answer_tip, hint_coffee_print, hint_coffee_price_change, hint_coffee_highest_increase, hint_coffee_increase_times, hint_coffee_percentage_increase, hint_coffee_percentage_change, hint_coffee_higher_close_price, hint_coffee_price_range, hint_coffee_bullish_or_bearish,
        hint_flights_deptime, hint_flights_difftime, hint_flights_number, hint_flights_extramin, hint_flights_arrtime, hint_flights_crstime, hint_flights_airtime, hint_flights_distance, hint_flights_unique, hint_flights_avgtime, hint_flights_fastest, hint_flights_totalnumber, hint_flights_avgspeed, hint_round, hint_flights_taxin, hint_flights_diverted, hint_flights_avgairtime, hint_flights_cancelled,
        hint_yelp_print, hint_yelp_unique_name, hint_yelp_postal_code, hint_yelp_star_rating, hint_yelp_hrs_operation, hint_yelp_num_business, hint_yelp_highest_rating, hint_yelp_distance, hint_yelp_radius, hint_yelp_avg_review, hint_yelp_nearest_business, hint_yelp_recommendation, hint_yelp_open, hint_yelp_avg_star_rating, hint_yelp_open_yes_no, hint_yelp_appointment_yes_no, hint_yelp_coordinates,
        hint_airbnb_host_name, hint_airbnb_available_days, hint_airbnb_last_review_date, hint_airbnb_avg_review, hint_airbnb_format, hint_airbnb_avg_price, hint_airbnb_cost_per_night, hint_airbnb_high_rate, hint_airbnb_lowest_price, hint_airbnb_radius, hint_airbnb_recommendation, hint_airbnb_num, hint_airbnb_review_rate
 )
    from tasks.t_ToolQA.t_table_task.utils.utils import DATA_BASE_DIR, read_qa
    from tasks.t_ToolQA.t_table_task.format_tips import FORMAT_TIPS
   
    question_answer = read_qa(DATA_BASE_DIR / f'{level}/{db_variant}-{level}.jsonl') # (questions, answers, question_types)
    tasks = TableTask.generate_variants(question_answer, db_variant, level, custom_init_script, basic_normalization, question_index, number_of_questions)
    if use_generic_task_description:
        for task in tasks:
            task_descriptions = """In this task, you are asked to answer a question by retrieving information from an external database. You can use provided tools to assist in exploring the database.\n\nHere is the question:\n"""
            
            task.task = task_descriptions + task.task_question + '\n\nFormat tip: ' + FORMAT_TIPS[db_variant][task.task_question_type]

    from tasks.t_ToolQA.tools import data_filter, get_value, check_edges, check_nodes, check_neighbours, mock_retrieve_agenda, mock_load_db, mock_load_mock_graph

    if all_tools:
        tool_docs = ["load_db", "data_filter", "get_value", "load_graph", "check_nodes", "check_neighbours", "check_edges", "retrieve_agenda", "complete_task"]
        tool_functions = {
            "load_db": mock_load_db,
            "data_filter": data_filter,
            "get_value": get_value,
            "load_graph": mock_load_mock_graph,
            "check_nodes": check_nodes,
            "check_neighbours": check_neighbours,
            "check_edges": check_edges,
            "retrieve_agenda": mock_retrieve_agenda,
            "complete_task" : complete_task,
        }
        from tasks.t_ToolQA.modify_agent import modify_agent

    else:
        tool_docs = ["load_db", "data_filter", "get_value", "complete_task"]
        tool_functions = {
            "load_db": mock_load_db,
            "data_filter": data_filter,
            "get_value": get_value,
            "complete_task" : complete_task,
        }
        from tasks.t_ToolQA.t_table_task.t_table_task import modify_agent

    prompt_config = []
    for task in tasks:
        guidelines = []
        guidelines.append(GUIDELINES["response_format"])
        guidelines.append(step_by_step_tips)
 
       
        if db_variant == 'coffee':
            guidelines.append(hint_coffee_print)
            if task.task_question_type == 'coffee price change':
                guidelines.append(hint_coffee_price_change)
            if task.task_question_type == 'day with the highest increase':
                guidelines.append(hint_coffee_highest_increase)
            if task.task_question_type == 'times of coffee price':
                guidelines.append(hint_coffee_increase_times)
            if task.task_question_type == 'percentage increase':
                guidelines.append(hint_coffee_percentage_increase)
            if task.task_question_type == 'average percentage change':
                guidelines.append(hint_coffee_percentage_change)
            if task.task_question_type == 'day with the higher close price':
                guidelines.append(hint_coffee_higher_close_price)
            if task.task_question_type == 'coffee price range':
                guidelines.append(hint_coffee_price_range)
            if task.task_question_type == 'A or B':
                guidelines.append(hint_coffee_bullish_or_bearish)

        if db_variant == 'flights':
            if task.task_question_type == 'flight departure time':
                guidelines.append(hint_flights_number)
                guidelines.append(hint_flights_deptime)
            if task.task_question_type == 'delay of arrival time':
                guidelines.append(hint_flights_number)
            if task.task_question_type == 'extra minutes':
                guidelines.append(hint_flights_extramin)
            if task.task_question_type == 'local arrival time':
                guidelines.append(hint_flights_number)
                guidelines.append(hint_flights_arrtime)
            if task.task_question_type == 'CRS-recorded arrival time':
                guidelines.append(hint_flights_crstime)
            if task.task_question_type == 'time difference':
                guidelines.append(hint_flights_number)
                guidelines.append(hint_flights_difftime)
            if task.task_question_type == 'flight duration':
                guidelines.append(hint_flights_airtime)
            if task.task_question_type == 'minutes taking to taxi in':
                guidelines.append(hint_flights_taxin)
            if task.task_question_type == 'diverted flights':
                guidelines.append(hint_flights_diverted)
            if task.task_question_type == 'flights with long distance':
                guidelines.append(hint_flights_distance)
            if task.task_question_type == 'average airtime':
                guidelines.append(hint_flights_avgairtime)
            if task.task_question_type == 'flights from A to B':
                guidelines.append(hint_flights_unique)
            if task.task_question_type == 'average flight time':
                guidelines.append(hint_flights_number)
                guidelines.append(hint_flights_avgtime)
            if task.task_question_type == 'fastest flight':
                guidelines.append(hint_flights_number)
                guidelines.append(hint_flights_fastest)
            if task.task_question_type == 'average speed':
                guidelines.append(hint_flights_avgspeed)
            if task.task_question_type == 'total number':
                guidelines.append(hint_flights_totalnumber)
            if task.task_question_type == 'percentage':
                guidelines.append(hint_flights_cancelled)
            guidelines.append(hint_round)
        
        if db_variant == 'yelp':
            guidelines.append('This task is about business data. Make sure to load the correct database.')
            guidelines.append('In one cell, do not perform too many steps.')
            if task.task_question_type == 'city' or task.task_question_type == 'state':
                guidelines.append(hint_yelp_print)
                guidelines.append(hint_yelp_unique_name)
            if task.task_question_type == 'postal code':
                guidelines.append(hint_yelp_postal_code)
            if task.task_question_type == 'star rating':
                # guidelines.append("For this question, filter the data by 'name', 'postal_code', 'city', and 'state'. Do not filter by 'catogories'.")
                guidelines.append(hint_yelp_star_rating)
            if task.task_question_type == 'hours of operation':
                guidelines.append(hint_yelp_print)
                guidelines.append(hint_yelp_hrs_operation)
            if task.task_question_type == 'coordinates':
                guidelines.append(hint_yelp_coordinates)
            if task.task_question_type == 'how many business':
                guidelines.append(hint_yelp_num_business)
            if task.task_question_type == 'highest star rating':
                guidelines.append(hint_yelp_highest_rating)
            if task.task_question_type == 'highest review count':
                guidelines.append(hint_yelp_highest_rating)
            if task.task_question_type == 'average review counts':
                guidelines.append(hint_yelp_radius)
                guidelines.append(hint_yelp_avg_review)
            if task.task_question_type == 'nearest business':
                guidelines.append(hint_yelp_distance)
                guidelines.append(hint_yelp_nearest_business)
            if task.task_question_type == 'business recommendation':
                guidelines.append(hint_yelp_radius)
                guidelines.append(hint_yelp_recommendation)
            if task.task_question_type == 'business not open':
                guidelines.append(hint_yelp_open)
            if task.task_question_type == 'average star rating':
                guidelines.append(hint_yelp_avg_star_rating)
            if task.task_question_type == 'yes or no - openning':
                guidelines.append(hint_yelp_print)
                guidelines.append(hint_yelp_open_yes_no)
            if task.task_question_type == 'yes or no - appointment':
                guidelines.append(hint_yelp_print)
                guidelines.append(hint_yelp_appointment_yes_no)

        if db_variant == 'airbnb':
            guidelines.append('This task is about accommodation data. Make sure to load the correct database.')
            if task.task_question_type == "host's name":
                guidelines.append(hint_airbnb_host_name)
            if task.task_question_type == 'days available':
                guidelines.append(hint_airbnb_available_days)
            if task.task_question_type == 'last review date':
                guidelines.append(hint_airbnb_last_review_date)
            if task.task_question_type == 'review rate number':
                guidelines.append(hint_airbnb_review_rate)
            if task.task_question_type == 'average reviews per month':
                guidelines.append(hint_airbnb_avg_review)
            if task.task_question_type == 'how many airbnbs':
                guidelines.append(hint_airbnb_num)
            if task.task_question_type == 'average price':
                guidelines.append(hint_airbnb_avg_price)
            if task.task_question_type == 'cost per night':
                guidelines.append(hint_airbnb_cost_per_night)
            if task.task_question_type == 'airbnb with high rate':
                guidelines.append(hint_airbnb_high_rate)
            if task.task_question_type == 'room with the lowest price':
                guidelines.append(hint_airbnb_lowest_price)
            if task.task_question_type == 'shared room with the lowest price':
                # guidelines.append("Filter the data by 'room type' instead of 'room_type'!")
                guidelines.append(hint_airbnb_radius)
                guidelines.append(hint_airbnb_recommendation)

            guidelines.append(hint_airbnb_format) 
  
        guidelines.append("\nDirectly present the answer in the required format without programmatically converting the output.")
        guidelines.append(answer_tip)

        prompt_config.append(PromptConfig(
            guidelines=guidelines,
            tool_docs="long",
            tool_docs_list=tool_docs,
        )) 

    engine_config = AgentEngineConfig(
        tools=tool_functions,
        modify_agent=modify_agent,
    )

    taskset_name = f"table_task_{db_variant}_{level}" + ("_full_list" if all_tools else "") + ("_generic" if use_generic_task_description else "")

    return TaskSet(taskset_name, tasks, prompt_config, engine_config).repeat(n_trials)

def table_task_test(db_variant: str = 'flights', level: str = 'easy', question_index: int = 0, number_of_questions: int = 100, tools: str = 'none', use_combined_guidelines: bool=True, combined_hints_model: str = 'llama3.1-70b', n_trials: int = 1) -> TaskSet:
    """
    Use this function to test our agent / baselines on table task.

    db_variant: ['flights', 'coffee', 'airbnb', 'yelp']
    use_combined_guidelines: True if combined guidelines are used; False otherwise
        False: without guidelines
        True: with combined guidelines + all tools' documentation
    combined_hints_model: ['llama3.1-70b', 'deepseek-chat', 'gpt-4o']
        if combined hints is True, the model whose optimized hints to use
    
    level: ['test','train']
    tools: ['none', 'relevant', 'relevant-long', 'all', 'all-long']
            'none': none of tools' names/documentation is provided;
            'relevant': only the relevant tools' names are provided;
            'relevant-long': only the relevant tools' names and docs are provided;
            'all': all tools' names are provided 
            'all-long': all tools' names and documentation are provided
    """
    from agent.tools_python import complete_task
    from tasks.t_ToolQA.t_table_task.t_table_task import (
        TableTask
 )
    from tasks.t_ToolQA.t_table_task.utils.utils import DATA_BASE_DIR, read_qa
    from tasks.t_ToolQA.t_table_task.format_tips import FORMAT_TIPS
   
    question_answer = read_qa(DATA_BASE_DIR / f'{level}/{db_variant}-{level}.jsonl') # (questions, answers, question_types)
    tasks = TableTask.generate_variants(question_answer=question_answer, db_variant=db_variant, level=level, custom_init_script=False, basic_normalization=True, question_index=question_index, number_of_questions=number_of_questions)

    for task in tasks:
        task_descriptions = """In this task, you are asked to answer a question by retrieving information from an external database. You can use provided tools to assist in exploring the database.\n\nHere is the question:\n"""
        
        task.task = task_descriptions + task.task_question + '\n\nFormat tip: ' + FORMAT_TIPS[db_variant][task.task_question_type]

    from tasks.t_ToolQA.tools import data_filter, get_value, check_edges, check_nodes, check_neighbours, mock_retrieve_agenda, mock_load_db, mock_load_mock_graph

    tool_functions = {
                "load_db": mock_load_db,
                "data_filter": data_filter,
                "get_value": get_value,
                "load_graph": mock_load_mock_graph,
                "check_nodes": check_nodes,
                "check_neighbours": check_neighbours,
                "check_edges": check_edges,
                "retrieve_agenda": mock_retrieve_agenda,
                "complete_task" : complete_task,
                }

    from tasks.t_ToolQA.modify_agent import modify_agent

    engine_config = AgentEngineConfig(
        tools=tool_functions,
        modify_agent=modify_agent,
    )

    if use_combined_guidelines:
        tools = 'all-long'
        if combined_hints_model == "llama3.1-70b":
            hints_list = list(HINTS.values())
        elif combined_hints_model == "gpt-4o":
            hints_list = list(HINTS_GPT4o.values())
        elif combined_hints_model == "deepseek-chat":
            hints_list = list(HINTS_DEEPSEEKV3.values())
        else:
            raise ValueError(f"Unknown model: {combined_hints_model}")

    if tools == 'none':
        prompt_config = PromptConfig(
                guidelines=None,
                tool_docs="none",
                monologue_format=False,
                tool_call_format=False,
            )

    else:
        tool_docs_list = ["load_db", "data_filter", "get_value", "complete_task",] if (tools == 'relevant' or tools == 'relevant-long') else ["load_db", "data_filter", "get_value", "load_graph", "check_nodes", "check_neighbours", "check_edges", "retrieve_agenda", "complete_task",]

        if use_combined_guidelines:
            prompt_config = PromptConfig(
                guidelines=hints_list,
                tool_docs="long",
                tool_docs_list=tool_docs_list,
                monologue_format=True,
                tool_call_format=True,
            )
        else:
            if tools == 'all' or tools == 'relevant':
                prompt_config = PromptConfig(
                    guidelines=None,
                    tool_docs="short", # only show the tool names
                    tool_docs_list=tool_docs_list,
                    monologue_format=False,
                    tool_call_format=False,
                )
            elif tools == 'all-long' or tools == 'relevant-long':
                prompt_config = PromptConfig(
                    guidelines=None,
                    tool_docs="long", 
                    tool_docs_list=tool_docs_list,
                    monologue_format=False,
                    tool_call_format=False,
                )

    taskset_name = f"table_task_{db_variant}_{level}_{tools}{'+combined_guidelines' if use_combined_guidelines else ''}" 

    return TaskSet(taskset_name, tasks, prompt_config, engine_config).repeat(n_trials)

def text_task(level: str = 'easy', all_tools: bool = True, question_index: int = 0, number_of_questions: int = 100, use_generic_task_description: bool = True, n_trials: int = 1) -> TaskSet:
    """
    level: ['easy', 'hard', 'all', 'train', 'val', 'test'],
    all_tools: True if all tools are provided to the agent; False if only the text tools are provided
    use_generic_task_description: True if use generic task description; False if use specific task description
    """
    from agent.tools_python import complete_task
    from tasks.t_ToolQA.t_text_task.t_text_task import (
        TextTask,
        step_by_step_tips,
        long_context_tips,
        answer_tips,
        hint_atendee,
        hint_query,
        hint_venue_name,
        hint_event_name,
        hint_schedule,
        hint_all_events,
        hint_date,
        hint_time_window,
    )
    from tasks.t_ToolQA.t_text_task.utils import DATA_BASE_DIR, read_qa
    from tasks.t_ToolQA.t_text_task.format_tips import FORMAT_TIPS

    question_answer = read_qa(DATA_BASE_DIR / f'{level}/agenda-{level}.jsonl') # (questions, answers, types)
    
    tasks = TextTask.generate_variants(question_answer, level, question_index, number_of_questions,)

    if use_generic_task_description:
        for task in tasks:
            task_descriptions = """In this task, you are asked to answer a question by retrieving information from an external database. You can use provided tools to assist in exploring the database.\n\nHere is the question:\n"""
            
            task.task = task_descriptions + task.task_question + '\n\nFormat tip: ' + FORMAT_TIPS[task.task_question_type]
    
    from tasks.t_ToolQA.tools import data_filter, get_value, check_edges, check_nodes, check_neighbours, mock_load_mock_db, mock_load_mock_graph, retrieve_agenda
    
    if all_tools:

        tool_docs = ["load_db", "data_filter", "get_value", "load_graph", "check_nodes", "check_neighbours", "check_edges", "retrieve_agenda", "complete_task",]
        
        tool_functions = {
                "load_db": mock_load_mock_db,
                "data_filter": data_filter,
                "get_value": get_value,
                "load_graph": mock_load_mock_graph,
                "check_nodes": check_nodes,
                "check_neighbours": check_neighbours,
                "check_edges": check_edges,
                "retrieve_agenda": retrieve_agenda,
                "complete_task" : complete_task,
                }

        from tasks.t_ToolQA.modify_agent import modify_agent

    else:
            tool_docs = ["retrieve_agenda", "complete_task",]
            tool_functions = {
                "retrieve_agenda": retrieve_agenda,
                "complete_task" : complete_task,
            }
            from tasks.t_ToolQA.t_text_task.t_text_task import modify_agent_agenda as modify_agent

    prompt_config = []
    for task in tasks:
        guidelines = []
        guidelines.append(GUIDELINES["response_format"])
        guidelines.append(step_by_step_tips)
        if task.task_question_type == 'how':
            guidelines.append("Start by retrieving, e.g., 10 documents.")
            guidelines.append(long_context_tips)
        if task.task_question_type == 'when':
            guidelines.append("Start by retrieving, e.g., 10 documents.")
            guidelines.append(long_context_tips)
        if task.task_question_type == 'who':
            guidelines.append(long_context_tips)
            guidelines.append(hint_atendee)
        if task.task_question_type == 'what':
            guidelines.append(long_context_tips)
            guidelines.append(hint_query)
            guidelines.append(hint_event_name)
        if task.task_question_type == 'where':
            guidelines.append("Start by retrieving, e.g., 10 documents.")
            guidelines.append(long_context_tips)
            guidelines.append(hint_venue_name)
        if task.task_question_type == 'schedule':
            guidelines.append(hint_schedule)
            # guidelines.append(hint_time_window)
        if task.task_question_type == 'all events':
            guidelines.append(hint_all_events)
        guidelines.append(hint_date)
        guidelines.append(answer_tips)
        guidelines.append("\nDirectly present the answer in the required format without programmatically converting the output.")
        prompt_config.append(PromptConfig(
            guidelines=guidelines,
            tool_docs="long",
            tool_docs_list=tool_docs,
        ))

    engine_config = AgentEngineConfig(
        tools=tool_functions,
        modify_agent=modify_agent,
    )

    taskset_name = f"text_task_agenda_{level}" + ("_full_list" if all_tools else "") + ("_generic" if use_generic_task_description else "")

    return TaskSet(taskset_name, tasks, prompt_config, engine_config).repeat(n_trials)


def text_task_test(level: str = 'test', tools: str = 'none', question_index: int = 0, number_of_questions: int = 100, use_combined_guidelines: bool = True, combined_hints_model: str = 'llama3.1-70b', n_trials: int = 1) -> TaskSet:
    """
    Use this function to test our agent / baselines on text task.

    use_combined_guidelines: True if combined guidelines are used; False otherwise
        False: without guidelines (for our trained agent)
        True: with combined guidelines + all tools' documentation (for untrained baselines)
    combined_hints_model: ['llama3.1-70b', 'deepseek-chat', 'gpt-4o']
        if combined hints is True, the model whose optimized hints to use
    
    level: ['test','train']
    tools: ['none', 'relevant', 'relevant-long', 'all', 'all-long']
            'none': none of tools' names/documentation is provided;
            'relevant': only the relevant tools' names are provided;
            'relevant-long': only the relevant tools' names and docs are provided;
            'all': all tools' names are provided
            'all-long': all tools' names and documentation are provided 
    """
    
    from agent.tools_python import complete_task
    from tasks.t_ToolQA.t_text_task.t_text_task import (
        TextTask,
    )
    from tasks.t_ToolQA.t_text_task.utils import DATA_BASE_DIR, read_qa
    from tasks.t_ToolQA.t_text_task.format_tips import FORMAT_TIPS

    question_answer = read_qa(DATA_BASE_DIR / f'{level}/agenda-{level}.jsonl') # (questions, answers, types)
    
    tasks = TextTask.generate_variants(question_answer, level, question_index, number_of_questions,)
    
    #default: task descriptions without any mention of the task type
    for task in tasks:
            task_descriptions = """In this task, you are asked to answer a question by retrieving information from an external database. You can use provided tools to assist in exploring the database.\n\nHere is the question:\n"""
            task.task = task_descriptions + task.task_question + '\n\nFormat tip: ' + FORMAT_TIPS[task.task_question_type]
    
    from tasks.t_ToolQA.tools import data_filter, get_value, check_edges, check_nodes, check_neighbours, mock_load_mock_db, mock_load_mock_graph, retrieve_agenda

    tool_functions = {
                "load_db": mock_load_mock_db,
                "data_filter": data_filter,
                "get_value": get_value,
                "load_graph": mock_load_mock_graph,
                "check_nodes": check_nodes,
                "check_neighbours": check_neighbours,
                "check_edges": check_edges,
                "retrieve_agenda": retrieve_agenda,
                "complete_task" : complete_task,
                }

    from tasks.t_ToolQA.modify_agent import modify_agent

    engine_config = AgentEngineConfig(
        tools=tool_functions,
        modify_agent=modify_agent,
    )

    if use_combined_guidelines:
        tools = 'all-long'
        if combined_hints_model == "llama3.1-70b":
            hints_list = list(HINTS.values())
        elif combined_hints_model == "gpt-4o":
            hints_list = list(HINTS_GPT4o.values())
        elif combined_hints_model == "deepseek-chat":
            hints_list = list(HINTS_DEEPSEEKV3.values())
        else:
            raise ValueError(f"Unknown model: {combined_hints_model}")

    if tools == 'none':
        prompt_config = PromptConfig(
                guidelines=None,
                tool_docs="none",
                monologue_format=False,
                tool_call_format=False,
            )

    else:
        tool_docs_list = ["retrieve_agenda", "complete_task",] if (tools == 'relevant' or tools == 'relevant-long') else ["load_db", "data_filter", "get_value", "load_graph", "check_nodes", "check_neighbours", "check_edges", "retrieve_agenda", "complete_task",]

        if use_combined_guidelines:
            prompt_config = PromptConfig(
                guidelines=hints_list,
                tool_docs="long",
                tool_docs_list=tool_docs_list,
                monologue_format=True,
                tool_call_format=True,
            )
        else:
            if tools == 'all' or tools == 'relevant':
                prompt_config = PromptConfig(
                    guidelines=None,
                    tool_docs="short", # only show the tool names
                    tool_docs_list=tool_docs_list,
                    monologue_format=False,
                    tool_call_format=False,
                )
            elif tools == 'all-long' or tools == 'relevant-long':
                prompt_config = PromptConfig(
                    guidelines=None,
                    tool_docs="long", 
                    tool_docs_list=tool_docs_list,
                    monologue_format=False,
                    tool_call_format=False,
                )


    taskset_name = f"text_task_agenda_{level}_{tools}_tools{'+combined_guidelines' if use_combined_guidelines else ''}" 

    return TaskSet(taskset_name, tasks, prompt_config, engine_config).repeat(n_trials)


def gsm8k_test(question_index: int = 0, number_of_questions: int = 1319, n_trials: int = 3) -> TaskSet:

    
    from agent.tools_python import complete_task_generic
    from tasks.t_ToolQA.t_math_task.t_math_task import (
        MathTask,
        modify_agent
    )
    from tasks.t_ToolQA.t_math_task.utils import QUESTION_ANSWER
    
    tasks = MathTask.generate_variants(QUESTION_ANSWER, question_index, number_of_questions,)
    
    prompt_config = PromptConfig(
        guidelines=[
            GUIDELINES["response_format"],
        ],
        tool_docs="long",
        tool_docs_list=[
            "complete_task",
        ],
    )
    engine_config = AgentEngineConfig(
        tools={"complete_task" : complete_task_generic},
        modify_agent=modify_agent,

    )

    taskset_name = "gsm8k_test" 

    return TaskSet(taskset_name, tasks, prompt_config, engine_config).repeat(n_trials)