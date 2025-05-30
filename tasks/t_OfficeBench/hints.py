hint_one_action_per_step = """Perform only one action in one step.
"""

hint_calendar_free_slot = """To solve this task, you should:
            1. List Bob's calendar events. Manually check the time slots for each event and identify 1-hour free slots.
            2. List Tom's calendar events. Manually check the time slots for each event and identify 1-hour free slots.
            3. Manually find a common 1-hour free slot available for both Bob and Tom.
            4. Create a new event '{event}' in both Bob's and Tom's calendars.
            Note that do not list Bob's and Tom's events in the same step."""

hint_excel_get_cell_id = """Use `excel_read_file` to view the file content (you can print it) and manually identify the row and column id to work on. Do not determine the indices programmatically."""

hint_excel_get_values = """Do not obtain cell values programmatically for calculations / comparison. Instead, manually inspect the file content to find the required values before performing calculations / comparison."""

hint_excel_verify_bf_completing = """Before completing the task, use `excel_read_file` to view the file content to verify that the file content is correct."""

hint_excel_write_to_file = """After creating a new Excel file, always remember to write the information into the new Excel file using `excel_set_cell()`."""

hint_word_write_to_file = """After creating a new Word file, always remember to write the information into the new Word file using `word_write_to_file()`."""

hint_word_verify_bf_completing = """Before completing the task, use `word_read_file` to view the file content to verify that the file content is correct."""

hint_new_file_path = """When creating a new file, store it in `data_path`. For example, if the file name is `test.docx`, use `os.path.join(data_path, "test.docx")` as the file path. Do not use `test.docx` as the file path directly, as this will not save the file in the correct task files folder."""

hint_new_dir_path = "If the data_path directory does not exist, please create it using os.makedirs(data_path)."

hint_new_pdf =  "To create a PDF file, first create a Word file and then convert it to PDF using word_convert_to_pdf."

hint_input_data_path = """When reading from data_path, use `os.path.join(data_path, "file_name")` to set the full path of the file with the correct separators."""

hint_format = """Strictly follow the format mentioned in the task description."""

hint_extract_info_from_text = """Print the file content and manually read the text to extract the required information. Do not extract it programmatically."""

hint_ls_data_path = """Use `print(os.listdir(data_path))` to see the files in the folder."""

ocr_results_mistakes = """The OCR tool may return some wrong characters. Please attempt to correct any obvious mistakes you spot, such as 'd' replaced by 'a', or missing characters."""

hint_compatible_string = """If you get the error 'All strings must be XML compatible: Unicode or ASCII, no NULL bytes or control characters', manually extract the plain text content from the OCR output to exclude problematic characters. Do not attempt to fix the OCR output programmatically."""

