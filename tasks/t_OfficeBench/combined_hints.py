hint_one_action_per_step = """Perform only one action in one step. For example, only read one person's calendar in one step."""

hint_new_file_path = """When creating a new file, store it in `data_path`. For example, if the file name is `test.docx`, use `os.path.join(data_path, "test.docx")` as the file path. Do not use `test.docx` as the file path directly, as this will not save the file in the correct task files folder."""

hint_new_dir_path = """If the data_path directory does not exist, please create it using os.makedirs(data_path)."""

hint_input_data_path = """When reading from data_path, use `os.path.join(data_path, "file_name")` to set the full path of the file with the correct separators."""

hint_format = """Stricty follow the format mentioned in the task description if there is any."""

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
hint_summary = """When a task requires you to extract information from a source file and write it into a new file, make sure to include all relevant information in the new file, without skipping any fields."""
hint_multiple_files = """If the task requires you to output information in multiple file formats, make sure each output file contains the full information. Do not skip any fields for brevity."""

hint_commitments = """Do not consider personal events like sleep when asked about a person's commitments for the day."""
hint_common_time = """When looking for a suitable meeting time, first write out all the scheduled events' start and end times in chronological order. Then, merge consecutive intervals in your list into one to have fewer intervals to consider. Repeat this for all participants before comparing the schedules. After these steps, it will be possible to find available slots. Do not skip any of these steps."""
hint_verify_constraints = """If you are asked to make a decision according to some constraints, make sure to verify the constraints are satisfied before executing the decision. For example, if you are asked to schedule a meeting, verify your chosen time slot does not overlap with any existing events of any participant before scheduling it!"""

hint_rounding = """If the task asks you to round a number "without decimal", you should round the number to the nearest integer."""
hint_daily_salary = """If the task asks you to calculate an average daily salary where the copmensation breakdown is given per year, you should add up the compensation components and divide by 365."""
hint_include_label = """If the task asks you to add a new element to a spreadsheet and includes a name for the element, make sure to include the name as a label (column or row label, matching the existing format of the spreadsheet) using the exact spelling and capitalization as specified.\nThe name of an element will be given with single quotes, like this: "if budget grow 10% per year, add 'predicted budget' for 3 years later to the last row in budget excel file, round with no decimal"."""
hint_math = """Do not perform mathematical operations in the inner monologue. Use ipython steps for calculations."""
hint_data_counting = """Always inspect the data and take any header rows into account when asked to modify the data. For example, if the task asks you to modify the data of the 5th staff member but there is a header row, the 5th member's data may be in the 6th row."""
hint_remove_header = """When deleting all values in a row or column, also remove the header name (typically, the first cell of the row or column). Do not leave empty rows or columns."""
hint_copy_data = """In spreadsheet tasks, copy the relevant data from specific cells programmatically into a list. Do not attempt to copy it manually, as it is easy to make mistakes."""
hint_string_processing = """Do not attempt to use string processing to extract data from a spreadsheet. Use excel_get_cell() calls instead."""
hint_copy_before_compare = """If you need to count or filter data in a file according to a greater than or less than comparison, first manually copy the entire row or column of data into a Python list. Then, perform the comparison programmatically in Python. This will avoid many mistakes."""
hint_programmatic = """When dealing with lists of more than 6 items in tasks with structured data where simple operations are enough (e.g. checking the length of the list, greater-than checks for numbers, or exact string matching), use programmatic analysis to avoid miscounting or misreading the data. In other cases, such as with unstructured data or with few elements, use manual analysis."""
hint_agreement_terms = """When extracting legal terms from a contract, make sure to include all terms exactly as specified, without paraphrasing the terms."""
hint_email_dates = """In any task requiring knowledge of email dates, always check the dates of all emails individually, one per step, using print(read_email(user_name, email_id))."""

