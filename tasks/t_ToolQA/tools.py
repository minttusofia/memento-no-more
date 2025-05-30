from agent import agent as ag

def data_filter(agent: ag.Agent, data, argument):
    """data_filter(database: pandas.DataFrame, argument: str) -> pandas.DataFrame
        This function filters the database by the column name, the relation (e.g., =, >, etc.) and the value, and keeps only rows matching the argument.
        - Input:
            1. A database;
            2. An argument string with column names, relations (e.g., =, >, etc.) and values as conditions to filter the database. Conditions in the argument should be separated by a semicolon and a space '; '.
            Example Argument: 'name=Snip Philadelphia; postal_code=19130'
            Note: You must strictly follow the extact format of input of the argument.
        - Output: A new `pandas.DataFrame` containing rows matching the argument.
        Example calls:
        `new_database=data_filter(full_database, 'IATA_Code_Marketing_Airline=AA; Flight_Number_Marketing_Airline=5647; Origin=BUF; Dest=PHL; FlightDate=2022-04-20')`: Returns a `new_database` contains only one row of the database."""
    agent.stats.add_tool_call("data_filter")
    commands = argument.split('; ')

    for i in range(len(commands)):
        try:
            if '>=' in commands[i]:
                command = commands[i].split('>=')
                column_name = command[0]
                value = command[1]
                data = data[data[column_name] >= value]
            elif '<=' in commands[i]:
                command = commands[i].split('<=')
                column_name = command[0]
                value = command[1]
                data = data[data[column_name] <= value]
            elif '>' in commands[i]:
                command = commands[i].split('>')
                column_name = command[0]
                value = command[1]
                data = data[data[column_name] > value]
            elif '<' in commands[i]:
                command = commands[i].split('<')
                column_name = command[0]
                value = command[1]
                data = data[data[column_name] < value]
            elif '=' in commands[i]:
                command = commands[i].split('=')
                column_name = command[0]
                value = command[1]
                data = data[data[column_name] == value]
            if len(data) == 0:
                # data = backup_data
                raise ValueError("The filtering query {} is incorrect. Please modify the condition.".format(commands[i]))
        except Exception as e:
            raise e
    current_length = len(data)
    if current_length > 0:
        print("We have successfully filtered the data ({} rows).".format(current_length))
        return data
    else:
        raise ValueError("No data matching the conditions")

def get_value(agent: ag.Agent, data, argument):
    """get_value(data: pandas.DataFrame, name: str) -> str
        This function returns the value(s) of a specific column in the database.
        - Input:
            1. A database;
            2. A single column name
            Note: You can only input one column name.
        - Output: The value(s) of the specific column as a string. If there are multiple rows in this database, the values are concatenated using a comma and a space ', '.
        Example calls:
        `dep_time = get_value(new_database, 'DepTime')`: Returns '1752.0'.
        `flight_number = get_value(new_database, 'Flight_Number_Marketing_Airline')`: Returns '388, 844, 3517, 4301'."""
    agent.stats.add_tool_call("get_value")
    column = argument
    if len(data) == 1:
        value = str(data.iloc[0][column])
    else:
        value = ', '.join(data[column].tolist())
    return value

def check_neighbours(agent: ag.Agent, GRAPH_DATA: tuple, graph_type: str, node: str): #GRAPH_DATA: (paper_net, author_net, title2id_dict, author2id_dict, id2author_dict, id2title_dict)
    """check_neighbours(GRAPH_DATA: tuple, graph_type: str, node: str) -> list[str]
        This function returns the names of a given node's neighbours in the graph.
        When the graph is 'AuthorNet', the output is a list of author names who have co-authored with the given author, without any information on papers. 
        - Input:
            1. Graph data as a tuple;
            2. The graph name, which can be either 'PaperNet' or 'AuthorNet'.
            3. The node name. 
        - Output: A list of the names of a given node's neighbours in the graph.
        Example calls:
        `check_neighbours(GRAPH_DATA, 'AuthorNet', 'Chao Zhang')`: Returns ['YUHUI YUAN', 'Rao Fu', 'Lang Huang']."""
    agent.stats.add_tool_call("check_neighbours")
    paper_net, author_net, title2id_dict, author2id_dict, id2author_dict, id2title_dict = GRAPH_DATA
    if graph_type == 'PaperNet':
        graph = paper_net
        dictionary = title2id_dict
        inv_dict = id2title_dict
    elif graph_type == 'AuthorNet':
        graph = author_net
        dictionary = author2id_dict
        inv_dict = id2author_dict
    neighbour_list = []
    for neighbour in graph.neighbors(dictionary[node]):
        if graph_type == 'PaperNet':
            # if neighbour in inv_dict:
            #     neighbour_list.append(inv_dict[neighbour])
            neighbour_list.append(inv_dict[neighbour])
        elif graph_type == 'AuthorNet':
            if neighbour in inv_dict:
                neighbour_list.append(inv_dict[neighbour])
            #neighbour_list.append(inv_dict[neighbour])
    print("The neighbours of {} is: {}. ".format(node, neighbour_list))

    return neighbour_list

