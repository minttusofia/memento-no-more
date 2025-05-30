

prompt_new_dir_first = """
You are provided with the trajectory from an AI agent. The agent's role is to help in office-related tasks. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.

Some tasks requires the agent to create a new file and store this file in a new directory under the existing folder `data_path` e.g., "read the meeting agenda from an image, write all events into meeting_agenda.txt, save this file in folder agenda".
The agent should first create a new directory under data_path, e.g.,`os.mkdir(os.path.join(data_path, 'agenda'))`and then create a new file in this directory. The agent sometimes makes mistakes by creating a new file without creating a new directory first.

Your task is to determine whether the agent has created a new directory before creating a new file in its last step.
Here is the format of the response you should strictly follow:
    ----
    <reasoning>
    Write down your reasoning here.
    </reasoning>
    <answer>
    Write down your answer here.
    Your answer should be either True or False.
    </answer>
    ----
Answer True if the agent does not need to created a new directory under data_path, or it has created a new directory under data_path before creating a new file in its last step; or the last step is not related to creating a new file.
Answer False if when the agent creates a new file in its last step without creating a new directory under data_path first.

Below is the agent's trajectory. Please make your judgment based on the last step only. The earlier steps are included as additional context.
"""

prompt_dir_issue = """
You are provided with the trajectory from an AI agent. The agent's role is to help in office-related tasks. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.

Some tasks requires the agent to create a new file or a new directory. The agent's working directory is `data_path`. The agent should always create a new file/directory **under the existing folder `data_path`**.

For example: 
1. When creating a new folder, the agent should use `os.mkdir(os.path.join(data_path, 'new_folder'))`.
2. When creating a new Word/Excel file using the tools `excel_create_new_file()` or `word_create_new_file()`, the file path should be `os.path.join(data_path, 'new_file.pdf')`. The agent use this file path to create a new file, e.g., `excel_create_new_file(os.path.join(data_path, 'invoices.xlsx'))`.

The agent sometimes makes mistakes by creating a new file/directory outside the `data_path` folder, e.g., `os.mkdir('new_folder')` or `excel_create_new_file(os.path.join('invoices.xlsx'))`. Your task is to determine whether the agent has created a new file/directory under the existing folder `data_path` in its last step.
Here is the format of the response you should strictly follow:
    ----
    <reasoning>
    Write down your reasoning here.
    </reasoning>
    <answer>
    Write down your answer here.
    Your answer should be either True or False.
    </answer>
    ----
Answer True if the agent has created a new file/directory under the existing folder `data_path` in its last step; or the last step is not related to creating a new file/directory.
Answer False if the agent has created a new file/directory outside the `data_path` folder in its last step.
Below is the agent's trajectory. Please make your judgment based on the last step only. The earlier steps are included as additional context.
"""
prompt_print_file = """
You are provided with the trajectory from an AI agent. The agent's role is to help in office-related tasks. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.
In some tasks, the agent needs to load a file before analyzing or extracting information from it. There are built-in functions to different file types:
```
content = word_read_file(file_path) # read the content of a Word file
content = excel_read_file(file_path) # read the content of an Excel file
content = ocr_recognize_text(file_path) # Recognize text from an image using OCR
content = pdf_read_file(file_path) # read the content of a PDF file
```
Important rule: After loading a file, the agent must execute `print(content)` to view the file's content before performing any further operations.
However, the agent sometimes fails to print the content and proceeds to make assumptions or take actions based on the file.
YYour task is to check whether, in the **last step**, the agent performed any operations based on the file **without first printing its content**.
Here is the format of the response you should strictly follow:
    ----
    <reasoning>
    Write down your reasoning here.
    </reasoning>
    <answer>
    Write down your answer here.
    Your answer should be either True or False.
    </answer>
    ----
Answer True if: The agent printed the file content after loading it, before any other operations; or the agent has not loaded a file yet; or the agent has loaded a file but did not performed any other operations based on it yet. 
Answer False if the agent performed any operations based on the file without printing its content first in the last step.
Below is the agent's trajectory. Please make your judgment based on the last step only. The earlier steps are included as additional context.
"""

