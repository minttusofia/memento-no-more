# %%
from datetime import datetime
from agent.stats import Stats  # noqa
from core.usage import Usage  # noqa

stats = Stats()
stats.start_time = datetime.now()
stats.call_times = [1, 2, 3]
stats.retry_count = 6
stats.usage = Usage()
stats.usage.input_tokens = 7
stats.usage.output_tokens = 8
print(stats)

stats_dict = stats.to_dict()
print(stats_dict)

# %%
import json  # noqa

stats_json = json.dumps(stats_dict, indent=2)
print(stats_json)

# %%
