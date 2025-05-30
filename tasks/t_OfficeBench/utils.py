# %%
import json
import glob
from pathlib import Path

def load_task_info(task_id: str, subtask_id: str):
    task_config_path = Path(__file__).parent / f'OfficeBench/tasks/{task_id}/subtasks/{subtask_id}.json'
    config = json.load(open(task_config_path))
    task = config.get('task', None)
    username = config['username']
    date = config['date']
    weekday = config['weekday']
    time = config['time']

    # get info on relevant tools
    task_tools = []
    file_types = ""
    with open(Path(__file__).parent / 'OfficeBench/tasks/task_info.jsonl', 'r') as file:
        for line in file:
            data = json.loads(line.strip())
            if data['task_id'] == task_id and data['subtask_id'] == subtask_id:
                file_types = data['file_type']
 
    for file_type in file_types.split(';'):
        if file_type == 'ics':
            task_tools.extend(['create_event', 'delete_event', 'list_events'])
        elif file_type == 'email':
            task_tools.extend(['list_emails', 'read_email', 'send_email'])
        elif file_type == 'xlsx':
            task_tools.extend(['excel_create_new_file', 'excel_delete_cell', 'excel_read_file', 'excel_set_cell', 'excel_convert_to_pdf'])
        elif file_type == 'docx':
            task_tools.extend(['word_create_new_file', 'word_read_file', 'word_write_to_file', 'word_convert_to_pdf'])
        elif file_type == 'pdf':
            task_tools.extend(['image_convert_to_pdf', 'pdf_convert_to_image', 'pdf_read_file', 'pdf_convert_to_word'])
        elif file_type == 'jpg' or file_type == 'png':
            task_tools.extend(['ocr_recognize_text',])
            
    if set(task_tools) == {'image_convert_to_pdf', 'pdf_convert_to_image', 'pdf_read_file', 'pdf_convert_to_word', 'ocr_recognize_text'}:
        task_tools.extend(['word_create_new_file', 'word_read_file', 'word_write_to_file', 'word_convert_to_pdf'])
    
    return task, username, date, weekday, time, task_tools

def get_testbed_path(task_id: str,) -> Path:
    return Path(__file__).parent / f'OfficeBench/tasks/{task_id}/testbed/'

def get_task_ids(level: str, num_apps=None) -> list:
    task_ids = []
    parent_path = str(Path(__file__).parent)
    task_config_filepaths = glob.glob(parent_path + "/OfficeBench/tasks/*/subtasks/*.json") if level == 'all' else glob.glob(parent_path + f"/OfficeBench/tasks_{level}/*/subtasks/*.json")
    for config_filepath in task_config_filepaths:
        task_id = config_filepath.split('/')[-3]
        subtask_id = config_filepath.split('/')[-1].split('.')[0]
        task_ids.append((task_id, subtask_id))
    task_ids = sorted(task_ids, key=lambda x: tuple(map(int, x[0].split('-'))) + (int(x[1]),))
    if num_apps is not None:
        task_ids = [id for id in task_ids if id[0].split('-')[0] == str(num_apps)]
    return task_ids
# %%