prompt_data_path = """
You are provided with the trajectory from an AI agent. The agent's role is to help in office-related tasks. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.
In some tasks, the agent needs to view the files available in a folder before proceeding. The folder path is stored in a read-only variable called data_path.
Important rules:
    The variable data_path is read-only. The agent must not modify it (e.g., by reassigning or appending paths to it).
    To list the files in the folder, the agent must use print(os.listdir(data_path)).
However, the agent sometimes incorrectly modifies data_path, or attempts to access files without checking what is inside the folder using os.listdir().
Your task is to check whether, in the last step, the agent:
    Tried to modify data_path, or
    Tried to access a file in data_path without first listing the folder contents using print(os.listdir(data_path)).

Here is the format of the response you should strictly follow:
----
<reasoning>
Write down your reasoning here.
</reasoning>
<answer>
Write down your answer here.
Your answer should be either True or False.
</answer>
----

Answer True if:
    The agent used print(os.listdir(data_path)) before accessing any files in the folder, or
    The agent has not accessed files or modified data_path in the last step.
Answer False if:
    The agent tried to modify data_path, or
    The agent accessed or referenced a file inside data_path without first using print(os.listdir(data_path)) to check its contents.

Below is the agent's trajectory. Please make your judgment based on the last step only. Earlier steps are included for context.
"""

prompt_manually_extract = """
You are provided with the trajectory from an AI agent. The agent's role is to help in office-related tasks. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.
In some tasks, the agent needs to extract or analyze information from a file, such as for comparison, calculation, writing to another file, or reasoning over the file content.

Important rule:
- The agent must manually inspect the content of the file and reason like a human.
- The agent must not parse the content programmatically, such as by:
    Using pattern matching (e.g., regex, .split(), .find(), string slicing)
    Automatically extracting specific values using code
    Iterating over file lines to identify structured patterns

Instead, the agent should:
- View the file content using print(content)
- Perform human-like reasoning in the inner monologue
- Extract information based on understanding of the content, not by parsing
Your task is to check whether, in the last step, the agent violated this rule by performing programmatic parsing on file content to extract or analyze information.
Here is the format of the response you should strictly follow:
----
<reasoning>
Write down your reasoning here.
</reasoning>
<answer>
Write down your answer here.
Your answer should be either True or False.
</answer>
----
Answer True if:
    The agent has not yet processed the file content, or
    The agent manually reasoned over the printed content (in inner monologue), or
    The agent made human-like observations without using programmatic parsing.

Answer False if:
    The agent used code to extract or analyze file content through string parsing, pattern matching, or automated methods.

Below is the agent's trajectory. Please make your judgment based on the last step only. Earlier steps are included for context.
"""
prompt_use_ocr = """
You are provided with the trajectory from an AI agent. The agent's role is to help in office-related tasks. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.
In some tasks, the agent needs to extract text from image files (e.g., .png, .jpg). There is a built-in function for this purpose:
```
content = ocr_recognize_text(file_path)  # Recognize and extract text directly from an image
```
Important rule:
When working with image files, the agent must use ocr_recognize_text() directly.
The agent must not convert the image to a PDF before using OCR. This is unnecessary and incorrect.
Your task is to determine whether, in the last step, the agent attempted to convert an image file to a PDF instead of using ocr_recognize_text() directly.

Here is the format of the response you should strictly follow:
----
<reasoning>
Write down your reasoning here.
</reasoning>
<answer>
Write down your answer here.
Your answer should be either True or False.
</answer>
----

Answer True if:
    The agent used ocr_recognize_text() directly on the image file, or
    The agent has not yet attempted to process the image file.

Answer False if:
    The agent attempted to convert the image to a PDF before applying OCR, or
    The agent used an incorrect or unnecessary function chain involving PDF conversion.

Below is the agent's trajectory. Please make your judgment based on the last step only. Earlier steps are included for context.
"""

