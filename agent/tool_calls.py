from .workspace import Workspace

def parse_run_ipython(content: str) -> str:
    "Parse a single <run_ipython> element by hand and return the code as a string."
    content = content.strip()
    if not content.startswith("<run_ipython>"):
        raise SyntaxError("IPython cell should start with <run_ipython>.")
    if not content.endswith("</run_ipython>"):
        raise SyntaxError("IPython cell should end with </run_ipython>.")
    content = content.split("<run_ipython>", maxsplit=1)[1]
    content = content.rsplit("</run_ipython>", maxsplit=1)[0]
    return content.strip()


def dump_tool_output(
    tool_output: dict | str,
    ws: Workspace,
) -> str:
    content = "<ipython_output>\n"
    if isinstance(tool_output, str):
        content += tool_output
    elif isinstance(tool_output, dict):
        for name, value in tool_output.items():
            if value and (value := str(value)):
                content += f"<{name}>{value[:4000]}"
                if len(value) > 4000:
                    ws.add_cell_output(name, value)
                    content += "<!-- truncated, open a browser to see the full output -->"
                content += f"</{name}>\n"
    else:
        msg = f"Unknown tool output type: {tool_output}"
        raise NotImplementedError(msg)
    return content + "</ipython_output>"
