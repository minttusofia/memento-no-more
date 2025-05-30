hint_one_action_per_step = """Perform only one action in one step."""

hint_new_file_path = """When creating a new file, store it in `data_path`. For example, if the file name is `test.docx`, use `os.path.join(data_path, "test.docx")` as the file path. Do not use `test.docx` as the file path directly, as this will not save the file in the correct task files folder."""

hint_new_dir_path = """If the data_path directory does not exist, please create it using os.makedirs(data_path)."""

hint_input_data_path = """When reading from data_path, use `os.path.join(data_path, "file_name")` to set the full path of the file with the correct separators."""

hint_format = """Stricty follow the format (e.g., time format) mentioned in the task description if there is any. E.g., if the task mentions 7:00, do not use 2021-04-01 07:00:00."""

hint_file_name = """Do not assume the file name by yourself."""

hint_ls_data_path = """Ths task files folder contains Excel, Word, PDF, and Image files. Use `print(os.listdir(data_path))` to see the files in the folder."""

hint_return_value = """If this task requires a final answer, you should provide `return_value` in `complete_task()`, e.g., `complete_task("The answer is:", "100")`"""


hint_calendar_event_summary = """When creating a new event in the calendar, the event summary must include all important information."""


ocr_results_mistakes = """The OCR tool may return some wrong characters. Please attempt to correct any obvious mistakes you spot, such as 'd' replaced by 'a', or missing characters."""
hint_compatible_string = """If you get the error 'All strings must be XML compatible: Unicode or ASCII, no NULL bytes or control characters', manually extract the plain text content from the OCR output to exclude problematic characters. Do not attempt to fix the OCR output programmatically."""


hint_excel_get_cell_id = """Use `excel_read_file` to view the file content (you can print it) and manually identify the row and column id to work on. Do not determine the indices programmatically."""
hint_excel_get_values = """Do not obtain cell values programmatically for calculations / comparison. Instead, manually inspect the file content to find the required values before performing calculations / comparison."""
hint_excel_verify_bf_completing = """Before completing the task, use `excel_read_file` to view the file content to verify that the file content is correct."""
hint_excel_create_bf_write = """If you want to write information into a new Excel file, first create a new Excel file using `excel_create_new_file()`."""
hint_excel_write_to_file = """After creating a new Excel file, always remember to write the information into the new Excel file using `excel_set_cell()`."""
hint_excel_add_header = """When creating a new excel file, remember to add a header in the first row."""
hint_excel_cell_value = """The value of each cell in the excel file should be a string."""
hint_excel_swap = """If the task requires a swap operation, make sure to swap the entire row or column, including the header."""


hint_word_create_bf_write = """If you want to write information into a new Word file, first create a new Word file using `word_create_new_file()`."""
hint_word_write_to_file = """After creating a new Word file, do not forget to write the information into the new Word file using `word_write_to_file()`."""
hint_word_verify_bf_completing = """Before completing the task, use `word_read_file` to view the file content to verify that the file content is correct."""


hint_new_pdf =  """To create a PDF file, first create a Word file and then convert it to PDF using word_convert_to_pdf."""
hint_info_from_pdf = """To get text from a **PDF**, use the `pdf_read_file()` function. Do not convert the PDF to image to extract the text."""
hint_extract_info_from_pdf = """When extracting information from a PDF file, review the content manually to find the required information. Do not parse the file programmatically."""


hint_email_full_content = """To read the full content of an email, including the date, use `read_email(user_name, email_id)`. For example: read_email('Bob', 'meeting.eml')."""
hint_email_list = """Use `list_emails(username)` to list all emails for a specific user."""
hint_email_name = """The output .eml file will automatically be named after the subject of the email."""


hint_extract_info_from_text = """Print the file content and manually read the text to extract the required information. Do not extract it programmatically."""
hint_view_task_files = """When you find out your task files, always remember to view its content. If the file is an image, use `ocr_recognize_text()` to extract the text and print it."""
hint_output_file_name = """When creating a new file, make sure to exactly adhere to the requested file name according to the task description."""
hint_verification = """Before completing the task, verify that you have completed all the required steps stated in the task description."""
hint_summary = """When a task requires you to extract information from a source file and write it into a new file, make sure to include all relevant information in the new file."""

hint_commitments = """Do not consider personal events like sleep when asked about a person's commitments for the day."""
hint_no_overwrite = """When asked to add data to a spreadsheet, make sure to do so in an unused cell. Do not overwrite existing data."""
hint_new_column = """Pay attention when creating a new column or row. Make sure all new values align with the new column or row."""
hint_inspect_data = """Always inspect the data first, and carefully look at the row and column names before making assumptions about the format."""
hint_remove_header = """When deleting all values in a row or column, also remove the header name. Do not leave empty rows or columns."""
hint_indexing = """Excel indexing starts from 1, not 0. For example, the first row is 1, the second row is 2, and so on. The same applies to columns."""
hint_complete_task = """If the task is a question requiring a final answer, use the second argument to `complete_task()` to provide the answer. For example, `complete_task("The answer is:", "100")`."""
hint_read_emails = """To find information about an email, such as the date it was received, view the full content of the email with `read_email(user_name, email_id)`."""
hint_create_event = """If your task is to find a good time for a meeting, also schedule this time in the calendar."""
hint_capitalization = """If an output file name is specified, use that exact name and pay attention to capitalization."""
hint_agreement_terms = """When extracting legal terms from a contract, make sure to include all terms exactly as specified, without paraphrasing the terms."""