prompt_compete_task = """You are provided with the trajectory from an AI agent. The agent's role is to help in office-related tasks. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.

In some tasks, the agent is required to answer a question and then complete the task using the built-in function:
```
complete_task(final_report, return_value)
```
The return_value must be set to the final answer to the question. 
Your task is to check whether, in the last step, the agent violated it by:
Not setting return_value to the actual final answer, or forget to provide the return_value at all.

Here is the format of the response you should strictly follow:
----
<reasoning>
Write down your reasoning here.
</reasoning>
<answer>
Write down your answer here.
Your answer should be either True or False.
</answer>
----
Answer True if: The agent set the return_value to the final answer. Or the task does not require a final answer.
Answer False if: The final answer was missing or not clearly provided when the task required it.

Below is the agent's trajectory. Please make your judgment based on the last step only. Earlier steps are included for context.
"""
prompt_excel_tools = """You are provided with the trajectory from an AI agent. The agent's role is to help in office-related tasks. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.

In some tasks, the agent needs to work with Excel files. The system provides a limited set of built-in functions for interacting with Excel files:
```
excel_create_new_file()
excel_delete_cell()
excel_set_cell()
excel_convert_to_pdf()
excel_read_file()
```
Important rules:
The agent must only use the functions listed above.
The agent must not use undefined or imaginary functions, such as excel_add_column(), excel_delete_file(), excel_read_cell(), or others not listed.
The function excel_read_file() returns the full content of an Excel file and cannot be used to access individual cells, rows, or columns.

Your task is to determine whether, in the last step, the agent violated any of these rules when it works with Excel files.

Here is the format of the response you should strictly follow:
----
<reasoning>
Write down your reasoning here.
</reasoning>
<answer>
Write down your answer here.
Your answer should be either True or False.
</answer>
----
Answer True if: The agent only used allowed Excel functions correctly, or the last step is not related to work with Excel files.
Answer False if: The agent used a non-existent Excel function, or the agent used excel_read_file() incorrectly to access specific cells, or

Below is the agent's trajectory. Please make your judgment based on the last step only. Earlier steps are included for context.
"""

prompt_create_event = """You are provided with the trajectory from an AI agent. The agent's role is to help in office-related tasks. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.
In some tasks, the agent needs to create a calendar event using the following built-in function: `create_event(user_name, event_summary, start_time, end_time)`
The function must be called with exactly four arguments, in this order: the user name, the event summary, the start time, and the end time. The event summary must be detailed, and should include as much information as available: the name or purpose of the event; who the event is for, who participates in it, or who hosts it; where the event is held.
The wording in the event summary should match the original phrasing in the task description and/or task file.
The start time and end time must come directly from the task or task file. The agent must not use datetime.now() or generate a custom time.
Your task is to check whether, in the last step, the agent violated any of above rules.
Here is the format of the response you should strictly follow:
----
<reasoning>
Write down your reasoning here.
</reasoning>
<answer>
Write down your answer here.
Your answer should be either True or False.
</answer>
----
Answer True if: The agent correctly used create_event() with four arguments in the correct order, and the event summary is detailed and matches the task language, and The times are directly from the task or task file.
Answer False if: The agent makes any mistake, such as using create_event() with fewer or more than four arguments, event summary is vague or missing key details, or using datetime.now() to generate a custom time.

Below is the agent's trajectory. Please make your judgment based on the last step only. Earlier steps are included for context.
"""

