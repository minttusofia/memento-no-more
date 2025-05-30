# generate new question-answer pairs for the graph task
# %%
import json
import pandas as pd 
import random
import pickle
import tqdm
# import jsonlines
random.seed(1)
from core import TOOLQA_PATH

# load dict from file
with open(TOOLQA_PATH / "data/external_corpus/dblp/title2id_dict.pkl", "rb") as f:
    title2id_dict = pickle.load(f)
with open(TOOLQA_PATH / "data/external_corpus/dblp/author2id_dict.pkl", "rb") as f:
    author2id_dict = pickle.load(f)
with open(TOOLQA_PATH / "data/external_corpus/dblp/id2title_dict.pkl", "rb") as f:
    id2title_dict = pickle.load(f)
with open(TOOLQA_PATH / "data/external_corpus/dblp/id2author_dict.pkl", "rb") as f:
    id2author_dict = pickle.load(f)
# Load the graphs from a file
with open(TOOLQA_PATH / 'data/external_corpus/dblp/paper_net.pkl', 'rb') as f:
    paper_net = pickle.load(f)
with open(TOOLQA_PATH / 'data/external_corpus/dblp/author_net.pkl', 'rb') as f:
    author_net = pickle.load(f)

def check_neighbours(GRAPH_DATA: tuple, graph_type: str, node: str): #GRAPH_DATA: (paper_net, author_net, title2id_dict, author2id_dict, id2author_dict, id2title_dict)
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
    return neighbour_list

def check_nodes(GRAPH_DATA: tuple, graph_type: str, node: str):
    """check_nodes(GRAPH_DATA: tuple, graph_type: str, node: str) -> dict
        This function returns the detailed attributes of a given node in the graph.
        When the graph is 'PaperNet', the node attributes include 'title', 'authors', 'year', 'venue', 'number of citations for this paper', 'keywords', 'doc_type', 'page_start', and 'page_end'. 
        When the graph is 'AuthorNet', the node attribute is only the organization of the author, without any information on papers.
        - Input:
            1. Graph data as a tuple;
            2. The graph name, which can be either 'PaperNet' or 'AuthorNet'.
            3. The node name.
        - Output: The attributes of the given node in the graph. 
        Example calls:
        `check_nodes(GRAPH_DATA, 'PaperNet', 'Learning the Principle of Least Action with Reinforcement Learning.')`: Returns {'title': 'Learning the Principle of Least Action with Reinforcement Learning.', 'authors': [{id:'', name: 'Hao Zhang', org: 'Univ Tokyo, Inst Ind Sci, Tokyo, Japan'},], 'year': 2021, 'venue': {'raw': 'AAAI Spring Symposium - MLPS'}, 'number of citations for this paper': 0, 'keywords': [], 'doc_type': 'Conference', 'page_start': '', 'page_end': ''}."""
    import copy
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
    return node_info

def check_edges(GRAPH_DATA: tuple,  graph_type: str, node1: str, node2: str):
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
    paper_net, author_net, title2id_dict, author2id_dict, id2author_dict, id2title_dict = GRAPH_DATA
    if graph_type == 'PaperNet':
        graph = paper_net
        dictionary = title2id_dict
        inv_dict = id2title_dict
        edge = graph.edges[dictionary[node1], dictionary[node2]]
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
        return new_edge

# id2author_dict = {}
# id2title_dict = {}

# for author, id in author2id_dict.items():
#     id2author_dict[id] = author

# for title, id in title2id_dict.items():
#     id2title_dict[id] = title

print(len(id2author_dict) == len(author2id_dict))
print(len(id2title_dict) == len(title2id_dict))

GRAPH_DATA = (paper_net, author_net, title2id_dict, author2id_dict, id2author_dict, id2title_dict)

num_question_per_template = 16
question_id = 0
questions = []

# %%
# template 1: "Who are the authors of " + paper_title + "?"
titles = []
answers = []
random.seed(1)
for _ in range(num_question_per_template):
    paper_id = random.choice(list(id2title_dict.keys()))
    paper_title = paper_net.nodes[paper_id]["title"]
    titles.append(paper_title)
    question = "Who are the authors of \"" + paper_title + "\"?" + " Seperate the authors with comma and space ', '."
    authors = paper_net.nodes[paper_id]["authors"]
    answer = ", ".join([author['name'] for author in authors])
    answers.append(answer)
    questions.append({"qid": "easy-dblp-{:0>4d}".format(question_id), "question": question, "answer": answer})
    question_id += 1
print(questions[-10:])
# validate:
for i in range(10):
    print(answers[i])
    print(check_nodes(GRAPH_DATA, "PaperNet", titles[i]))
