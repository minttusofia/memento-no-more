from xml.etree import ElementTree as ET

from agent.clients import BaseClient
from core.messages import Message, Role

async def grade_set(
    client: BaseClient,
    task: str,
    correct_answer: list,
    returned_answer: list
) -> tuple[float | None, str | None, str | None]:
    c2r_response, r2c_response = None, None
    try:
        formatted_prompt = prompt.format(
            task=task,
            correct_answer=str(correct_answer),
            returned_answer=str(returned_answer)
        ) + pass1
        c2r_results, c2r_response = await match_elements_of_one_set(
            client, formatted_prompt
        )
        # print("pass1_results", c2r_results)
        assert len(c2r_results) == len(correct_answer), f"Grading failed: Wrong number of items ({len(c2r_results)} vs {len(correct_answer)})."

        formatted_prompt = prompt.format(
            task=task, correct_answer=correct_answer, returned_answer=returned_answer
        ) + pass2
        r2c_results, r2c_response = await match_elements_of_one_set(client, formatted_prompt)
        assert len(r2c_results) == len(returned_answer),  f"Grading failed: Wrong number of items ({len(r2c_results)} vs {len(returned_answer)})."

        # Compute jaccard similarity
        # print("pass2_results", r2c_results)
        intersection = sum(
            [1 for a, b in zip(c2r_results, r2c_results, strict=False) if a == b]
        )
        union = len(c2r_results) + len(r2c_results) - intersection
        score = intersection / union if union != 0 else 0
        return score, c2r_response, r2c_response

    except Exception as e:
        print("Grading failed with error:", e)
        return None, c2r_response, r2c_response


async def match_elements_of_one_set(
    client: BaseClient,
    formatted_prompt: str
) -> tuple[list[int], str]:
    msg = Message(Role.SYSTEM, formatted_prompt)
    response = await client.call(messages=[msg])
    response = response.split("<items>")[1].rsplit("</items>")[0]
    response = "<items>" + response + "</items>"
    # This is a quick and dirty way, this does not work if the correct or returned answer
    # contains xml tags
    root = ET.fromstring(response)
    binary_list = []
    for item in root.findall("item"):
        score = item.find("score").text.strip()
        if score == "reject":
            binary_list.append(0)
        elif score == "accept":
            binary_list.append(1)
        else:
            raise ValueError(f"Grading failed: Unknown score: {score}.")

    return binary_list, response


prompt = """\
The agent is given the following task:
<task>
{task}
</task>
with the correct answer given below:
<correct_answer>
{correct_answer}
</correct_answer>

The agent returns the following answer:
<returned_answer>
{returned_answer}
</returned_answer>
"""

pass1 = """\
Go through every item in the correct answer and produce the following list in the xml-like format. The number of items must be the same as in the correct answer.
<items>
<item>
<correct_item>
item from the correct answer
</correct_item>
<returned_item>
closest answer from the returned answer
</returned_item>
<comparison>
Your evaluation of how close the items are
</comparison>
<score>
your evaluation:
"accept": two items can be recognized to be same, there are only stylistic differences
"reject": the returned item has at least one mistake in a crucial detail.
</score>
</item>
...
</items>
"""

pass2 = """\
Go through every item in the returned answer and produce the following list in the xml-like format. The number of items must be the same as in the returned answer.
<items>
<item>
<returned_item>
closest answer from the returned answer
</returned_item>
<correct_item>
item from the correct answer
</correct_item>
<comparison>
Your evaluation of how close the items are
</comparison>
<score>
your evaluation with three grades:
"accept": two items can be recognized to be same, there are only stylistic differences
"reject": the returned item has at least one mistake in a crucial detail.
</score>
</item>
...
</items>
"""