prompt_send_email = """You are provided with the trajectory from an AI agent. The agent's role is to help in office-related tasks. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.
In some tasks, the agent needs to send an email using the following built-in function: `send_email(sender_email, recipient_email, subject, content)
`.

Important rules:
    The function must be called with exactly four string arguments, in this order: The sender's email address (typically the user the agent is working for); The recipient’s email address; The subject of the email (this will also determine the generated email file name); The content of the email

The agent must not:
    Add a fifth argument (e.g., to specify an attachment). Instead, mention the attachment in the email content.
    Use invalid email formats (e.g., ending in .eml). Email addresses must follow standard format like user@example.com.

The email file name will be automatically generated as {subject}.eml. For example, if the required file is bob.eml, the subject must be 'bob' (without .eml).

Your task is to check whether, in the last step, the agent violated any of the rules above when calling send_email(). And if the subject is set to the correct value if the task requires a specific email name.
Here is the format of the response you should strictly follow:
----
<reasoning>
Write down your reasoning here.
</reasoning>
<answer>
Write down your answer here.
Your answer should be either True or False.
</answer>
----
Answer True if: The agent used send_email() with four arguments only, and The email addresses are in valid format, and The subject matches the required output file name (if applicable), and if a file was to be sent, it was described in the email content instead of passed as an argument. Or, the last step is not related to sending an email.
Answer False if: The agent used send_email() with fewer or more than four arguments, or The email addresses are in invalid format, or The subject does not match the required output file name (if applicable), or The agent added a fifth argument to send_email() instead of mentioning the attachment in the email content.
Below is the agent's trajectory. Please make your judgment based on the last step only. Earlier steps are included for context.
"""

prompt_get_pdf = """
ou are provided with the trajectory from an AI agent. The agent's role is to help in office-related tasks. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.

In some tasks, the agent is required to generate a PDF file—for example, by summarizing information or creating a report.
To do this, the agent must follow this exact process:
```
word_create_new_file(file_path) # create a new Word file
word_write_to_file(file_path, content) # write the content to the Word file
word_convert_to_pdf(word_file_path, pdf_file_path) # convert the Word file to PDF
```
However, the agent sometimes makes mistakes by using undefined or imaginary functions like: excel_convert_to_word(), pdf_write_to_file(), word_convert_to_image(). 
Your task is to check whether, in the last step, the agent followed this process correctly and only used the defined functions to generate a PDF file.
Here is the format of the response you should strictly follow:
----
<reasoning>
Write down your reasoning here.
</reasoning>
<answer>
Write down your answer here.
Your answer should be either True or False.
</answer>
----
Answer True if: The agent followed the correct process to generate a PDF file and only used the defined functions, or the last step is not related to generating a PDF file.
Answer False if: The agent used undefined or imaginary functions to generate a PDF file, or the agent did not follow the correct process to generate a PDF file.
Below is the agent's trajectory. Please make your judgment based on the last step only. The earlier steps are included as additional context.
"""

prompt_get_image = """
You are provided with the trajectory from an AI agent. The agent's role is to help in office-related tasks. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.
In some tasks, the agent is required to generate an image file—for example.
To do this, the agent must follow this exact process:
```
word_create_new_file(file_path) # create a new Word file
word_write_to_file(file_path, content) # write the content to the Word file
word_convert_to_pdf(word_file_path, pdf_file_path) # convert the Word file to PDF
pdf_convert_to_image(pdf_file_path, image_file_path) # convert the PDF file to image
```
However, the agent sometimes makes mistakes by using undefined or imaginary functions like: `excel_convert_to_image()`, `word_convert_to_image()`, `pdf_write_to_file()`.
Your task is to check whether, in the last step, the agent followed this process correctly and only used the defined functions to generate a an image.
Here is the format of the response you should strictly follow:
----
<reasoning>
Write down your reasoning here.
</reasoning>
<answer>
Write down your answer here.
Your answer should be either True or False.
</answer>
----
Answer True if: The agent followed the correct process to generate an image and only used the defined functions, or the last step is not related to generating an image.
Answer False if: The agent used undefined or imaginary functions to generate an image, or the agent did not follow the correct process to generate an image.
Below is the agent's trajectory. Please make your judgment based on the last step only. The earlier steps are included as additional context.
"""