hint_date = """Assume today's date as specified in the task description. Do not use the current date or time from the system. For example, if the task states "today is 2022-10-24", use that date for all calculations and comparisons."""
hint_calendar_user = """Create events in the calendar of the relevant user or users (who should attend the event) as implied in the task. Note that the relevant user is not necessarily Alice."""
hint_complete_information = """When asked to extract information from a file, make sure to include all relevant information. For example, do not omit some items on the agenda. Also do not omit personal events when processing an agenda."""
hint_ignore_year = """If the task asks for emails received in a given month, ignore the year. For example, if the task states "find all emails received in May", consider all emails received in May of any year."""
hint_skip_headers = """If the task description specifies the format of the data, such as what should be in the first row of the spreadsheet, make sure to follow that format. For example, If the task states "the first row should contain the prices", do not include any header row."""

hint_next_week = """If the task asks to schedule an event for next week but does not specify other constraints (such as the participants' schedules, or a specific day of the week), use the current day of the week next week. For example, if today is Monday, choose Monday next week."""
hint_all_recipients = """If the task asks to notify multiple people by email, make sure you have sent emails to each of them using separate calls to `send_email()` before completing the task."""
hint_all_calendars = """If the task asks to schedule a meeting between two or more people, add the event to each of their calendars."""
hint_named_calendar = """To read a specific named calendar file, use `list_events(calendar_name)` instead of `list_events(user_name)`."""
hint_units = """When extracting data from one file to another, do not forget to include the units or currency, if given. For example, if the original source mentions "$100", include "$100" in the output file."""

hint_task_specific = """In the task: "find the lowest cost in budget item, add to highest cost in budget excel file" you should overwrite the existing cell that contains the highest cost with the new value."""

example1 = """Task: extract text from power failure notification image, save in power_failure.pdf, send email power_failure.eml to notify workers Bob and Tom.
Example Solution:
1. Use `ocr_recognize_text()` to extract text from the image file and print the content.
2. Create a new Word file using `word_create_new_file()`.
3. Write the extracted text into the new Word file uswithing `word_write_to_file()`.
4. Convert the new Word file to PDF "power_failure.pdf" with `word_convert_to_pdf()`.
5. Send emails using `send_email()` to notify both Bob and Tom about the power failure. The email subject should be "power_failure" and the content should include the extracted information from the image."""

example2 = """Task: Scan Conference Invitation PDF and search for conference date (If no time is specified, use 6:00 am as default start time), add event to that date on calender, save as invitation.ics, record date, location, conference name, etc. in excel conference.xlsx
Example Solution:
1. Use `pdf_read_file()` to read the PDF file content and print it.
2. Manually review the content to identify the required information using reasoning.
3. Create a new Excel file with `excel_create_new_file()`.
4. Use `excel_set_cell()` to write the required information into the Excel file.
5. Create a new event in the calendar using `create_event()` with the appropriate date and time.. In the event summary, include all key information. If no time is given, use 06:00:00 as the start time."""

example3 = """Task: if Dean's list requires term average gpa to be higher than 3.9, how many terms can this students be awarded on Dean's list?
Example Solution:
1. Use `os.listdir(data_path)` to view the files in the task files folder.
2. use `ocr_recognize_text()` to read the transcript.
3. Manually review and list the number of term-specific GPAs higher than 3.9. Do not count the Cumulative GPAs.
4. Create a Python list out of the qualifying terms and use the `len()` function to count the length of the list.
"""

example4 = """Task: schedule a reward meeting to the top-three students in midterm2, write reward statement in statement.pdf
Example Solution:
1. Use `os.listdir(data_path)` to view the files in the task files folder.
2. Use `excel_read_file()` to read the exam scores file.
3. Inspect the file content manually or programmatically to find the students with the top three scores in midterm2.
4. Schedule a meeting in the calendar for the top three students and Bob using `create_event()`.
5. Create a new Word file using `word_create_new_file()` and write a reward statement mentioning the top three students' names in the new file using `word_write_to_file()`.
6. Convert the Word file to statement.pdf using `word_convert_to_pdf()`.
"""

COMBINED_HINTS_DEEPSEEKV3 = [

    hint_one_action_per_step,
    hint_new_file_path,
    hint_ls_data_path,
    hint_input_data_path,
    hint_format,
    hint_return_value,
    """You are provided with tools to operate on Excel, Word, PDF, Email, Calendar, and Image files. Below are hints for working with these different file types.""",
    hint_calendar_event_summary,
    hint_excel_get_values,
    hint_excel_create_bf_write,
    hint_excel_write_to_file,
    hint_excel_add_header,
    hint_excel_cell_value,
    hint_excel_swap,
    hint_excel_verify_bf_completing,
    hint_word_create_bf_write,
    hint_word_write_to_file,
    hint_word_verify_bf_completing,
    hint_email_full_content,
    hint_email_list,
    hint_email_name,
    hint_new_pdf,
    hint_info_from_pdf,
    hint_extract_info_from_pdf,
    ocr_results_mistakes,
    hint_compatible_string,
    hint_output_file_name,
    hint_extract_info_from_text,
    hint_view_task_files,
    hint_verification,
    hint_summary,
    hint_commitments,
    hint_no_overwrite,
    hint_new_column,
    hint_inspect_data,
    hint_remove_header,
    hint_indexing,
    hint_complete_task,
    hint_read_emails,
    hint_create_event,
    hint_capitalization,
    hint_agreement_terms,
    hint_date,
    hint_calendar_user,
    hint_complete_information,
    hint_ignore_year,
    hint_skip_headers,
    hint_next_week,
    hint_all_recipients,
    hint_all_calendars,
    hint_named_calendar,
    hint_units,
    hint_task_specific,
    """Below are examples of how to solve the tasks:""",
    example1,
    example2,
    example3,
    example4,
]