# %%
# template 2: What organization is {author_name} from?
names = []
answers = []
random.seed(2)
for _ in range(num_question_per_template):
    answer = ""
    while answer == "":
        author_id = random.choice(list(id2author_dict.keys()))
        author_name = id2author_dict[author_id]
        question = "What organization is " + author_name + " from?"
        answer = author_net.nodes[author_id]["org"]
    answers.append(answer)
    names.append(author_name)
    questions.append({"qid": "easy-dblp-{:0>4d}".format(question_id), "question": question, "answer": answer})
    question_id += 1
print(questions[-10:])
# validate:
for i in range(10):
    print(answers[i])
    print(check_nodes(GRAPH_DATA, "AuthorNet", names[i]))
# %%
# template 3: How many pages is {paper_title}?
titles = []
answers = []
random.seed(3)
for _ in range(num_question_per_template):
    answer = 0
    while answer <= 0:
        paper_id = random.choice(list(id2title_dict.keys()))
        paper_title = paper_net.nodes[paper_id]["title"]
        question = "How many pages is \"" + paper_title + "\"?"
        if paper_net.nodes[paper_id]["page_end"] != '' and paper_net.nodes[paper_id]["page_start"] != '':
            answer = int(float(paper_net.nodes[paper_id]["page_end"])) - int(float(paper_net.nodes[paper_id]["page_start"])) + 1
        else:
            answer = 0
    titles.append(paper_title)
    answers.append(answer)
    questions.append({"qid": "easy-dblp-{:0>4d}".format(question_id), "question": question, "answer": answer})
    question_id += 1
print(questions[-10:])
# validate:
for i in range(10): 
    print(answers[i])
    print(check_nodes(GRAPH_DATA, "PaperNet", titles[i]))
# %%
# template 4: # How many papers did {paper_title} cite? 
# info in paper_net cannot be matched with info in dict, pass this question

# answers = []
# titles = []
# random.seed(4)

# for _ in range(num_question_per_template):
#     answer = 0
#     while answer == 0:
#         paper_id = random.choice(list(id2title_dict.keys()))
#         # paper_title = paper_net.nodes[paper_id]["title"]
#         paper_title = id2title_dict[paper_id]
#         question = "How many papers did " + paper_title + " cite?"
#         # print(paper_net.neighbors(paper_id))
#         answer = paper_net.out_degree(paper_id)
#     titles.append(paper_title)
#     answers.append(answer)
#     questions.append({"qid": "easy-dblp-{:0>4d}".format(question_id), "question": question, "answer": answer})
#     question_id += 1
# print(questions[-10:])
# # validate:
# for i in range(10):
#     print(answers[i])
#     print(check_neighbours(GRAPH_DATA, "PaperNet", titles[i]))

# %%
# template 5: How many papers in the DBLP citation network cited {paper_title}?
# use check_nodes to confirm the answer
answers = []
titles = []
random.seed(5)
for _ in range(num_question_per_template):
    answer = 0
    while answer == 0:
        paper_id = random.choice(list(id2title_dict.keys()))
        paper_title = paper_net.nodes[paper_id]["title"]
        question = "How many papers in the DBLP citation network cited \"" + paper_title + "\"?"
        # print(paper_net.neighbors(paper_id))
        # answer = paper_net.in_degree(paper_id)
        answer = paper_net.nodes[paper_id]['n_citation']
    questions.append({"qid": "easy-dblp-{:0>4d}".format(question_id), "question": question, "answer": answer})
    question_id += 1
    answers.append(answer)
    titles.append(paper_title)
print(questions[-10:])
# validate:
for i in range(10):
    print(answers[i])
    print(check_nodes(GRAPH_DATA, "PaperNet", titles[i]))

# %%
# template 6: How many collaborators does {author_name} have in the DBLP citation network?
answers = []
names = [] 
random.seed(6)
for _ in range(num_question_per_template):
    answer = 0
    while answer == 0:
        author_id = random.choice(list(id2author_dict.keys()))
        author_name = id2author_dict[author_id]
        question = "How many collaborators does " + author_name + " have in the DBLP citation network?"
        # print(paper_net.neighbors(paper_id))
        # answer = author_net.degree(author_id)
        neighbour_list = []
        for neighbour in author_net.neighbors(author_id):
            if neighbour in id2author_dict:
                neighbour_list.append(id2author_dict[neighbour])
        answer = len(neighbour_list)

    questions.append({"qid": "easy-dblp-{:0>4d}".format(question_id), "question": question, "answer": answer})
    question_id += 1
    answers.append(answer)
    
    names.append(author_name)