prompt_follow_task = """You are provided with the trajectory from an AI agent. The agent's role is to help in office-related tasks. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.
In some tasks, the agent is required to carefully read the task description and follow all the stated requirements precisely.
The agent must always comply with the following task constraints:
File creation: If the task asks for a new file to be created (e.g., a report or .txt file), the agent must create it.
File type: If the task specifies a particular file type (e.g., a .txt file or an image file), the agent must create exactly that type—not another format.
File name: If the task provides a specific file name, the agent must use it exactly as given—no modifications or substitutions.
File content: If the task requires writing specific content into a file, the agent must write it exactly as provided—no additions, omissions, or alterations.

Your task is to check whether, in the last step, the agent violated any of these constraints.
Here is the format of the response you should strictly follow:
----
<reasoning>
Write down your reasoning here.
</reasoning>
<answer>
Write down your answer here.
Your answer should be either True or False.
</answer>
----
Answer True if: The agent followed all the task requirements regarding file creation, file type, file name, and file content. Or the last step is not related to these requirements.
Answer False if: The agent violated any of the task requirements regarding file creation, file type, file name, or file content in this last step.
Below is the agent's trajectory. Please make your judgment based on the last step only. The earlier steps are included as additional context.
"""

prompt_calendar_time = """You are provided with the trajectory from an AI agent. The agent's role is to help in office-related tasks. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.

In some tasks, the agent is required to create a calendar event using the create_event() function, which takes four arguments: the user name, event summary, start time, and end time. When setting the start and end times, the agent must follow these rules:
- If a specific time is given in the task files, the agent must use that exact time.
- If no time is given in the files, but the task description includes a date such as "Today is 2020-05-01", then the agent must set the calendar time accordingly—using the stated year, month, and day.
- The agent must never use datetime.now() or invent/generate its own time.
Your task is to check whether, in the last step, the agent followed these rules when setting the event times.
Here is the format of the response you should strictly follow:
----
<reasoning>
Write down your reasoning here.
</reasoning>
<answer>
Write down your answer here.
Your answer should be either True or False.
</answer>
----
Answer True if: The agent used the exact time from the task files, or from the task description (e.g., used the correct date/year stated in "Today is YYYY-MM-DD"), and did not use datetime.now() or make up the time. Or the last step is not related to setting the event times.
Answer False if: The agent used datetime.now() or invented its own time to set the event times in this last step.

Below is the agent's trajectory. Please make your judgment based on the last step only. The earlier steps are included as additional context.
"""

prompt_detailed_info_in_email = """You are provided with the trajectory from an AI agent. The agent's role is to help in office-related tasks. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.
In some tasks, the agent is required to send an email using the send_email() function. This function takes four string arguments: sender's email address, recipient's email address, subject, and content.
When sending an email, the agent must follow these rules:
    If detailed information is available in the task description or a file, the agent must include that information in the email body (the content argument).
    If the task involves sending a file, the agent must not just say “The file is attached.” Instead, the full content of the file must be included in the email body if it is available.
Your task is to check whether, in the last step, the agent violated these rules when composing the email.
Here is the format of the response you should strictly follow:
----
<reasoning>
Write down your reasoning here.
</reasoning>
<answer>
Write down your answer here.
</answer>
----
Answer True if: The agent included detailed information in the email body, and did not simply say “The file is attached” without elaboration; or the last step is not related to sending an email.
Answer False if: The agent failed to include detailed information in the email body when the last step is related to sending an email.

Below is the agent's trajectory. Please make your judgment based on the last step only. The earlier steps are included as additional context.
"""

prompt_excel_set_cell = """You are provided with the trajectory from an AI agent. The agent's role is to help in office-related tasks. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.
In some tasks, the agent is required to write to an Excel file using the excel_set_cell() function. The correct usage of excel_set_cell() is as follows: `excel_set_cell(file_path, text, row_index, column_index)`
This function takes exactly four arguments: The Excel file path; The text to be written; The row index; The column index
Important: The function does not take a sheet name as an argument.
Your task is to check whether, in the last step, the agent used excel_set_cell() incorrectly by adding a sheet name or providing the wrong number of arguments.

Here is the format of the response you should strictly follow:
----
<reasoning>
Write down your reasoning here.
</reasoning>
<answer>
Write down your answer here.
Your answer should be either True or False.
</answer>
----

Answer True if: The agent used excel_set_cell() with exactly four arguments in the correct order (file path, text, row, column), and did not specify a sheet name. Or the last step is not related to use of excel_set_cell().
Answer False if: The agent added a fifth argument for the sheet name, or used the function with an incorrect number of arguments.

Below is the agent's trajectory. Please make your judgment based on the last step only. The earlier steps are included as additional context.
"""

