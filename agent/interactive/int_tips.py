# %%
from agent.tips import SectionedContent

sections = SectionedContent(
    top="<guidelines>\n",
    bottom="\n</guidelines>",
)

sections.add("> first")
sections.add("> hidden")
sections.add("> visible")

print(sections.render())

# %%
sections = SectionedContent(
    top="<guidelines>\n",
    bottom="\n</guidelines>",
    separator="\n--------\n",
)

sections.add("> first")
sections.add("> hidden")
sections.add("> visible")

print(sections.render())


# %%
from agent.tips import ExerciseSectionedContent

sections = ExerciseSectionedContent(
    top="<guidelines>\n",
    bottom="\n</guidelines>",
)

sections.add("> first")
sections.add("> hidden", for_teacher=True)
sections.add("> visible")

print(sections.render())