print(questions[-10:])
# validate:
for i in range(10):
    print(answers[i])
    print(check_neighbours(GRAPH_DATA, "AuthorNet", names[i]))

# %% 
# template 7: # How many papers did {author1} and {author2} write together in the DBLP citation network?
answers = []
names = []
random.seed(7)
for _ in range(num_question_per_template):
    answer = 0
    while answer == 0:
        author_id1 = random.choice(list(id2author_dict.keys()))
        author_name1 = id2author_dict[author_id1]
        # neighbour_list = []
        # for neighbour in author_net.neighbors(author_id1):
        #     if neighbour in id2author_dict:
        #         neighbour_list.append(neighbour)
        neibors = check_neighbours(GRAPH_DATA, "AuthorNet", author_name1)
        if len(neibors) == 0:
            continue
        author_name2 = random.choice(neibors)
        question = "How many papers did " + author_name1 + " and " + author_name2 + " write together in the DBLP citation network?" + " Papers with the same title are considered the same."
        papers = check_edges(GRAPH_DATA, "AuthorNet", author_name1, author_name2)["papers"]
        # if len(edge['papers']) == 0:
        #     answer = 0
        #     continue
        # for id in range(len(edge['papers'])):
        #     if edge['papers'][id] in id2title_dict:
        #         answer += 1
        answer = len(list(set(papers)))
    questions.append({"qid": "easy-dblp-{:0>4d}".format(question_id), "question": question, "answer": answer})
    question_id += 1
    answers.append(answer)
    names.append((author_name1, author_name2))
print(questions[-10:])
# validate:
# for i in range(10):
#     print(answers[i])
#     print(check_edges(GRAPH_DATA, "AuthorNet", names[i][0], names[i][1]))

# %%
# template 8: What papers did {author_name} write in the DBLP citation network?
answers = []
names = []
random.seed(8)
for _ in range(num_question_per_template):
    answer = 0
    while answer == 0 or answer == "":
        author_id = random.choice(list(id2author_dict.keys()))
        author_name = id2author_dict[author_id]
        question = "What papers did " + author_name + " write in the DBLP citation network?" + " Seperate the papers with semicolon and space '; '." + " Papers with the same title are considered the same."
        # print(paper_net.neighbors(paper_id))
        papers = []
        for neibours in check_neighbours(GRAPH_DATA, "AuthorNet", author_name):
                for paper in check_edges(GRAPH_DATA, "AuthorNet", author_name, neibours)["papers"]:
                    papers.append(paper)
        papers = list(set(papers))
        answer = "; ".join(papers)
    questions.append({"qid": "easy-dblp-{:0>4d}".format(question_id), "question": question, "answer": answer})
    question_id += 1
    answers.append(answer)
    names.append(author_name)
print(questions[-10:])
# validate:
# for i in range(10):
#     print(answers[i])
#     print(check_neighbours(GRAPH_DATA, "AuthorNet", names[i])) # + check_edges

# %%
# template 9: How many papers did {author_name} write in the DBLP citation network?
answers = []
names = []
random.seed(9)
for _ in range(num_question_per_template):
    answer = 0
    while answer == 0:
        author_id = random.choice(list(id2author_dict.keys()))
        author_name = id2author_dict[author_id]
        question = "How many papers did " + author_name + " write in the DBLP citation network?" + " Papers with the same title are considered the same."
        answer = 0
        papers = []
        for neighbours in check_neighbours(GRAPH_DATA, "AuthorNet", author_name):
                # answer += len(list(set(check_edges(GRAPH_DATA, "AuthorNet", author_name, neighbours)["papers"])))
                for paper in check_edges(GRAPH_DATA, "AuthorNet", author_name, neighbours)["papers"]:
                    papers.append(paper)
        answer = len(list(set(papers)))
    questions.append({"qid": "easy-dblp-{:0>4d}".format(question_id), "question": question, "answer": answer})
    question_id += 1
    answers.append(answer)
    names.append(author_name)
print(questions[-10:])
# validate:
# for i in range(10):
#     print(answers[i])
#     print(check_neighbours(GRAPH_DATA, "AuthorNet", names[i])) # + check_edges

# %%
# template 10
#info in paper_net cannot be matched with info in dict, pass this question

# %%
 
df_data = pd.DataFrame(questions)
with open(TOOLQA_PATH / "data/questions/easy/dblp_easy.jsonl", "w") as f:
    f.write(df_data.to_json(orient="records", lines=True, force_ascii=False))

# %%
# template 11: How many people does {author1} need to know at least to know {author2} in the DBLP citation network?
# pass this question

