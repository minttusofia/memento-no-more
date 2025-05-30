hint_data_path1 = """Very important: Never reassign the variable `data_path`! It is already set to the task files folder and loaded to the global namespace. You can simply refer to it in your code. You WILL FAIL the task if you modify this variable!"""
hint_placeholders = """Note that the code you write will be executed as is. Do not set any placeholder values that a user needs to set later."""
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
hint_email_order = """To find the date an email was received, use `read_email(user_name, email_id)`. Do not assume the emails returned by list_emails() are in chronological order."""
hint_email_list = """Use `list_emails(username)` to list all emails for a specific user."""
hint_email_name = """The output .eml file will automatically be named after the subject of the email."""


hint_extract_info_from_text = """Print the file content and manually read the text to extract the required information. Do not extract it programmatically."""
hint_view_task_files = """When you find out your task files, always remember to view its content. If the file is an image, use `ocr_recognize_text()` to extract the text and print it."""
hint_output_file_name = """When creating a new file, make sure to exactly adhere to the requested file name according to the task description."""
hint_verification = """Before completing the task, verify that you have completed all the required steps stated in the task description."""
hint_summary = """When a task requires you to extract information from a source file and write it into a new file, make sure to include all relevant information in the new file."""

hint_date = """Assume today's date as specified in the task description. Do not use the current date or time from the system. For example, if the task states "today is 2022-10-24", use that date for all calculations and comparisons."""
hint_commitments = """Do not consider personal events like sleep when asked about a person's commitments for the day."""

hint_rounding = """If the task asks you to round a number "without decimal", you should round the number to the nearest integer."""
hint_output_file = """Pay close attention to whether the task requires you to create a new file or to modify an existing one. If the task description does not mention the creation of any new file, then a new file is not expected."""
hint_remove_header = """If you delete all values in a row or column, also remove the header name. Do not leave headers in place for empty rows or columns."""
hint_modify_manually = """If the task requires you to modify or reorder data in a spreadsheet, do not attempt to do this modification programmatically. Instead, write out an explicit call to `excel_set_cell()` for each cell you need to modify."""
hint_agreement_terms = """When extracting legal terms from a contract, make sure to include all terms exactly as specified, without paraphrasing the terms."""
hint_complete_task = """If the task is a question requiring a final answer, use the second argument to `complete_task()` to provide the answer. For example, `complete_task("The answer is:", "100")`."""
hint_answer_format = """Make sure to respect exactly the specified answer format or formats. For example, if the task asks to answer with yes/no and a number, make sure to include both in the second argument to `complete_task()`."""

hint_calendar_user = """Create events in the calendars of the relevant person or all relevant people (who should attend the event) as implied in the task. Note that the relevant person is not necessarily Alice."""
hint_events = """If you are asked about events and no particular input file has been mentioned, you should check the user's calendar for event information."""
hint_skip_headers = """If the task description specifies the format of the data, such as what should be in the first row of the spreadsheet, make sure to follow that format. For example, If the task states "the first row should contain the prices", do not include any header row."""
hint_next_week = """If the task asks to schedule an event for next week but does not specify other constraints (such as the participants' schedules, or a specific day of the week), use the current day of the week next week. For example, if today is Monday, choose Monday next week."""
hint_named_calendar = """To read a specific named calendar file, use `list_events(calendar_name)` instead of `list_events(user_name)`."""
hint_output_path = """If the task specifies that an output file should be created in a specific directory, create this directory under `data_path` and save the file there."""
hint_email_title = """If the task specifies a .eml file name of an email, use this exact string as the email subject when sending the email. For example, if the file name is "exam.eml", use "exam" as the email subject."""
hint_email_attachments = """All emails should be self-contained. You will not be able to send attachments."""

hint_data_path2 = """Note that data_path is a read-only variable and already loaded to the namespace, avoid modifying it."""

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

COMBINED_HINTS_GPT4o = [
    hint_data_path1,
    hint_placeholders,
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
    hint_email_order,
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
    hint_date,
    hint_commitments,
    hint_rounding,
    hint_output_file,
    hint_remove_header,
    hint_modify_manually,
    hint_agreement_terms,
    hint_complete_task,
    hint_answer_format,
    hint_calendar_user,
    hint_events,
    hint_skip_headers,
    hint_next_week,
    hint_named_calendar,
    hint_output_path,
    hint_email_title,
    hint_email_attachments,
    hint_data_path2,
    """Below are examples of how to solve the tasks:""",
    example1,
    example2,
]