# %%
from agent.workspace import Workspace
ws = Workspace()

code = """
import warnings
a = 1
print(a)
warnings.warn("This is a warning")
b = range(10)
assert a == 2, "MyError"
d =  "{'a': 123, 'b': 456}"
print(d)
"""
stdout, stderr, exception = ws.execute_expr(code)
print("stdout:", stdout)
print("stderr:", stderr)
print("exception:", repr(exception))

# %%
from agent.workspace import Workspace
ws = Workspace()

code = """
import warnings
a = 1
print(a)
warnings.warn("This is a warning")
b = range(10)
assert a == 2, "MyError"
d =  "{'a': 123, 'b': 456}"
print(d)
"""
out = ws.run_ipython(code)
for key, value in out.items():
    print(f"{key}:\n{value}")

# %%