HINTS = {
    "1-1":{
        "3":[
            """The event summary should be detailed and be exactly as mentioned in the task description. For this task, you need to mention the place of the class in the event summary.""",
        ]
    },
    "1-2":{
        "0":[
            hint_one_action_per_step,
            hint_calendar_free_slot.format(event="meeting"),
        ],
        "2":[
            hint_one_action_per_step,
            hint_calendar_free_slot.format(event="shopping"),
        ],
        "4": [
            hint_one_action_per_step,
            """Note: Not all events in the calendar are commitments. Only events that involve an appointment with others should be considered."""
        ]
    },
    "1-4":{
        "2":[
            hint_one_action_per_step,
            hint_excel_get_cell_id,
        ],
    },
    "1-5":{
        "2":[
            hint_excel_get_cell_id,
            hint_excel_get_values,
            """Add a new row at the bottom of the table. In the 'Name' column, write "average salary per day" (exactly as stated in the task). In the 'amount' column, compute the average yearly salary by summing all the amounts and divide the total by 365, then round to the nearest whole number (no decimals). Ensure both cells are filled.""",
        ],
        "3": [
            hint_ls_data_path,
            hint_excel_get_cell_id,
            hint_excel_get_values,
            """Add a new row at the bottom of the table. In the 'Name' column, write "predicted budget" (exactly as stated in the task). In the 'amount' column, calculate the total budget by summing all existing 'amount' values (i.e., salary, computer, entertain), then multiple the sum by (1.1**3). Ensure both cells are filled.""",
            
        ]
    },
    "1-6": {
        "0": [
            hint_excel_get_cell_id,
            """First, add a new header named 'Class'.""",
            """The value of each cell should be a string.""",
            hint_excel_verify_bf_completing,        
        ],
        "2": [
            hint_excel_get_cell_id,
            """First, add a new header named 'Meeting'.""",
            """Do not use `datetime.timedelta` or similar programmatic methods to generate the meeting times. Instead, manually write the start time for each student in 10-minute increments starting from 8:00 — for example: 8:00, 8:10, 8:20, 8:30""",
            hint_excel_verify_bf_completing,
        ],
        "4": [
            hint_excel_get_values,
        ],
        "5":[
            """Use `excel_set_cell()` to set the value of the header and the value of the new column. Do not parse the excel programmatically using loops.""",
        ]
    },
    "1-7":{
        "1":[
            hint_excel_get_cell_id,
            """Note that the third student's score is recorded in the fourth row. You should use,e.g., `excel_delete_cell(..., 4, ...)` to remove the score in the fourth row for the third student.""", 
        ],
    },
    "1-8":{
        "1":[
            hint_excel_get_cell_id,
            """Remove only the 'Class' header and the class information. Do not delete student names.""",
            hint_excel_verify_bf_completing,
        ],
        "2":[
            hint_excel_get_cell_id,
            """Do not forget to remove the 'amount' header.""",
            hint_excel_verify_bf_completing
        ],
        "3": [
            hint_excel_get_cell_id,
            """Do not parse the excel file or delete the content programmatically (e.g., using loops). To solve this task, you should: 1. Use `excel_read_file()` to view the file content. 2. Use `excel_delete_cell()` to delete the content of each cell that contains a value, one by one.""",
            hint_excel_verify_bf_completing,
        ]
    },
    "1-9":{
        "0":[
            hint_excel_get_values,
            """
            Strictly follow the solution steps:
            1: read the excel file and inspect its content. Do not parse the file programmatically.
            2. To compute the average for midterm1: Identify the column labeled midterm1. Read each student's score from this column. Add all the scores together and divide by the total number of students (rows excluding the header, so there are 20 students). Do not use loops or programmatic methods obtain values for calculations.
            3. Repeat the same process for midterm2, using the values under that column.
            4. When modifying the table: Do not overwritten the original bottom row (the last student's row). Insert a new row at the bottom of the table by excel_set_cell(). Write 'Average' in the first column of this row. Enter the computed average values under the midterm1 and midterm2 columns, respectively."""

        ],
        "1":[
            hint_excel_get_values,
            """Strictly follow the solution steps:
            1: read the excel file and inspect its content. Do not parse the file programmatically.
            2. Compute the average for midterm1: Identify the column labeled midterm1. Read each student's score from this column. Add all the scores together and divide by the total number of students (rows excluding the header, so there are 20 students). Do not use loops or programmatic methods obtain values for calculations.
            3. Compare each student's midterm 1 score with the average, to find the student whose midterm1 score is closest to the average."""

        ],
        "3":[
            hint_ls_data_path,
            hint_excel_get_cell_id,
            hint_excel_get_values,
            """Add a new row at the bottom of the table. In the 'Name' column, write "Total" (exactly as stated in the task). In the 'amount' column, calculate the total cost by summing all existing 'amount' values (i.e., salary, computer, entertain). Ensure both cells are filled.""",
            hint_excel_verify_bf_completing,
        ],
        "4":[
            hint_excel_get_cell_id,
            hint_excel_get_values,
            hint_excel_verify_bf_completing,
        ],
        "5":[
            hint_excel_get_cell_id,
            hint_excel_get_values,
            """Add a new row at the bottom of the table. In the 'Name' column, write "Average" (exactly as stated in the task). In the 'amount' column, calculate the average amount. Ensure both cells are filled.""",
            hint_excel_verify_bf_completing,
        ],
    },
    "1-10":{
        "0":[
            hint_excel_get_values,
            """Do not parse the excel programmatically."""
        ],
        "1":[
            """Strictly follow the solution steps:
            1. Import os and use print(os.listdir(data_path)) to list all files in the folder. Identify the name of the Excel file.
            2. Use `excel_read_file()` to display the full Excel file content.
            3. For each row (starting from row 2), manually compare the values in the midterm1 and midterm2 columns:
                if the value in midterm2 is less than the value in midterm1, include the student's name in your answer.
            Do not process the entire table programmatically. Instead, visually inspect the values row by row.
            4. Important: Since this task requires a final answer, you should provide `return_value` in `complete_task()`: `complete_task("The answer is:", your_answer)`""",
        ],
        "2":["""Strictly follow the solution steps:
            1. Import os and use print(os.listdir(data_path)) to list all files in the folder. Identify the name of the Excel file.
            2. Use `excel_read_file()` to display the full Excel file content.
            3. Visually inspect the rows and determine which one has the highest value in the 'amount' column.
            4. Use `set_excel_cell()` to duplicate that row at the bottom of the table (in a new row).""",
        ],
        "3":[
            hint_excel_get_values,
            """Do not write the result to a new cell. Instead, overwrite the existing cell that contains the highest cost with the new value.""", 
        ],
        "4":[
            hint_excel_get_values,
        ]
    },
    "1-11":{
        "0":
            [
            """Print the Excel file content to manually view the midterm 1 scores. Manually sort the students by their scores in descending order and write into a new file instead of sorting them programmatically.""",
            """When writing into the new file, also remember to write midterm2 scores for each student, although they are sorted by midterm1 scores.""",
        ],

        "1":
            [
            hint_ls_data_path,
            """Strictly follow these steps:
            1. Use `excel_read_file()` to display the full Excel file content.
            2. Use `excel_create_new_file(os.path.join(data_path, 'midterm1.xlsx'))` and`excel_create_new_file(os.path.join(data_path, 'midterm2.xlsx'))` to create two new excel files. 
            3. After creating the new files, you must write data into them using `set_excel_cell()`. In midterm1.xlsx, manually write each student's name and their midterm1 score.xlsx. In midterm2.xlsx, manually write each student's name and their midterm2 score.  Do not copy or generate the content programmatically. 
            Creation is not sufficient — you must populate both new files row by row.""",
            hint_excel_verify_bf_completing
        ],
        "2":
            [
            hint_excel_get_cell_id,
            hint_excel_get_values,   
        ],
        "3": [
            """Do not parse the excel file programmatically. Instead, manually check the file content to sort the item by your reasoning.""",
        ]
    },
    "1-12":{
        "0":[
            """Display the Excel file content and manually check the following separately: 1. The total number of students 2: The number of senior students based on the 'Academic Standing' column.""",
            """Count the total number of student rows by subtracting 1 (the header) from the total number of rows: If there are 10 rows in total in this file. One row is used as the header, so there are 9 rows for each student, then totally 9 students. Go through the file output row by row and find all students who are the senior.
            Do not use code or loops to process the data — inspect it manually.""",
            """Since this task requires a final answer, you should provide `return_value` in `complete_task()`: `complete_task([YOUR_REPORT], [YOUR_FINAL_ANSWER])`"""
        ],
        "1":[
            """Print the Excel file content and manually count how many students have a final score of 60 or higher by your reasoning. Do not count them programmatically. In your monologue, explain your thought process as you examine the scores.""", 
        ],
    },
    "1-13":{
        "0":[
            """Do not parse the excel file programmatically. Instead, manually check the file content to find whether CS101, CS 102, Math 151, and Math 152 were taken by visually inspecting the file and your reasoning.""",
        ],
        "1":[
            """Print the Excel file content and manually check the number of CS courses. Do not count them programmatically.""",
        ],
        "2":[
            """Print the Excel file content and manually check the number of CS courses and Math courses. Do not count them programmatically.""", 
        ],
    },
    "1-14":{
        "1":[
            """Use `excel_read_file()` to view the full content of the Excel file. Then, for each row, manually swap the values using `set_excel_cell()`. Do not perform the swap programmatically — inspect each row and update the cells one by one to switch the two values. Remember to swap the header as well.""",
            """Important: Always perform the swap operations after reading the file content. Do not complete the task before solving it.""",
        ],
        "2":[
            """Manually identify the items with the lowest and highest incoming. Then, use `set_excel_cell()` to swap the positions of these two items in the table manually. The swap operation should be performed on the whole row, so you must swap both 'Name' and 'amount'. Do not sort or process the data programmatically!""",
        ],
        "3":[
            """Manually identify the items with the fewest and second fewest quantities by examining the 'amount' column. Once identified, use `set_excel_cell()` to swap the positions of these two items in the table manually. The swap operation should be performed on the whole row, so you must swap both 'Name' and 'amount'. Do not sort or process the data programmatically.""",
            """Note that the cell value must be a string, even for numbers. For example, to set the value of a cell in the second row and the second column to 3, use `set_excel_cell(..., '3', 2, 2)`.""",
        ]
    },
    "1-16":{
        "0":[
            hint_ls_data_path,
            hint_new_file_path,
            """Write the content of random_paragraph.txt to the word file. Do not write other content to the word file.""",
        ],
        "1":[
            hint_new_file_path,
        ],
    },  
    "1-18":{
        "0":[
            """To solve this task, you should:
            1. Use `pdf_read_file()` to read the file content and print it.
            2. Manually check the content to find the required information.
            3. Create a new Word file by `word_create_new_file()`.
            4. Write the required information into the new Word file using `word_write_to_file()`.
            5. Convert the new Word file to PDF using `word_convert_to_pdf()`.
            6. Convert this PDF file to image using `pdf_convert_to_image()`.""",
        ],
        "1":[
            """To solve this task, you should:
            1. Use `pdf_read_file()` to read the file content and print it.
            2. Manually check the content to find the required information.
            3. Create a new Word file by `word_create_new_file()`.
            4. Write the required information into the new Word file using `word_write_to_file()`.
            5. Convert the new Word file to PDF using `word_convert_to_pdf()`.""",
        ],
    },
    "1-19":{
        "2":[
            """To solve this task, you should:
            1. Use `pdf_read_file()` to read the file content and print it.
            2. Manually check the content to find the required information.
            3. Create a new Word file by `word_create_new_file()`.
            4. Write the required information into the new Word file using `word_write_to_file()`.
            5. Convert the new Word file to PDF using `word_convert_to_pdf()`.
            6. Convert this PDF file to image using `pdf_convert_to_image()`.""",
        ],
        "3":[
            hint_extract_info_from_text,
            hint_format
        ],
        "4":[
            hint_extract_info_from_text,
            """In your summary, include all content from the '2. Terms' section. Make sure to copy this section exactly as it appears, without summarizing, rephrasing, or omitting any part of it.""",
        ]
    },
    "1-20":{
        "0":[
            """Strictly follow the solution steps:
            1. use `list_email()` to get all emails' ids; 
            2. Use `read_email(user_name, email_id)` to read each email one at a time. In a single step, you can only read one email! Do not call `read_email()` for all emails at once. When viewing each email, identify the date manually.
            3. Determine if this email was sent in last three months (from 2024-03-01 to 2024-05-01) by your reasoning.
            3. Provide the final answer, e.g.`complete_task("The subjects of the emails received in the last three month are:", Their Subjects)`. Note that the answer should be a string."""    

        ],
        "1":[
            """Strictly follow the solution steps:
            1. use `list_email()` to get all emails' ids; 
            2. Use `read_email(user_name, email_id)` to read each email one at a time. In a single step, you can only read one email! Do not call `read_email()` for all emails at once. When viewing each email, identify the date manually. You must complete the reading of **all four emails** before providing the final answer.
            3. Compare the date of each email using your reasoning to determine which is the earliest email.
            3. Provide the final answer, e.g.`complete_task("The subjects of the earliest email is:", [The Email Subject])`."""    

        ],
        "2":[
            """Strictly follow the solution steps:
            1. use `list_email()` to get all emails' ids; 
            2. Use `read_email(user_name, email_id)` to read each email one at a time. In a single step, you can only read one email! Do not call `read_email()` for all emails at once. When viewing each email, identify the date manually.
            3. Compare the date of each email using your reasoning to determine which is the latest email.
            3. Provide the final answer, e.g.`complete_task("The content of the latest email is:", [CONTENT of the EMAIL])`."""    

        ],
        "3":[
            """For this task, strictly follow these steps:
            1. Use `list_email()` to get all emails' ids.
            2. Use `read_email(user_name, email_id)` to read each email one by one. When viewing each email, identify the date manually.
            3. Determine if Bob received emails in the last month by your reasoning based on the date of each email.
            4. Provide the final answer. **The answer includes yes or no and the number of the email.** If he received emails in the last month, then the answer should be, e.g., 'yes, [Number_Of_Emails]'. Use `complete_task("The answer is:", your_final_answer)` to provide the final answer."""   
        ],

    },
    "1-21":{
        "0":[
            """For this task, you should: 1. use `list_email()` to get all emails' ids; 2. Use `read_email(user_name, email_id)` to read each email one by one. When viewing each email, identify the date manually. Use your reasoning to decide which email is the latest one based on the date of each email. 3. The answer is subject of the latest email."""
        ],
        "1":[
            """Strictly follow the solution steps:
            1. use `list_email()` to get all emails' ids; 
            2. Use `read_email(user_name, email_id)` to read each email one at a time. In a single step, you can only read one email! Do not call `read_email()` for all emails at once. When viewing each email, identify the date manually. You must complete the reading of **all four emails** before providing the final answer.
            3. Compare the date of each email using your reasoning to determine which is the earliest email.
            3. Provide the final answer, e.g.`complete_task("The subject of the earliest email is:", [SUBJECT of the EMAIL])`."""   

        ],
        "2":[
            """Strictly follow the solution steps:
            1. Use `list_email()` to get all emails' ids; 
            2. Use `read_email(user_name, email_id)` to read each email one by one. In a single step, you can only read one person's email! Do not call `read_email()` for all emails at once. When viewing each email, identify the date manually. 
            3. Determine if Bob receive emails in the last month by your reasoning based on the date of each email.""",
        ],

    },
    "1-23":{
        "0":[
            hint_excel_get_values,
        ],
        "1":[
            """Read the excel by using `excel_read_file()`. Count the number of rows where the 'Academic Standing' is 'Freshman' by visually inspecting the excel file content. Do not parse the excel file programmatically. Decide your answer based on your reasoning.""",
            ]
    },

    "2-1":{
        "0":[
            hint_ls_data_path,
            hint_new_pdf,
            hint_compatible_string,
        ],
        "2":[
            hint_compatible_string,
        ],
    },

    "2-2":{
        "0":[
            """You must strictly follow it: In your first step, import `os` and use `os.listdir(data_path)` to list all files in the folder. Do not assume the file name. The file name is not 'Concert Announcement.pdf'""",
        ],
        "1":[
            """You must strictly follow it: In your first step, import `os` and use `os.listdir(data_path)` to list all files in the folder. Do not assume the file name. The file name is not 'Concert Announcement.pdf'""",
        ],
    },
    "2-3":{
        "0":[
            """Create a new word file. Use `word_write_to_file()` to write the content of the pdf file into a Word file. Then, use `word_convert_to_pdf()` to convert the Word file to a PDF file. Finally, use `pdf_convert_to_image()` to convert the PDF file to an image post.""",
        ]
    },

    "2-5": {
        "0":[
            hint_extract_info_from_text,
        ],
    },
    "2-6":{
        "0":[
            """Use `ocr_recognize_text()` to first recognize the text from the image."""
        ]

    },
    "2-10":{
        "0":[
            """Use `ocr_recognize_text()` to first recognize the text from the image. Then, use `excel_set_cell()` to write the recognized text into the excel file manually. Do not parse the excel file programmatically.""",
        ],
        "1":[
            ocr_results_mistakes,
            """Student IDs start with an 's'.""",
            hint_extract_info_from_text,
            """Verify that the output file contains all the required information.""",
        ],
    },
    "2-11":{
        "0":[
            "You work for Alice, so you need to find the information about the car bought by Alice."
            "Include all available information, including date and the buyer and seller names.",
            hint_extract_info_from_text,
        ],
        "1":[
            hint_ls_data_path,
            ocr_results_mistakes,
        ]
    },
    "2-12":{
        "0":[
            "To get text from a PDF, use the pdf_read_file() function. Do not convert the PDF to image to extract the text.",
            hint_extract_info_from_text,
            """Note that the meeting date is not today. Extract the date and the time from the agenda. Use the year 2020."""
        ],
    },
    "2-13":{
        "0":[
            """Do not parse the excel file programmatically. Instead, manually check the file content to find the required information.""",
            """Create a new calendar event for each member."""],
        "1":[
            hint_ls_data_path,
            hint_extract_info_from_text,
            """Verify the events have been created in the calendars before completing the task.""",
        ],
    },
    "2-14":{
        "0":[
            """Do not parse the excel file programmatically.""",
            """Create a new calendar event for each student. Do not only create events for Alice."""
        ]
    },
    "2-15":{
        "0":[
            "Do not forget import `os` before creating a new excel file.",
            hint_new_file_path,
            hint_extract_info_from_text,
            "If there are multiple meeting events in the calendar, write all of them into the excel file.",
        ],
    },
    "2-17":{
        "0":[
            "The events should be created in the students' calendars.",
            hint_extract_info_from_text,
            """Verify the events have been created in the calendars before completing the task.""",
        ],
    },
    "2-18":{
        "1":[
            hint_new_file_path,
        ],
        "2":[
            """Use `excel_read_file()` to view the file content.""",
            """Do not parse the excel file programmatically. Manually identify shopping items by visually inspecting the file content and your reasoning. Then, write the shopping items into a new word file.""",
        ],
    },
    "2-20":{
        "0":[
            hint_excel_get_values,
            hint_word_verify_bf_completing,
            """Do not programmatically parse and extract information from the excel file and write it into the word file.""",
            """The students who need taking CS161 are those whose major is CS. Write their names and ID into the word file.""",
        ],
        "1":[
            """Before read any files, in your first step, import `os` and use `os.listdir(data_path)` to list all files in the folder.""",
            hint_excel_get_values,
            """Visually examine the Excel file to find students who are CS majors. Do not parse the file programmatically.""",
            hint_word_verify_bf_completing,
        ],
        "2":[
            """Before read any files, in your first step, import `os` and use `os.listdir(data_path)` to list all files in the folder.""",
            hint_excel_get_values,
            hint_word_verify_bf_completing,
        ]
    },
    "2-21":{
        "0":[
            hint_input_data_path,
            hint_extract_info_from_text,
            hint_word_verify_bf_completing,
        ],
        "1":[
            hint_excel_get_values,
            """Use the word_create_new_file and word_write_to_file functions to create docx files.""",
            hint_extract_info_from_text,
            """Verify the output file contains all the required information.""",
        ],
        "2":[
            "In your first step, import `os`.",
            """Use `excel_read_file` to view the file content.""",
            """Do not parse the excel content programmatically. Instead, manually check the file content to find the required information.""",
            
        ],
        "3":[
            hint_extract_info_from_text,
            hint_word_verify_bf_completing,
        ],
        "4":[
            hint_extract_info_from_text,
        ],
        "5":[
            hint_extract_info_from_text,
            hint_excel_get_values,
            hint_word_verify_bf_completing,
        ],
    },
    "2-22":{
        "0":[
            hint_new_file_path,
        ],
        "1":[
            hint_new_file_path,
        ],
    },
    "2-23":{
        "0":[
            hint_extract_info_from_text,
        ],
        "1":[
            hint_input_data_path,
            hint_new_file_path,
            """If you store the output of `pdf_read_file()` into a variable, you must print it to see the content, e.g., 
            ```pdf_text = pdf_read_file(os.path.join(data_path, 'Invoice_2.pdf'))
            print(pdf_text)```"""
        ],
    },
    "2-24":{
        "0":[
            hint_input_data_path,
            hint_excel_get_values,
        ],
    },
    "2-27": {
        "0":[
            hint_extract_info_from_text,
            "There are 7 agenda items listed in the PDF. Make sure to create a separate calendar event for each item。"
        ],
    },
    "2-29":{
        "0":[
            """Print the PDF file content and manually check the content to find the required information.""",
        ],
    },
    "2-30":{
        "0":[hint_extract_info_from_text,
        ]

    },
    "2-31":{
        "4":[
            "The question is asking about the median of historical values.",
        ]
    },
    "2-32":{
        "0":[
            ocr_results_mistakes,
            hint_extract_info_from_text,
            """Do not use information in the company trading records for calculating. The summarized reimbersement information are in the company budget file. Only consider company expenses clearly marked as reimbursements (Salary Reimbursement + Machine Purchase Reimbursement).""",
            """The reimbursement amount is: number of employees * salary for each + Machine Purchase Reimbursement. Compare the reimbursement amount with Budget for the Year to get the answer.""",
        ],
        "1":[
            ocr_results_mistakes,
            hint_extract_info_from_text,
            "The question is asking if the sum of the prices of sold items is larger than the sum of the prices of bought items.",
            "Be mindful of OCR errors. sola = sold, ten = Item, and sometimes S can mean $.",
            """The OCR result lists columns vertically, and the column headers are: Date, Transaction, Item, Amount. It means:
            All dates come first, followed by all transaction types, then items, and finally amounts.
            To pair a transaction with its date, item, and amount, match entries by their order (e.g., the 1st entry in each column forms the 1st transaction).""",
            # """Here is an example of the format (not the actual data):

            # Name
            # George
            # John
            # Mary
            # Department
            # Engineering
            # HR
            # Sales

            # To find the department for Mary (3rd row), for example, you need to read the 3rd entry in the column 'Department', which is 'Sales'.""",
            """Here is an example of the format (not the actual data):

            Date
            2024-01-01
            2024-01-02
            2024-01-03
            Transaction
            Bought
            sola
            Bought
            ten
            Laptop
            Phone
            Mouse
            Amount
            $200
            $200
            $200

            First, you should correct obvious OCR mistakes. 'sola' means 'sold', and 'ten' means 'Item'.
            The first value in each column corresponds to the first transaction, the second to the second transaction, and so on. For example, the type of the transaction on 2024-01-02 (2nd value in the 'Date' column) is 'sold' (2nd value in the 'Transaction' colum after correction), and the item is 'Phone' (2nd value in the 'Item' colum after correction). The amount for this transaction is $200 (2nd value in the 'Amount' colum)."""
        ],
    },
    "2-33":{
        "0":[
            """Do not parse the excel file programmatically. Instead, manually check the file content to find the required information.""",
        ],
        "1":[
            """In your first step, import `os` and use `os.listdir(data_path)` to list all files in the folder.""",
            hint_extract_info_from_text,
            "To find the class with the least students, first count how many students are in each class.",
        ],
    },
    "2-34":{
        "0":[
            """Do not parse the excel file programmatically. Analyze housing price from the excel by your reasoning like a human would do.""",
        ],
        "1":[
            hint_extract_info_from_text,
        ],
    },
    "2-35":{
        "2":[
            hint_extract_info_from_text,
            """You can import numpy and use numpy.var(ages) to calculate the variance of ages.""",
            hint_new_file_path,
        ],
    },
    "2-36":{
        "0":[
            "The output file should be called report.docx. Make sure to exactly adhere to the requested file name."
        ],
        "1":[
            hint_ls_data_path,
            # "Manually check the file content to find the required information. Do not parse it programmatically.",
            # "Use the term-specific GPAs in your calculation, not the Cumulative GPA.",
            # """Course-specific grades are given as letters immediately after the course, e.g. 'Physics A'. To get *term* GPAs, find entries marked as 'GPA', but NOT 'Cumulative GPA', because the latter indicates the average of all terms until that point, not the most recent term.""",
            """Example Solution:
                1. Use `os.listdir(data_path)` to view the files in the task files folder.
                2. use `ocr_recognize_text()` to read the transcript.
                3. Manually review and list the number of term-specific GPAs higher than 3.9. Do not count the Cumulative GPAs.
                For example, for this transcript:
                    Student: Teddy Roosevelt Date of Birth: Oct 27, 1910 Weighted GPA: =. 3..78/4.00
                    Street Address: 1900 Pennsytvania Ave Place of Birth: Manhattan, NY Unweighted GPA: 3.65/4.00
                    City/State/Zip: Washington, DC 20500 Gender: Male
                    Phone: (202) 456-1111 Credits Earned: 23.00
                    Fall Winter
                    Course Grade Credits Course Grade Credits
                    Physical Science A 1.00 Tennis A 1.00
                    U.S. History A 1.00 GPA 4.00 1.00
                    GPA 4.00 2.00 Cumulative GPA 4.00 3.00
                    Cumulative GPA 4.00 2.00
                    Spring Summer
                    Course Grade Credits Course Grade Credits
                    English Composition A 1.00 Algebra! A 1.00
                    Music Appreciation B 1.00 GPA 4.00 1.00
                    GPA 3.50 2.00 Cumulative GPA 3.83 6.00
                    Cumulative GPA 3.80 5.00

                    The term GPAs are 4.00, 4.00, 4.00, 3.50. Do not count the number following 'Cumulative GPA'. The answer is 3.

                4. Create a Python list out of the qualifying terms and use the `len()` function to count the length of the list."""
        ],
        "2":[
            """print the PDF file content and manually check the content to find the required information.""",
            hint_extract_info_from_text,

        ],
        "3":[
            "Manually check the file content to find the required information. Do not parse it programmatically.",
            """Use pdf_read_file to extract the text from a PDF file.""",
        ],
    },
    "2-37":{
        "3":[
            hint_new_file_path,
            hint_new_dir_path,
        ],
    },
    "2-38":{
        "0":[
            "The output .eml file will automatically be named after the subject of the email.",
            "Do not directly read or write .eml files but use the email tools provided."
            "Docx files can be read using the word_read_file() function.",
        ],
    },
    "2-39":{
        "0":[
            hint_new_file_path,
            hint_new_dir_path,
            "Do not forget import `os`.",
            """All output files should be created in the data_path directory.""",
        ],
        "1":[
            hint_new_file_path,
            hint_new_dir_path,
            "Do not forget import `os`.",
        ],
        "2":[
            "Do not forget import `os`.",
            hint_new_file_path,
            """Strictly follow the solution steps:
            1. use `word_create_new_file()` to create a new word file;
            2. use `list_email()` to get all emails' ids; 
            3. Use `read_email(user_name, email_id)` to read each email one at a time. In a single step, you can only read one email! Do not call `read_email()` for all emails at once. After inspecting each email visually, write the content into the word file using `word_write_to_file()`.
            4. Convert the new word file to PDF using `word_convert_to_pdf()`."""

        ],
        "3":[
            hint_new_file_path,
            hint_new_dir_path,
            "Do not forget import `os`.",
            """Strictly follow the solution steps:
            1. use `list_email()` to get all emails' ids; 
            2. Use `read_email(user_name, email_id)` to read each email one at a time. In a single step, you can only read one email! Do not call `read_email()` for all emails at once. When viewing each email, identify the date manually. Use your reasoning to determine whether the email is sent in 2024.
            3. Create a new word file. Write the content of the email in 2024 into this new word file."""
        ],
        "4":[
            hint_new_pdf,
            hint_new_file_path,
            hint_new_dir_path,
            "Do not forget import `os`.",
            "Do not parse the email programmatically.",
        ],
    },
    "2-40":{
        "0":[
            """Visually examine the calendar and identify each event manually. Do not parse the calendar programmatically. For each event you see, send an email to Bob. Use the event's name (summary) as the subject of the email.""",
        ],
        "2":[
            """Visually examine the calendar and identify each event manually. Do not parse the calendar programmatically. Do not include events named 'sleeping'. For each of other events, send an email to Bob. Use the event's name (summary) as the subject of the email."""
        ]

    },
    "2-41":{
        "0": [
            """Use `list_emails()` to visually examine and identify email ID of the work overtime email; then use `read_email()` to view this email's content. 
            Manually check the recipient's name in the email content. For example, if the recipient's email is Bob123@gmail.com, then the recipient's name is Bob. """

        ],
        "1":[
            """Solution steps:
            1. Use `list_emails()` to visually examine and identify email IDs of all emails related to body test; then use `read_email()` to view these emails' content. 
            2. Manually check the recipient's name in these emails. For example, if the recipient's email is Bob123@gmail.com, then the recipient's name is Bob.
            3. For each recipient, create a new calendar event for them.""",
            "Remember to process all Body Test emails, not just one.",
        ],
    },
    "2-42":{
        "0":[
            hint_new_file_path,
            hint_new_dir_path,
            "Do not forget import `os`.",
            """Use the list_emails() tool to list the emails for each user. Manually count how many emails each user has."""
        ],
    },
    "2-44":{
        "0":[
            hint_new_file_path,
            hint_new_dir_path,
            "Do not forget import `os`.",
            hint_extract_info_from_text,
            """Remember to write information of Bob's all emails into the table. Do not write information of only one email into the table."""
        ],
    },
    "2-45":{
        "0":[
            ocr_results_mistakes,
        ],
        "1":[
            ocr_results_mistakes,
            """From the OCR result, find out the staff names by visually checking the file content. Then, use `send_email()` to send all information about business Travel notification to each staff.""",
        ],
    },
    "2-46":{
        "0":[
            hint_extract_info_from_text

        ]
    },
    "2-48":{
        "0":[
            hint_extract_info_from_text,
            """When counting the sleeping time, all events related to sleeping should be considered. For example, the event 'nap' should also be included in the sleeping time calculation."""
        ]
    },
    "2-49":{
        "0":[
            hint_new_file_path,
            hint_new_dir_path,
            """Use the list_emails() tool to list the email to get the email id, then use the read_email() tool to display the content of the email.""",
            """Visually inspect the score table in the email. Do not directly copy the HTML score table in the email. Instead, manually read each student's name and score, and write them into a new Excel file. The Excel file should have two columns with headers: 'Name' and 'Score'.""",
        ],
    },
    "2-50":{
        "0":[
            hint_new_file_path,
            hint_new_dir_path,
            """Use the list_emails() tool to list the email to get the email id, then use the read_email() tool to display the content of the email.""",
            """In the excel file, the cell value format of the revenues column should be, e.g., 1200000, without the $ sign or commas."""
        ],
    },

    "3-2":{
        "0":[
            """When writing the summary in a Word file, Remember to add a title in the first line. The summary should include key, e.g., the company name.""",
        ],
    },

    "3-3": {
        "0":[
            hint_new_file_path,
             """Use word_convert_to_pdf() to get manual.pdf. Then, use `send_email()` to send the PDF file to Alice. Remember to mention the file is a manual in the email."""
        ]
    },

    "3-4":{
        "0":[
            """Use excel_convert_to_pdf() to convert the Excel file to PDF."""
        ]
    },
    "3-5":{
        "0": [
            """Carefully read and visually inspect the two PDF invoices. Obtain the required information by your reasoning. Do parse the content programmatically. After you learn about the invoices, enter the invoice details into an Excel file using `excel_set_cell()` and write keywords that describe the types of services into a Word file using `word_write_to_file()`."""
        ]

    },

    "3-6": {
        "0":[
            hint_new_file_path,
             """To solve this task, follow these steps: 
             1. Creating a New Event for Alice:
                    Print the Excel file content and manually check Alice's section and training time based on her row;
                    Create a new event 'team training' in Alice's calendar. When setting the date, use 2020-05-01 as stated in the task, so the date of next week is 2020-05-08. Do not use `datetime.now()` to get the current date!
             2. Sending Emails to All Team Members:
                    Print the Excel file content and manually check the section and training time for each team member based on their respective rows. Do not use code to extract the information programmatically.
                    Send emails to all team members (including Alice), informing them about their training section and time:
                        In the email content, you must clearly state the activity (i.e., team training), in which section (e.g., section A), and the time (e.g., 11:00 AM - 1:00 PM).
                        For example: `send_email('Assistant@example.com', 'Bob@example.com', 'Team Training', 'You are invited to the team training at 11:00 AM - 1:00 PM in the section B.')`
                    Note: Alice should also receive an email about the training.""",
        ],
        "1":[
            hint_new_file_path,
             """To solve this task, follow these steps: 
             1. Creating a New Event for Alice:
                    Print the Excel file content and manually check Alice's section and training time based on her row;
                    Create a new event 'team training' in Alice's calendar. When setting the date, assuming today is 2020-05-01 as stated in the task, so the date of next week is 2020-05-08. Do not use `datetime.now()` to determine the date.
             2. Sending Emails to Team Members in Section A:
                    Print the Excel file content and manually check which students belong to Section A and their training times. Do not use code to extract the information programmatically.
                    Send emails to team members of Section A, informing them about their training section and time:
                        In the email content, you must clearly state the activity (i.e., team training), in which section (e.g., section A), and the time (e.g., 11:00 AM - 1:00 PM).
                        For example: `send_email('Assistant@example.com', 'David@example.com', 'Team Training', 'You are invited to the team training at 11:00 AM - 1:00 PM in the section A.')`
                    Note: If Alice is in Section A, you also need to send an email to her."""
        ]

    },
    "3-8": {
        "0":[
            """Print the Excel file content and manually check which years have revenues of $2000000 or more. Do not filter the data programmatically. Create a new Excel file and write the information for these years into it.""",
            hint_excel_write_to_file,
            hint_word_write_to_file,
            hint_excel_verify_bf_completing,
        ],
        "1":[
            """Print the Excel file content and manually read each row to identify the years where revenue is greater than 4000000. Do not parse the data programmatically. Visually check the numbers and make your judgment like a person would. Once you've identified the correct years, create a new Excel file and write these the years into it. Do not write your reasoning into the excel table, only the years with revenues higher than 4000000.""",
            # """Hint: You can create two lists, one for the years and one for the revenues. Find the revenues higher than 4000000$ and their corresponding years.""",
            hint_excel_write_to_file,
            hint_word_write_to_file,
            """In the report, you should include the keyword "revenues" as well as the correct years you identified in the content.""",
            hint_excel_verify_bf_completing
        ],
        "2":[
            """Print the Excel file content and manually read each row to identify which two years have the highest revenue. Do not parse the data programmatically. Visually check the numbers and make your judgment like a person would. Once you've identified the correct years, create a new Excel file and write these the years into it.""",
            # """Hint: You can create two lists, one for the years and one for the revenues. Find the top 2 revenues and their corresponding years.""",
            hint_excel_write_to_file,
            hint_word_write_to_file,
            """In the report, you should include the keyword "revenues" as well as the correct years you identified in the content.""",
            hint_excel_verify_bf_completing
        ],
         "4":[
            """Print the Excel file content and manually read each row to get the revenue value of the year 2019 and the year 2020 for calculation. Do not parse the data programmatically. Visually check the numbers and find out the value you nedd like a person would.""",
            hint_word_write_to_file,

        ],

        "6":[
            """Print the Excel file content and carefully read each student's scores for midterm1 and midterm2. For each student, manually check if their midterm2 score is higher than their midterm1 score:
                - If midterm2 score is higher, the student made progress.
                - If midterm2 score is lower or the same, the student did not make progress.
            Do not write code to compare the numbers. Look at them yourself and make a decision like a human would.
            Example:
            Tom: 93 -> 79 (lower; not made progress)
            Noah: 65 -> 66 (higher; made progress)""",
        ],
        "7":[
            hint_new_file_path,
            """Print the Excel file content and carefully read each student's scores for midterm1 and midterm2. For each student, manually check if their midterm2 score is higher than their midterm1 score:
                - If midterm2 score is higher, the student made progress.
                - If midterm2 score is lower or the same, the student did not make progress.
            Do not write code to compare the numbers. Look at them yourself and make a decision like a human would.
            Example:
            Tom: 93 -> 79 (lower; not made progress)
            Noah: 65 -> 66 (higher; made progress)
            The answer is the number of students who made progress.""",
            """To record the answer, you should first create a new Word file using `word_create_new_file()`. Then, write the answer in this file using `word_write_to_file()`.""",
        ],
      
    },

    "3-9": {
        "0": [
            """To obtain an image, you can first convert the excel file to pdf using `excel_convert_to_pdf()`, and then convert the pdf to image using `pdf_convert_to_image()`.""",
        ],
        "1": [
            """Print the Excel file content and manually check how many years of revenues are higher than 4000000$. Do not perform it programmatically.""",
            """To obtain an image, you can first convert the excel file to pdf using `excel_convert_to_pdf()`, and then convert the pdf to image using `pdf_convert_to_image()`."""
        ],

    },

    "3-10":{
        "0":[
            hint_new_file_path,
            """Note that this tasks requires you to create folders for each recipients, but not for each sender.""",

        ]
    },

    "3-12":{
        "0":[
            """Create a new Word file. Write the extracted text into the Word file. Then, convert the Word file to PDF using `word_convert_to_pdf()`.""",
            """Call `send_email()` twice to send eamil to Bob and Tom one by one. """
        ],
        "1":[
            """Create a new Word file. Write the meeting notification information into the word file. Then, convert the Word file to PDF using `word_convert_to_pdf()`.""",
        ]
    },

    "3-13": {
        "1": [
            hint_one_action_per_step,
            """The folder contains multiple images. As a first step, use os.listdir(data_path) to list all files in the folder and identify the correct image file to work on.""",
            """After extracting the text from the image using OCR, print it to manually check the content. Manually split the content into the part regarding the party and the part regarding the meeting based on your reasoning like human would do. Do not use code to split the content programmatically.""",
            """In party.pdf file, mention the keyword 'party' in the content. In the meeting.pdf file, mention the keyword 'meeting' in the content."""
        ],
    },
    
    "3-14": {
        "0": [
            hint_one_action_per_step,
            """The folder contains multiple images. As a first step, use os.listdir(data_path) to list all files in the folder and identify the correct image file to work on.""",
            """To obtain meeting.pdf, first create a new Word file. Write the summary into this Word file, then convert it to PDF.""",
        ],
        "1": [
            hint_one_action_per_step,
            """The folder contains multiple images. As a first step, use os.listdir(data_path) to list all files in the folder and identify the correct image file to work on.""",
            """To obtain PDF files, first create a new Word file. Write the content into this Word file, then convert it to PDF.""",
            """Note that Alice holds the meeting, and Bob holds the party."""
        ],
    },

    "3-15":{
        "0":[
            """To solve this task, you should:
            1. Use `pdf_read_file()` to read the file content and print it.
            2. Manually check the content to find the name and contact information.
            3. Create a new Word file by `word_create_new_file()`.
            4. Write the name and contact information into the new Word file using `word_write_to_file()`.
            5. Convert the new Word file to PDF using `word_convert_to_pdf()`.
            6. Convert this PDF file to image using `pdf_convert_to_image()`.
            7. Send email containing the extracted information to Bob.""",
        ]
    },
    
    "3-17":{
        "0":[
            """To solve this task, you should:
            1. Use `pdf_read_file()` to read the file content and print it.
            2. Manually check the content to find the key information.
            3. Create a new Word file by `word_create_new_file()`.
            4. Write the welcome information into the new Word file using `word_write_to_file()`.
            5. Convert the new Word file to PDF using `word_convert_to_pdf()`.
            6. Convert this PDF file to image using `pdf_convert_to_image()`.
            7. Send an email to the corresponding person including a welcome information.""",
        ]
    },

    "3-18":{
        "0":[
            """To solve this task, you should:
            1. Use `pdf_read_file()` to read the file content and print it.
            2. Manually check the content to find the name and contact information.
            3. Create a new Word file by `word_create_new_file()`.
            4. Write the name and contact information into the new Word file using `word_write_to_file()`.
            5. Convert the new Word file to PDF using `word_convert_to_pdf()`.
            6. Convert this PDF file to image using `pdf_convert_to_image()`.
            7. Create a new excel file and write the name and contact information into it.""",
        ]
    },
    "3-19":{
        "0":[
            """Strictly follow the solution steps:
            1. As a first step, use os.listdir(data_path) to list all files in the folder;
            2. Important: Use OCR to extract text from the school_policy.jpg to learn about the school policy;
            3. Use `pdf_read_file()` to view the content of the application;
            4 Manually verify whether the application complies each point of the policy by your reasoning. Do not analyze the application programmatically.
            The policy requires the student to provide at least two references. If the applicant only provide one referee in the "References:" section, then the application does not comply with the policy.
            For example:
                References:
                Dr. John Smith, Professor, University X
            Here the applicant only provide one referee John Smith, **so your answer is 'no'**;
            Write "no" into a new word file.
            5. Send the application content by email to the officer."""
        ]

    },

    "3-20":{
        "0":[
            """Strictly follow the solution steps:
            1. As a first step, use os.listdir(data_path) to list all files in the folder;
            2. Important: Use OCR to extract text from the school_policy.jpg to learn about the school policy;
            3. Use `word_read_file()` to view the content of the application;
            4 Manually verify whether the application complies each point of the policy by your reasoning. Do not analyze the application programmatically.
            If the applicant only provide one referee in the "References:" section, then the application does not comply with the policy.
            For example:
                References:
                Dr. John Smith, Professor, University X
            Here the applicant only provide one referee John Smith, so your answer is 'no';
            5. In the calendar, create a new event 'a meeting with officer'."""

        ]
    },

    "3-21":{
        "0":[
            """Strictly follow the solution steps:
            1. As a first step, use os.listdir(data_path) to list all files in the folder;
            2. Important: Use OCR to extract text from the school_policy.jpg to learn about the school policy;
            3. Use `pdf_read_file()` to view the content of the application;
            4 Manually verify whether the application complies each point of the policy by your reasoning. Do not analyze the application programmatically.
            If the applicant only provide one referee in the "References:" section, then the application does not comply with the policy.
            For example:
                References:
                Dr. John Smith, Professor, University X
            Here the applicant only provide one referee John Smith, so your answer is 'no'.""",
            """Create a new folder: `os.mkdir(os.path.join(data_path, 'application'))` before saving any files in it.""",

        ]
    },
    "3-24":{
        "0":[
            """Manually summarize key points of the paper based on its abstract. Print it to check the content before writing it into a word file.""",
            """When creating a new event in the calendar, the event summary must include all important information. For this task, it should include 'meeting', 'professor Dan' and 'paper'.""",
        ]
    },
    
    "3-26":{
        "0":[
            """Manually summarize key points of the paper based on its abstract. Print it to check the content before writing it into a word file.""",
            """You should also write the summary in the email body.""",
        ]
    },

    "3-27":{
        "0":[
            ocr_results_mistakes,
             """Remember to send the email to Alice. Include Bob's contact information in the email. The output .eml file will automatically be named after the subject of the email. Therefore, for this task, when sending the email, the subject should be "Bob" to make the file named 'Bob.eml'."""
        ]

    },

    "3-28":{
        "0":[
            """When calling create_event() to add a new event to the calendar, the first argument must be the name of the user for whom the event is created. For this task, Bob is the user. Do not create an event for Alice.""",
            """The event summary must include all important information.""",
        ]
    },

    "3-29":{
        "0":[
            ocr_results_mistakes,
            """Ensure that contact information is saved in alphabetical order by first name. For example, if the contacts are Bob and John, Bob's row should come before John's.""",
            """Important: Write only the first name into the column "Name". Do not write the last name, e.g., it should be 'John' instead of 'John Doe'.""",
            """The output .eml file will automatically be named after the subject of the email. Therefore, for this task, when sending the email, the subject should be "contact" to make the file named 'contact.eml'."""
            """You should send the email to Tom. The Tom's email address can be found in his contact card. In the email to Tom, remember to include the contact information of Bob and John, including their email address, phone number, and address."""
        ]
    },

    "3-30":{
        "0":[
            ocr_results_mistakes,
            """'Rob' shoule be 'Bob'. """
            """Ensure that contact information is saved in alphabetical order by first name: Bob's row should come first, then the next row is John's, then the last row should be Tom's.""",
            """Important: Write only the first name into the column "Name". Do not write the full name, e.g., it should be 'John' instead of 'John Doe'.""",
            ]
    },

    "3-33":{
        "0":[
            """Solution step:
            1. Read the pdf file, then print the content.
            2. Create an Excel file. 
            3. Manually extract information from the PDF file content and write it into this excel file using `excel_set_cell()`.
            4. Create a new event in the calendar.""",
        ]
    },

    "3-35":{
        "0":[
            hint_ls_data_path,
            """For this task, you should: 1. Use `ocr_recognize_text()` to extract text from the image file and print the content; 2. Manually check who gets the highest score; 3. Send an email to the student with the highest socre; the email subject should be "reward"; menthion the reward in the email main text.""",
            ocr_results_mistakes,
        ]
    },
   "3-36":{
        "0":[
            hint_ls_data_path,
            """For this task, you should: 
            1. Use `ocr_recognize_text()` to extract text from the image file and print the content; 
            2. Create a new Excel; 
            3. Important: Use `excel_set_cell()` to write the information into the new Excel file manually;
            3. create a new event in the calendar with the requried time.""",
            ocr_results_mistakes,
            """Note that the maximum scores is 400. Correct the OCR mistakes and write the correct scores into the excel file.""",
        ]
    },
    "3-39":{
        "0":[
            hint_ls_data_path,
            """Student IDs start with 's1' or 's2'."""
            """For this task, you should: 1. Use `ocr_recognize_text()` to extract text from the image file and print the content; 2.View the output; Manually split the students into 2 groups based on their IDs: starting with 's1' or 's2'. 3. Manually save each group (including student names) into separate Excel files.""",
            ocr_results_mistakes,
            """Before creating new Excel files, the folder `Class1` and `Class2` should already exist. These folders should be located inside the task files folder specified by `data_path`, e.g., `os.mkdir(os.path.join(data_path, 'Class1'))`."""
        ]
    },
    "3-40":{
        "0":[
            ocr_results_mistakes,
            """
            - View the extracted text from the image carefully;
            - Use `excel_create_new_file()` to create a new Excel file ;
            - Important: Manually write car trading information into an excel file using `excel_set_cell()`. Include headers and cell values.""",
            """Create new calendar events for both the seller and the buyer of the first record: `create_event(first_buyer_name,...)` and `create_event(first_seller_name,...)`""",
        ]
    },

    "3-41":{
        "0": [
            """When writing the company trading information from the text, do not parse the text programmatically. Instead, manually check the content and write the information into the Excel file using `excel_set_cell()`.""",

        ]
    },

    "3-42":{
        "0":[
            """To perform file operations, import `os` in your first step.""",
            hint_ls_data_path,

            """
            Follow these steps to complete the task:
            1. Use `ocr_recognize_text()` to extract text from the image file and print the content.
            2. Manually check the content to find the required information by your reasoning.
            3. Create a new Excel file using `excel_create_new_file()`.
            4. Write the required information into the new Excel file using `excel_set_cell()` manually.
            6. Send an email to the president to inform him about the trading information. Your email should include the keyword "company trading". The sender is Bob, and the recipient is the president.""",

            ocr_results_mistakes,
            hint_excel_verify_bf_completing,
        ]
    },

    "3-43":{
        "0":[
            """Use pdf_read_file to extract the text from a PDF file. Use create_event() to create a new calendar event.""",
            """Remember to write the content of the PDF file into .txt file. For example:
            ```
            with open(os.path.join(data_path, 'meeting.txt'), 'w') as file:
                file.write(text)
            ```""",
        ]
    },

    "3-45":{
        "0":[
            """Solution steps:
            1. Use `excel_read_file()` to read the file content and print it.
            2. Manually identify and extract the names from the file.
            3. Create a new event in the calendar for each person manually.
            """,
        ]
    },
    
    "3-46":{
        "0":[
            hint_excel_get_values,
            """Manually review the Excel file to identify the top three students in Midterm 2. Do not use a programmatic approach. Create calendar events and send emails for each student individually. In both the emails and calendar events, mention their scores and the reward.""",
            """Do not create a calendar event for Bob. Create calendar events for top-3 students only. For example, if Carol is one of the top-3 students, use `create_event('Carol',...)` to create a calendar event for Carol.""",
        ]
    },
    "3-49":{
        "0":[
            """Do not create a calendar event for Bob. Create calendar events for each student in section C only. For example, if Carol is in section C, use `create_event('Carol',...)` to create a calendar event for Carol. You should mention "helping section" in the event summary.""",
        ]
    },
    "3-47":{
        "0":[
            hint_excel_get_values,
            """Manually review the Excel file to extract information of the top three students in Midterm 2. Do not use a programmatic approach. Create a new Word file and write the top three students names and reward statement into it. Then, convert the Word file to PDF.""",
        ]
    },
    "3-50":{
        "0":[
            """When writing meeting agenda information into the Excel file, do not parse the text programmatically. Instead, manually check the content and write the information into the Excel file using `excel_set_cell()`.""",
            """Convert the excel file to PDF using `excel_convert_to_pdf()` and then convert the PDF file to image using `pdf_convert_to_image()`.""",
        ]
    },

    "3-51":{
        "0":[
            """For file operations, import `os` in your first step.""",
            """Follow the solution steps:
            1. List the calendar events: `list_events('meeting_agenda')`.
            2. Review the event content. Do not parse it manually. Understand the required information using reasoning.
            3. Create a new Excel file using `excel_create_new_file()`.
            4. Write the required information (event names and time) into the new Excel file using `excel_set_cell()`. 
            5. Send an email. In the email, you should provide **detailed information** on all events, e.g., "There will be an Introductions by Linda,  Strategy by Charlie and Agenda by Davide in the meeting.".""",
            """When using `send_email`, remember that you can only input 4 arguments: for example, `send_email('Bob@example.com', 'Rena@example.com', 'Note', 'info)`"""
        ]
    },

    "3-52":{
        "0":[
            """In the calendar, each item (e.g., Introductions, Agenda, Strategy) should be a separate event. In event summary, provide detailed information about the event. Do not use `datetime` to set the date. Instead, use the date mentioned in the task description (e.g., 2020-05-01).""",
            """In each participants' email, you should provide detailed information about their respective events. For example, in the email to Linda, you should mention her event name 'Introductions'."""
        ]
    },

    "3-53":{
        "0":[
            hint_ls_data_path,
            """Use `excel_read_file()` to display the content of the correct excel file to review. Do not assume the class member information by yourself. Instead, manually review the Excel file to identify which students are in class 1/2/3. Do not parse the excel file programmatically.""",
            """The new folders should be created under the task files folder specified by `data_path`.""",
            """For example, if Noah is in class 1, then there should be a text file named 'Noah.txt' in the folder for class 1."""
        ]
    },

    "3-55":{
        "0":[
            hint_ls_data_path,
            """To complete this task, you should: 
            1. Important: Always use `excel_read_file()` to read the excel file content.
            Manually review the Excel file containing scores to identify the student with the highest Midterm 1 score. Do not parse the excel file programmatically.
            2. Once you have reviewed the file using excel_read_file(), create a new Word document and write a congratulatory statement for that student. 
            3. Convert the Word document to a PDF, then convert the PDF into an image."""
        ]
    },

    "3-58":{
        "0":[
            """Review the Excel file to identify each item and manually write them into a doc. Do not programmatically extract the information.""",    
        ]
    },

    "3-60":{
        "0":[
            hint_extract_info_from_text,
            """Before creating the Word file, first create a new folder `os.mkdir(os.path.join(data_path, 'CS161'))`."""

        ]
    },

    "3-61":{
        "0":[
            """When calling send_email(), the generated email file will have the same name as the subject. Therefore, set the subject argument to 'thomas' for this task.""",
            """In the email, mention the situation and include a reference to the file `classes.docx.`"""
        ]
    },
    "3-62":{
        "0":[
            """Do not directly copy the raw output from `excel_read_file()` (which includes cell coordinates like (1,1), (1,2), etc.) into the Word file. Instead, visually inspect the table and manually extract the real content: the headers (Name, midterm1, midterm2) and each student's actual data (e.g., Liam, 74, 72). Write only the clean table content (without any (row, column) coordinates) into the Word document. After the Word file looks correct, then convert it to a pdf file.""",
            # """Important: Do not include index values (e.g., (1,1), (2,1), etc.) in the Word file. Only write the cell contents.""",
        ]
    },

    "3-64":{
        "0":[
            hint_ls_data_path,
            """Information about house price index are stored in an excel file.""",
        ]
    },

    "3-65":{
        "0":[
            hint_ls_data_path,
            """Information about house price index are stored in an excel file.""",
        ]
    },

    "3-67":{
        "0":[
            hint_ls_data_path,
        ]
    },
    
    "3-68":{
        "0":[
            hint_ls_data_path,
            """Use `excel_create_new_file()` to create a new Excel before writing the information into it.""",
        ]
    },

    "3-73":{
        "0":[
            """To make an invitation post image, you should create a Word file and write the invitation information into it. Then, convert the Word file to PDF using `word_convert_to_pdf()`. Finally, convert the PDF file to image using `pdf_convert_to_image()`."""
        ]
    },

    "3-74":{
        "0":[
            hint_ls_data_path,
            hint_extract_info_from_text,
            """The created Excel file must include a header row at the top with the following column names: date, location, and conference fame."""
        ]
    },

    "3-75":{
        "0":[
            """In the email, specify the student's name so the teacher knows whose homework it is."""
        ]
    },

    "3-76":{
        "0":[
            """Remeber to only find the maximum prices of the cars sold in **March**. Do not find the maximum prices of cars sold in other months."""
        ]
    },

    "3-78":{
        "0":[
            """The reimbursement amount is calculated as: (number of employees * salary for each employee + Machine Purchase Reimbursement). Compare the reimbursement amount with 'Budget for the Year' to determine if the reimbursement exceeds the budget. If yes, you should report "The reimbursement amount exceeds the company budget." to the manager in the email."""
        ]
    },

    "3-79":{
        "0":[
            """Write a detailed event summary including what the event is about, the main topic of discussiont and who participates.""",
        ]
    },

    "3-80":{
        "0":[
            """Remember to create a folder:`os.makedirs(os.path.join(data_path, 'trading_account'))`.""",
            """Create a Word file and write the analysis into it. Convert the Word file to PDF using `word_convert_to_pdf()`. Then, convert the PDF file to image using `pdf_convert_to_image()`.""",
        ]
    },
    "3-81":{
        "0":[
            hint_excel_get_values,
            """Create a new Excel file 'Class_member.xlsx' and write the student names into it. Then convert the Excel file to PDF using `excel_convert_to_pdf()`.""",
        ]
    },

    "3-82":{
        "0":[
            """Do not parse the excel file programmatically.""",
            hint_excel_get_values,
        ]

    },

    "3-83":{
        "0":[
           
            """Do not parse the excel file programmatically. Instead, review the Excel file to find which class has the fewest students by using reasoning. If a class only has 1 student, then this class is the one with the fewest students.""",
        ]
    },

    "3-84":{
        "0":[
            """You must generate a report named report.docx"""
        ]
    },

    "3-85":{
        "0":[
            hint_ls_data_path,
            """To get an image as the report, you should create a Word file and write the report into it. Then, convert the Word file to PDF using `word_convert_to_pdf()`. Finally, convert the PDF file to image using `pdf_convert_to_image()`. If you don't find any relationships between sleeping hours and other variables, you can write 'no relationship' in the report.""",
            hint_new_file_path,
        ]
    },

    "3-87":{
        "0": [
                        """Example Solution:
                1. Use `os.listdir(data_path)` to view the files in the task files folder.
                2. use `ocr_recognize_text()` to read the transcript.
                3. Manually review and list the number of term-specific GPAs higher than 3.9. Do not count the Cumulative GPAs.
                For example, for this transcript:
                    Student: Teddy Roosevelt Date of Birth: Oct 27, 1910 Weighted GPA: =. 3..78/4.00
                    Street Address: 1900 Pennsytvania Ave Place of Birth: Manhattan, NY Unweighted GPA: 3.65/4.00
                    City/State/Zip: Washington, DC 20500 Gender: Male
                    Phone: (202) 456-1111 Credits Earned: 23.00
                    Fall Winter
                    Course Grade Credits Course Grade Credits
                    Physical Science A 1.00 Tennis A 1.00
                    U.S. History A 1.00 GPA 4.00 1.00
                    GPA 4.00 2.00 Cumulative GPA 4.00 3.00
                    Cumulative GPA 4.00 2.00
                    Spring Summer
                    Course Grade Credits Course Grade Credits
                    English Composition A 1.00 Algebra! A 1.00
                    Music Appreciation B 1.00 GPA 4.00 1.00
                    GPA 3.50 2.00 Cumulative GPA 3.83 6.00
                    Cumulative GPA 3.80 5.00

                    The term GPAs are 4.00, 4.00, 4.00, 3.50. Do not count the number following 'Cumulative GPA'. The answer is 3.

                4. Create a Python list out of the qualifying terms and use the `len()` function to count the length of the list.
                5. Email the answer to Teddy@example.com"""
        ]

    },

    "3-90":{
        "0":[
        
        """You can find the frequency information in the calendar. Use the exact words from the calendar to write the frequency information, e.g., "weekly", "monthly", "yearly" or "daily".""",
        """Write the answer into a new word file, then covert the word file to PDF."""
        ]
    },

    "3-92":{
        "0":[
            """Strictly follow these steps to complete the task:
            1. IMPORTANT: In your first step, import `os` and use `os.listdir(data_path)` to list all files in the folder!
            2. IMPORTANT:Use `pdf_read_file()` to read the file content and print it!
            3. Review the file content to learn about the party information;
            4. Send an email to Bob to invite him to the party;
            5. Write a welcome post in a Word file and convert it to PDF using `word_convert_to_pdf()`.
            6. Convert the PDF file to image as welcome.jpg using `pdf_convert_to_image()`."""

        ]
    },
    "3-93":{
        "0":[
            """Do not parse the calendar content programmatically. Instead, visually inspect the calendar to find the event information. Send them to Bob by the email. Write the event information into a new Word file using `word_write_to_file()`. Then, convert the Word file to PDF event.pdf using `word_convert_to_pdf()`.""",
        ]

    },

    "3-94":{
        "0":[
            """Inspect the calendar content to find the name of common events. Send common events names to Bob and Tom by email. Write the common events names into a new word file, then convert it to PDF, finally convert the PDF file to image as common_events.jpg using `pdf_convert_to_image()`.""",
        ]

    },

    "3-96":{
        "0":[
            hint_ls_data_path,
            """When calling send_email(), the generated email file will have the same name as the subject. Therefore, set the subject argument to 'revenues' for this task.""",

        ]
    },

    "3-97":{
        "0":[
            """For file operations, import `os` in your first step.""",
            """Do not perform `list_events("Bob")` and `list_events("Tom")` in the same step: The output of `list_events("Bob")` will be overwritten by `list_events("Tom")` if you perform them in the same step. Instead, you should perform them in two separate steps.""",
            """Manually review their calendar events and count their sleeping time and class time by your reasoning like a human would. Do not parse the events programmatically.""",
            hint_new_file_path,
            """Write the summary in an excel file `daily_events.xlsx`. Then convert it to PDF using `excel_convert_to_pdf()`.""",
            """In the Excel file, clearly indicate both the people's name, event name and event duration: there can be three columns: 'Name', 'Class Time' and 'Sleeping Time'. Record class time in the 'Class Time' column and sleeping time in the 'Sleeping Time' column.""",
        ]
    },

    "3-99":{
        "0":[
            hint_ls_data_path,
            hint_new_file_path,
            """Do not forget to write something in the document."""
        ]
    },

}