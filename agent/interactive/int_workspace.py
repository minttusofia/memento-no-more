# %%
def test_add_variables_from_other():
    # %%
    from agent.workspace import Workspace

    ws = Workspace()

    vars = {
        "a": "sssss",
        "b": 123,
        "c": {'a': 123, 'b': 456},
    }
    ws.add_variables(vars)

    ws_sub = Workspace()
    ws_sub.add_variables({"d": 789})
    ws_sub.add_variables_from_other(ws, variable_names=["a", "b"])

    print(ws_sub._variables)

    ws.add_variables_from_other(ws_sub, variable_names=["d"])
    print(ws._variables)

# %%
def test_pickle():
    # %%
    import pickle
    from agent.workspace import Workspace

    ws = Workspace()

    vars = {
        "a": "sssss",
        "b": 123,
        "c": {'a': 123, 'b': 456},
        "math": __import__("math"),
    }
    ws.add_variables(vars)

    # %%
    pickled_state = pickle.dumps(ws)
    new_ws = pickle.loads(pickled_state)
    print(new_ws._variables)
    print(id(new_ws))

# %%
