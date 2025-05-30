from agent.agent import Agent

def modify_agent(agent: Agent):
    complete_task_method = agent.config.engine_config.tools["complete_task"]
    complete_task_method.__doc__ = complete_task_method.__doc__.replace("tools.", "")

    agent.workspace.add_variables({"complete_task" : agent.core_tools.complete_task})
    agent.workspace.add_variables({"data_filter" : agent.core_tools.data_filter})
    agent.workspace.add_variables({"get_value" : agent.core_tools.get_value})
    agent.workspace.add_variables({"load_db" : agent.core_tools.load_db})
    agent.workspace.add_variables({"load_graph" : agent.core_tools.load_graph})
    agent.workspace.add_variables({"check_neighbours" : agent.core_tools.check_neighbours})
    agent.workspace.add_variables({"check_nodes" : agent.core_tools.check_nodes})
    agent.workspace.add_variables({"check_edges" : agent.core_tools.check_edges})
    agent.workspace.add_variables({"retrieve_agenda" : agent.core_tools.retrieve_agenda})
