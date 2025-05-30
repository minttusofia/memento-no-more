# %%
from agent.trajectory import Trajectory

traj = Trajectory(
    task="Compute '2 + 3' using Python and report the result.",
    return_cls_name="int",
    input_variables={},
)
print(traj)

s = traj.to_json()
print(s)

# %%
from pprint import pprint

new_traj = Trajectory.from_json(s)
pprint(new_traj)

# %%
print(traj.get_responses())
print(traj.get_feedbacks())

# %%