prompt_read_excel = """You are provided with the trajectory from an AI agent. The agent's role is to help in office-related tasks. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.
In some tasks, the agent needs to read the content of an Excel file by using `excel_read_file()` in order to perform analysis or extract information.

However, the agent sometimes forgets to read the content of the Excel file. Your task is to check whether, in the last step, the agent forget to read the content of the Excel file using `excel_read_file()`.

Here is the format of the response you should strictly follow:
----
<reasoning>
Write down your reasoning here.
</reasoning>
<answer>
Write down your answer here.
Your answer should be either True or False.
</answer>
----
Answer True if: The agent use excel_read_file() to read the content of the Excel file; or the last step is not related to read an Excel file; or this task does not require reading an Excel file.
Answer False if: The agent forget to read the excel file when the task requires it in the last step.

Below is the agent's trajectory. Please make your judgment based on the last step only. The earlier steps are included as additional context.
"""

prompt_read_pdf = """"You are provided with the trajectory from an AI agent. The agent's role is to help in office-related tasks. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.
In some tasks, the agent needs to read the content of a PDF file by using `pdf_read_file()` in order to perform analysis or extract information.
However, the agent sometimes forgets to read the content of the PDF file. Your task is to check whether, in the last step, the agent forget to read the content of the PDF file using `pdf_read_file()`.

Here is the format of the response you should strictly follow:
----
<reasoning>
Write down your reasoning here.
</reasoning>
<answer>
Write down your answer here.
</answer>
----

Answer True if: The agent use pdf_read_file() to read the content of the PDF file; or the last step is not related to read a PDF file; or this task does not require reading a PDF file.
Answer False if: The agent forget to read the PDF file when the task requires it in the last step.

Below is the agent's trajectory. Please make your judgment based on the last step only. The earlier steps are included as additional context.
"""

prompt_word_write_to_file = """You are provided with the trajectory from an AI agent. The agent's role is to help in office-related tasks. The agent performs this task by thinking in inner monologues and writing Python code to execute its actions.

In some tasks, the agent needs to write content to a Word document using the built-in function `word_write_to_file()`.
This function takes exactly two arguments: the Word file path and the content to write (string).

However, the agent sometines incorrectly uses the function by including additional arguments, such as `append=True`.
Your task is to check whether, in the last step, the agent used `word_write_to_file()` correctly by providing exactly two arguments and not including any additional arguments.

Here is the format of the response you should strictly follow:
----
<reasoning>
Write down your reasoning here.
</reasoning>
<answer>
Write down your answer here.
</answer>
----

Answer True if: The agent used `word_write_to_file()` with exactly two arguments (file path and content) and did not include any additional arguments; or the last step is not related to writing to a Word file.
Answer False if: The agent used `word_write_to_file()` with more than two arguments or included additional arguments in the last step.
Below is the agent's trajectory. Please make your judgment based on the last step only. The earlier steps are included as additional context.
"""


OFFICE_BENCH_PROMPTS = {
'new_dir_first': prompt_new_dir_first,
'dir_issue': prompt_dir_issue,
'print_file': prompt_print_file,
'data_path': prompt_data_path,
'manually_extract': prompt_manually_extract,
'use_ocr': prompt_use_ocr,
'compete_task': prompt_compete_task,
'excel_tools': prompt_excel_tools,
'create_event': prompt_create_event,
'send_email': prompt_send_email,
'get_pdf': prompt_get_pdf,
'get_image': prompt_get_image,
'follow_task': prompt_follow_task,
'calendar_time': prompt_calendar_time,
'detailed_info_in_email': prompt_detailed_info_in_email,
'excel_set_cell': prompt_excel_set_cell,
'read_excel': prompt_read_excel,
'read_pdf': prompt_read_pdf,
'word_write_to_file': prompt_word_write_to_file,
}   