# %%
# template 12: How many common collaborators does {author} have with {author}?
random.seed(12)
for _ in tqdm.tqdm(range(num_question_per_template)):
    answer = 0
    while answer == 0:
        candidate_list = []
        while candidate_list == []:
            author_id1 = random.choice(list(id2author_dict.keys()))
            name1 = id2author_dict[author_id1]
            candidate_list = [neighbour for neighbour in author_net.neighbors(author_id1) if neighbour in id2author_dict]
        author_id2 = random.choice(candidate_list)
        name2 = id2author_dict[author_id2]
        question = "How many common collaborators does {} have with {}?".format(name1, name2)
        author1_neibour = set(candidate_list)
        author2_neibour = set([neighbour for neighbour in author_net.neighbors(author_id2) if neighbour in id2author_dict])
        answer = len(author1_neibour.intersection(author2_neibour))
    questions.append({"qid": "hard-dblp-{:0>4d}".format(question_id), "question": question, "answer": answer})
    question_id += 1
print(questions[-14:])

# %%
# template 13: Which is the most cited paper written by {author} in the DBLP citation network?

random.seed(13)
for _ in range(num_question_per_template):
    answer = []
    while answer == []:
        author_id = random.choice(list(id2author_dict.keys()))
        author_name = id2author_dict[author_id]
        question = "Which is/are the most cited paper(s) written by " + author_name + " in the DBLP citation network?" + " Papers with the same title are considered the same." + " If there are multiple papers with the same citations, separate them with semicolon and space '; '."
        # print(paper_net.neighbors(paper_id))
        papers = []
        max_citation = 0
        for neighbour_id in author_net.neighbors(author_id):
            if neighbour_id in id2author_dict:
                neibour_name = id2author_dict[neighbour_id]
                for paper in check_edges(GRAPH_DATA, "AuthorNet", author_name, neibour_name)["papers"]:
                    papers.append(paper)
        papers = list(set(papers))
        for paper in papers:
            citation = check_nodes(GRAPH_DATA, 'PaperNet', paper)["number of citations for this paper"]
            if citation > max_citation:
                max_citation = citation
                answer = [paper]
            elif citation == max_citation:
                answer.append(paper)
    answer = "; ".join(answer)
    questions.append({"qid": "hard-dblp-{:0>4d}".format(question_id), "question": question, "answer": answer})
    question_id += 1
print(questions[-14:])
# %%
# template 14: Which collaborator does {author} have the most citations with in the DBLP citation network?
random.seed(14)
for _ in range(num_question_per_template):
    answer = []
    while answer == [] or len(answer) > 3:
        author_id = random.choice(list(id2author_dict.keys()))
        name = id2author_dict[author_id]
        question = "Which co-author of {} has the highest total citations for all their co-authored papers in the DBLP citation network?".format(name) + "  Papers with the same title are considered the same." + " If there are multiple collaborators with the same citations, separate them with semicolon and space '; '."
        max_citation = 0
        for neighbour_id in author_net.neighbors(author_id):
            if neighbour_id in id2author_dict:
                citation = 0
                papers = [paper for paper in check_edges(GRAPH_DATA, "AuthorNet", name, id2author_dict[neighbour_id])["papers"]]
                papers = list(set(papers))
                for paper in papers:
                    citation += check_nodes(GRAPH_DATA, "PaperNet", paper)["number of citations for this paper"]
                if citation > max_citation:
                    max_citation = citation
                    answer = [id2author_dict[neighbour_id]]
                elif citation == max_citation:
                    answer.append(id2author_dict[neighbour_id])
    answer = "; ".join(answer)
    questions.append({"qid": "hard-dblp-{:0>4d}".format(question_id), "question": question, "answer": answer})
    question_id += 1
print(questions)

# %%
# template 15: # Which venue does {author} publish the most papers in the DBLP citation network?
# pass this question

# %%
# template 16: How many accumulated citations do papers collaborated by {author1} and {author2} have in the DBLP citation network?
random.seed(16)
for _ in range(num_question_per_template):
    candidate_list = []
    while candidate_list == []:
        author_id1 = random.choice(list(id2author_dict.keys()))
        name1 = id2author_dict[author_id1]
        candidate_list = [neighbour for neighbour in author_net.neighbors(author_id1) if neighbour in id2author_dict]
    author_id2 = random.choice(candidate_list)
    name2 = id2author_dict[author_id2]
    question = "How many accumulated citations do papers collaborated by {} and {} have in the DBLP citation network?".format(name1, name2) + " Papers with the same title are considered the same."
    answer = 0
    papers = [paper for paper in check_edges(GRAPH_DATA, "AuthorNet", name1, name2)["papers"]]
    papers = list(set(papers))
    for paper in papers:
        answer += check_nodes(GRAPH_DATA, "PaperNet", paper)["number of citations for this paper"]
    answer = str(answer)
    questions.append({"qid": "hard-dblp-{:0>4d}".format(question_id), "question": question, "answer": answer})
    question_id += 1
