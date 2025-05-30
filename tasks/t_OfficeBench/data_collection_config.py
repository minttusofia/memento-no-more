from agent.configs import AgentEngineConfig, PromptConfig
from agent.tips import GUIDELINES
from tasks.taskset import TaskSet
from typing import Literal
from tasks.t_OfficeBench.hints import HINTS
from tasks.t_OfficeBench.combined_hints import COMBINED_HINTS
from tasks.t_OfficeBench.combined_hints_deepseekv3 import COMBINED_HINTS_DEEPSEEKV3
from tasks.t_OfficeBench.combined_hints_gpt4o import COMBINED_HINTS_GPT4o

def officebench(level: Literal["all", "train", "val", "test"] = "all", 
                n_trials: int = 1,
                guidance: Literal["only-tool", "full", "none"] = "full",
                use_combined_hints: bool = False,
                combined_hints_model: Literal["llama3.1-70b", "gpt-4o", "deepseek-v3"] = "llama3.1-70b",
                task_index: list = None,
                num_apps_only: int = None,
                toolset: Literal['relevant', 'full']='full',
                ) -> TaskSet:
    """
    level: eval on all tasks or only train/val/test
    guidance: 
        "none": no guidelines
        "only-tool": only tool docs
        "full": full guidelines + tool docs
    combined_hints: if True, use combined hints
    combined_hints_model: if combined hints is True, the model whose optimized hints to use
    task_index: if not None, eval on specific tasks
    num_apps_only: if not None, eval on tasks using 1/2/3 apps only
    toolset:
        "relevant": only provide relevant tools
        "full": provide all tools
    """
    
    from agent.tools_python import officebench_complete_task

    from tasks.t_OfficeBench.t_OfficeBench import OfficeBenchTask, modify_agent, generic_hints, file_operations_hints
    from tasks.t_OfficeBench.utils import get_task_ids
    from tasks.t_OfficeBench import tools

    if task_index is None:
        task_index = get_task_ids(level, num_apps_only)
    
    tasks = OfficeBenchTask.generate_variants(level, task_index)

    tool_functions = {
            "create_event": tools.create_event,
            "delete_event": tools.delete_event,
            "list_events": tools.list_events,
            "list_emails": tools.list_emails,
            "read_email": tools.read_email,
            "send_email": tools.send_email,
            "excel_convert_to_pdf": tools.excel_convert_to_pdf,
            "excel_create_new_file": tools.excel_create_new_file,
            "excel_delete_cell": tools.excel_delete_cell,
            "excel_read_file": tools.excel_read_file,
            "excel_set_cell": tools.excel_set_cell,
            "ocr_recognize_text": tools.ocr_recognize_text,
            "image_convert_to_pdf": tools.image_convert_to_pdf,
            "pdf_convert_to_image": tools.pdf_convert_to_image,
            "pdf_read_file": tools.pdf_read_file,
            "pdf_convert_to_word": tools.pdf_convert_to_word,
            "word_convert_to_pdf": tools.word_convert_to_pdf,
            "word_create_new_file": tools.word_create_new_file,
            "word_read_file": tools.word_read_file,
            "word_write_to_file": tools.word_write_to_file,
            "complete_task": officebench_complete_task,
        }
    
    engine_config = AgentEngineConfig(
            tools=tool_functions,
            modify_agent=modify_agent,
        )
    
    if use_combined_hints:
        toolset = "full"
        guidance = "full"
    
    prompt_configs = []

    for task in tasks:
        tool_docs = [
            "create_event", "delete_event", "list_events", 
            "excel_create_new_file", "excel_delete_cell", "excel_read_file", "excel_set_cell", "excel_convert_to_pdf",
            "pdf_read_file", "image_convert_to_pdf", "pdf_convert_to_image", "pdf_convert_to_word",
            "list_emails", "read_email", "send_email",
            "ocr_recognize_text",  
            "word_create_new_file", "word_read_file", "word_write_to_file", "word_convert_to_pdf",
            "complete_task",]
        
        if toolset == "relevant":
            tool_docs = task.task_tools
            tool_docs.append("complete_task")

        match guidance:
            case "none":
                prompt_config = PromptConfig(
                    guidelines=None,
                    tool_docs="none",
                    monologue_format=False,
                    tool_call_format=False,
                )
            case "only-tool":
                prompt_config = PromptConfig(
                    guidelines=None,
                    tool_docs="long",
                    tool_docs_list=tool_docs,
                )
            case "full":
                guidelines=[
                        GUIDELINES["response_format"],
                        generic_hints,
                        file_operations_hints,
                    ]
                if use_combined_hints:
                    if combined_hints_model == "llama3.1-70b":
                        guidelines.extend(COMBINED_HINTS)
                    elif combined_hints_model == "gpt-4o":
                        guidelines.extend(COMBINED_HINTS_GPT4o)
                    elif combined_hints_model == "deepseek-v3":
                        guidelines.extend(COMBINED_HINTS_DEEPSEEKV3)
                    else:
                        raise ValueError(f"Unknown model: {combined_hints_model}")
                else:
                    if HINTS.get(task.task_id) and HINTS[task.task_id].get(task.subtask_id):
                        guidelines.extend(HINTS[task.task_id][task.subtask_id])

                prompt_config = PromptConfig(
                    guidelines=guidelines,
                    tool_docs="long",
                    tool_docs_list=tool_docs,
                )
        prompt_configs.append(prompt_config)

    taskset_name = f"OfficeBench_{level}"
    sguidance = "" if guidance == "none" else f"_g-{guidance}"
    taskset_name += sguidance 

    return TaskSet(taskset_name, tasks, prompt_configs, engine_config).repeat(n_trials)