def check_nodes(agent: ag.Agent, GRAPH_DATA: tuple, graph_type: str, node: str):
    """check_nodes(GRAPH_DATA: tuple, graph_type: str, node: str) -> dict
        This function returns the detailed attributes of a given node in the graph.
        When the graph is 'PaperNet', the node attributes include 'title', 'authors', 'year', 'venue', 'number of citations for this paper', 'keywords', 'doc_type', 'page_start', and 'page_end'. 
        When the graph is 'AuthorNet', the node attribute is only the organization of the author, without any information on papers.
        - Input:
            1. Graph data as a tuple;
            2. The graph name, which can be either 'PaperNet' or 'AuthorNet'.
            3. The node name. When the graph is 'PaperNet', the node name must be the title of the paper. When the graph is 'AuthorNet', the node name must be the author's name.
        - Output: The attributes of the given node in the graph. 
        Example calls:
        `check_nodes(GRAPH_DATA, 'PaperNet', 'Learning the Principle of Least Action with Reinforcement Learning.')`: Returns {'title': 'Learning the Principle of Least Action with Reinforcement Learning.', 'authors': [{id:'', name: 'Hao Zhang', org: 'Univ Tokyo, Inst Ind Sci, Tokyo, Japan'},], 'year': 2021, 'venue': {'raw': 'AAAI Spring Symposium - MLPS'}, 'number of citations for this paper': 0, 'keywords': [], 'doc_type': 'Conference', 'page_start': '', 'page_end': ''}."""
    import copy
    agent.stats.add_tool_call("check_nodes")
    paper_net, author_net, title2id_dict, author2id_dict, id2author_dict, id2title_dict = GRAPH_DATA
    if graph_type == 'PaperNet':
        graph = paper_net
        dictionary = title2id_dict
        node_info = copy.deepcopy(graph.nodes[dictionary[node]])
        node_info['number of citations for this paper'] = node_info.pop('n_citation')
    elif graph_type == 'AuthorNet':
        graph = author_net
        dictionary = author2id_dict
        node_info = copy.deepcopy(graph.nodes[dictionary[node]])
        
    print("The attributes of the node {} is: {}. ".format(node, node_info))
    return node_info

def check_edges(agent: ag.Agent, GRAPH_DATA: tuple,  graph_type: str, node1: str, node2: str):
    """check_edges(GRAPH_DATA: tuple,  graph_type: str, node1: str, node2: str) -> dict
        This function returns the detailed attributes of an edge between two nodes in the graph.
        When the graph is 'AuthorNet', the edge represents the collaboration between two authors, and the edge attributes are information of the papers they have co-authored.
        - Input:
            1. Graph data as a tuple;
            2. The graph name, which can be either 'PaperNet' or 'AuthorNet'.
            3. The first node name.
            4. The second node name.
        - Output: The attributes of the edge between the two given nodes in the graph.
        Example calls:
        `check_edges(GRAPH_DATA, 'AuthorNet', 'Chao Zhang', 'Weihong Lin')`: Returns {'weight': 1, 'papers': ['HRFormer: High-Resolution Vision Transformer for Dense Predict.'], 'number of citations for this paper': [95]}."""
    import copy
    agent.stats.add_tool_call("check_edges")
    paper_net, author_net, title2id_dict, author2id_dict, id2author_dict, id2title_dict = GRAPH_DATA
    if graph_type == 'PaperNet':
        graph = paper_net
        dictionary = title2id_dict
        inv_dict = id2title_dict
        edge = graph.edges[dictionary[node1], dictionary[node2]]
        print(edge)
        return edge
    elif graph_type == 'AuthorNet':
        graph = author_net
        dictionary = author2id_dict
        inv_dict = id2title_dict
        edge = graph.edges[dictionary[node1], dictionary[node2]]
        new_edge = copy.deepcopy(edge)
        for id in range(len(new_edge['papers'])):
            new_edge['papers'][id] = inv_dict[new_edge['papers'][id]]
        new_edge['number of citations for this paper'] = new_edge.pop('n_citation')
        print(new_edge)
        return new_edge

def mock_retrieve_agenda(agent: ag.Agent, query: str, num_docs: int):
    """retrieve_agenda(query: str, num_docs: int) -> list[str]
        This function retrieves relevant agenda-related documents based on the query.
        - Input:
            1. query: A query including the key information to answer the question.
            2. num_docs: The number of documents to retrieve. Determine it based on the complexity of the question.
        - Output: A list of `num_docs` documents relevant to the query.
        Example calls:
        `retrieved_docs = retrieve_agenda("Grace attend Broadway Show on February 2nd, 2022", 10)`: Returns 10 revelant documents."""
    agent.stats.add_tool_call("retrieve_agenda")
    return None