hint_all_calendars = """If the task asks to schedule a meeting between two or more people, add the event to each of their calendars."""
hint_date = """Assume today's date as specified in the task description. Do not use the current date or time from the system. For example, if the task states "today is 2022-10-24", use that date for all calculations and comparisons. This includes expressions such as "last year": assume they are relative to the date specified in the task description."""
hint_txt_file = """If you are asked to produce a .txt file, use the Python built-in function open(..., 'w') to create and write to the file. Do not use the Word or PDF related functions to do so, as they are not compatible with .txt files."""
hint_email_attachments = """All emails should be self-contained. You will not be able to send attachments."""
hint_events = """If you are asked about events and no particular input file has been mentioned, you should check the user's calendar for event information."""
hint_skip_headers = """If the task description specifies the format of the data, such as what should be in the first row of the spreadsheet, make sure to follow that format. For example, If the task states "the first row should contain the prices", do not include any header row."""
hint_list_length = """If you need to know the length of a list, use the Python function `len()` to get it. Do not attempt to count the elements manually, as it is easy to miscount."""
hint_statistics = """Do not attempt to calculate statistics like mean, median, or mode manually. Use Python functions to do so."""

hint_pdf_inputs = """If you are given PDF files as input, use the `pdf_read_file()` function to read the file content. Get the information from the original files rather than after any file conversions."""
hint_next_week = """If the task asks to schedule an event for next week but does not specify other constraints (such as the participants' schedules, or a specific day of the week), use the current day of the week next week. For example, if today is Monday, choose Monday next week."""
hint_schedule_event = """If you are asked to schedule an event and the start or end times are already implied in the input files, use those times."""
hint_create_image = """To create a jpg file, first create a PDF and then use `pdf_convert_to_image()` to convert it to a jpg."""
hint_list_of_criteria = """When reviewing inputs according to a list of review criteria, make sure to check and write out your reasoning for each criterion one by one. Do not attempt to check all criteria at once, as it may lead to missing some important details."""
hint_email_title = """If the task specifies a .eml file name of an email, use this exact string as the email subject when sending the email. For example, if the file name is "exam.eml", use "exam" as the email subject."""
hint_calendar_user = """Create events in the calendars of the relevant person or all relevant people (who should attend the event) as implied in the task. Note that the relevant person is not necessarily Alice."""
hint_excel_operations = """Do not use Excel functions, like SUM(A1:A3), to perform calculations. Calculate all values using Python and write them to Excel using `excel_set_cell()`."""
hint_descriptive_names = """Give descriptive summaries to all events you create. Include all information you have about the event."""
hint_verify_multiple_files = """If you need to inspect multiple files, do not attempt to read them in the same step. Inspect one file per ipython step to ensure all outputs are shown."""
hint_capitalization = """If an output file name is specified, use that exact name and pay attention to capitalization."""
hint_calendar_files = """Do not try to manually create calendar files. Only use the provided functions to manage calendar events. For example, use `create_event()` to create a new event in the calendar."""

hint_overwrite = """You are expected to overwrite data if it is implied by the task description. For example, if you are asked to add the cost of item B to the cost of item A, but no new header name or file name is given, you should overwrite the cost of item A with the sum of both items."""
hint_output_file = """Pay close attention to whether the task requires you to create a new file or to modify an existing one. If the task description does not mention the creation of any new file, then a new file is not expected. In this case, add the new information to the input file instead."""

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


COMBINED_HINTS = [

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
    hint_multiple_files,
    hint_commitments,
    hint_common_time,
    hint_verify_constraints,
    hint_rounding,
    hint_daily_salary,
    hint_include_label,
    hint_math,
    hint_data_counting,
    hint_remove_header,
    hint_copy_before_compare,
    hint_programmatic,
    hint_agreement_terms,
    hint_email_dates,
    hint_all_calendars,
    hint_date,
    hint_txt_file,
    hint_email_attachments,
    hint_events,
    hint_skip_headers,
    hint_list_length,
    hint_statistics,
    hint_pdf_inputs,
    hint_next_week,
    hint_schedule_event,
    hint_create_image,
    hint_list_of_criteria,
    hint_email_title,
    hint_calendar_user,
    hint_excel_operations,
    hint_descriptive_names,
    hint_verify_multiple_files,
    hint_capitalization,
    hint_calendar_files,
    hint_overwrite,
    hint_output_file,
    """Below are examples of how to solve the tasks:""",
    example1,
    example2,
    example3,
]