print(questions[-14:])

# %%
# template 17: # How many papers in all do {author} and his/her collaborators have in the DBLP citation network?

random.seed(17)
for _ in range(num_question_per_template):
    answer = 720000
    while answer > 50:
        author_id = random.choice(list(id2author_dict.keys()))
        name = id2author_dict[author_id]
        question = "How many papers in all do {} and his/her collaborators have in the DBLP citation network?".format(name) + " Papers with the same title are considered the same."
        paper_list = []
        neibors = check_neighbours(GRAPH_DATA, "AuthorNet", name)
        if len(neibors) == 0 or len(neibors) > 3:
            continue
        for neighbour_name in neibors:
                for p in check_edges(GRAPH_DATA, "AuthorNet", name, neighbour_name)["papers"]:
                    paper_list.append(p)
                for neighbour_name2 in check_neighbours(GRAPH_DATA, "AuthorNet", neighbour_name):
                    for p2 in check_edges(GRAPH_DATA, "AuthorNet", neighbour_name, neighbour_name2)["papers"]:
                        paper_list.append(p2)
        answer = len(set(paper_list))       
    print(question, answer)
    questions.append({"qid": "hard-dblp-{:0>4d}".format(question_id), "question": question, "answer": answer})
    question_id += 1
print(questions[-1])

# %%
# template 18: Who collarborated with {author} most in the DBLP citation network?
random.seed(18)
num_questions = 0
while num_questions < num_question_per_template:
    # randomly choose a paper
    author_id = random.choice(list(id2author_dict.keys()))
    name = id2author_dict[author_id]
    question = "Who collaborated with {} most in the DBLP citation network?".format(name) + " Papers with the same title are considered the same." + " If there are multiple authors with the same number of collaborations, separate them with semicolon and space '; '."
    max_weight = 0
    max_author = []
    neighbors = check_neighbours(GRAPH_DATA, "AuthorNet", name)
    if len(neighbors) <= 1 or len(neighbors) > 3: 
        continue
    for neighbor_name in neighbors:
        #weight = check_edges(GRAPH_DATA, "AuthorNet", name, neighbor_name)["weight"]
        papers = check_edges(GRAPH_DATA, "AuthorNet", name, neighbor_name)["papers"]
        weight = len(set(papers))
        if weight > max_weight:
            max_weight = weight
            max_author = [neighbor_name]
        elif weight == max_weight:
            max_author.append(neighbor_name)
    answer = '; '.join(max_author)
    questions.append({"qid": "hard-dblp-{:0>4d}".format(question_id), "question": question, "answer": answer})
    question_id += 1
    num_questions += 1
print(questions[-14:])


#%%
# template 19: # What institutions participated in the study of {title} in the DBLP citation network?
# pass this question
random.seed(19)

for _ in range(num_question_per_template):
    answer = ""
    paper = []
    while answer == "":
        paper_id = random.choice(list(id2title_dict.keys()))
        title = id2title_dict[paper_id]
        if title in paper:
            continue
        paper.append(title)
        question = "What institutions participated in the study of {} in the DBLP citation network?".format(title) + " Same institutions are considered the same." + " If there are multiple institutions, separate them with semicolon and space '; '."
        authors = check_nodes(GRAPH_DATA, "PaperNet", title)["authors"]
        if len(authors) > 4:
            continue
        answer = [author['org'] for author in authors if author['org'] != '']
        answer = "; ".join(list(set(answer)))
    questions.append({"qid": "hard-dblp-{:0>4d}".format(question_id), "question": question, "answer": answer})
    question_id += 1
print(questions)

# %%
# test
author_id = random.choice(list(id2author_dict.keys()))
name = id2author_dict[author_id]
print(name)
neibors = [id2author_dict[n] for n in author_net.neighbors(author_id) if n in id2author_dict]
print(neibors)
# %%
check_neighbours(GRAPH_DATA, "AuthorNet", "Dain Kim")
check_edges(GRAPH_DATA, "AuthorNet", "Dain Kim", "Dongwhi Kim")
# %%
df_data = pd.DataFrame(questions)
with open(TOOLQA_PATH / "data/questions/hard/dblp_hard_more.jsonl", "w") as f:
    f.write(df_data.to_json(orient="records", lines=True, force_ascii=False))
# %%