def retrieve_agenda(agent: ag.Agent, query: str, num_docs: int):
    """retrieve_agenda(query: str, num_docs: int) -> list[str]
        This function retrieves relevant agenda-related documents based on the query.
        - Input:
            1. query: A query including the key information to answer the question.
            2. num_docs: The number of documents to retrieve. Determine it based on the complexity of the question.
        - Output: A list of `num_docs` documents relevant to the query.
        Example calls:
        `retrieved_docs = retrieve_agenda("Grace attend Broadway Show on February 2nd, 2022", 10)`: Returns 10 revelant documents."""
    agent.stats.add_tool_call("retrieve_agenda")
    from tasks.t_ToolQA.t_text_task.load_chroma_agenda_db import CHROMA_DB, MODEL
    model = MODEL
    db = CHROMA_DB
    query_embedding = model.encode(query).tolist()
    results = db.query(query_embeddings=query_embedding, n_results=num_docs)
    retrieved_docs = [result for result in results['documents'][0]]
    return retrieved_docs

def mock_load_mock_db(agent: ag.Agent, db_variant: str):
    """load_db(db_variant: str) -> pandas.DataFrame
        This function loads the database and shows names of all columns of this database. `db_variant` can be one of the following: flights/coffee/airbnb/yelp.
        - Input: used to indicate which database to load.
        - Output: A `pandas.DataFrame` containing the loaded database. Note that all elements in the DataFrame are converted to strings.
        Example calls:
        `flights_db = load_db('flights')`: Returns the flights database."""
    TABLE_TASK_MOCK_DATA = (None, None)
    agent.stats.add_tool_call("load_db")
    if db_variant != 'flights' and db_variant != 'coffee' and db_variant != 'airbnb' and db_variant != 'yelp':
        raise ValueError("Invalid database variant. Please choose from flights, coffee, airbnb, or yelp.")
    print("{} database has been successfully loaded, which includes the following columns: {}.".format(db_variant, TABLE_TASK_MOCK_DATA[1]))
    return TABLE_TASK_MOCK_DATA[0]

def mock_load_db(agent: ag.Agent, db_variant: str):
    """load_db(db_variant: str) -> pandas.DataFrame
        This function loads the database and shows names of all columns of this database. `db_variant` can be one of the following: flights/coffee/airbnb/yelp.
        - Input: used to indicate which database to load.
        - Output: A `pandas.DataFrame` containing the loaded database. Note that all elements in the DataFrame are converted to strings.
        Example calls:
        `flights_db = load_db('flights')`: Returns the flights database."""
    agent.stats.add_tool_call("load_db")
    if db_variant == 'flights':
        from tasks.t_ToolQA.t_table_task.utils.load_flights import DATA_FLIGHTS as TABLE_DATA
    elif db_variant == 'coffee':
        from tasks.t_ToolQA.t_table_task.utils.load_coffee import DATA_COFFEE as TABLE_DATA
    elif db_variant == 'airbnb':
        from tasks.t_ToolQA.t_table_task.utils.load_airbnb import DATA_AIRBNB as TABLE_DATA
    elif db_variant == 'yelp':
        from tasks.t_ToolQA.t_table_task.utils.load_yelp import DATA_YELP as TABLE_DATA
    else:
        raise ValueError("Invalid database variant. Please choose from flights, coffee, airbnb, or yelp.")
    print("{} database has been successfully loaded, which includes the following columns: {}.".format(db_variant, TABLE_DATA[1]))
    return TABLE_DATA[0]

def mock_load_mock_graph(agent: ag.Agent):
    """load_graph() -> tuple
        This function loads the graph data.
        - Output: The graph data.
        Example calls:
        `GRAPH_DATA = load_graph()`: Returns the graph data."""
    agent.stats.add_tool_call("load_graph")
    GRAPH_TASK_MOCK_DATA = (None, None, None, None, None, None)
    print("DBLP graph data is loaded, including two graphs: AuthorNet and PaperNet.")
    return GRAPH_TASK_MOCK_DATA


def mock_load_graph(agent: ag.Agent):
    """load_graph() -> tuple
        This function loads the graph data.
        - Output: The graph data.
        Example calls:
        `GRAPH_DATA = load_graph()`: Returns the graph data."""
    from tasks.t_ToolQA.t_graph_task.utils import GRAPH_DATA
    agent.stats.add_tool_call("load_graph")
    print("DBLP graph data is loaded, including two graphs: AuthorNet and PaperNet.")
    return GRAPH_DATA