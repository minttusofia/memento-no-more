import os
from icalendar import Calendar, Event
from datetime import datetime
from agent import agent as ag

from tasks.t_OfficeBench.OfficeBench.apps.calendar_app import calendar_delete_event, calendar_list_events
from tasks.t_OfficeBench.OfficeBench.apps.email_app import email_list_emails, email_read_email, email_send_email
from tasks.t_OfficeBench.OfficeBench.apps import excel_app
from tasks.t_OfficeBench.OfficeBench.apps import ocr_app
from tasks.t_OfficeBench.OfficeBench.apps import pdf_app
from tasks.t_OfficeBench.OfficeBench.apps import word_app


# tools for Calendar App
def create_event(agent: ag.Agent, user, summary, time_start, time_end):
    """create_event(user: str, summary: str, time_start: str, time_end: str)
    Create a new event to a user's calendar where the time format is '%Y-%m-%d %H:%M:%S'.
    - Input:
        1. user: the user name
        2. summary: the event summary exactly as mentioned in the task. You may include key details, but ensure it matches the original wording.
        3. time_start: event start time
        4. time_end: event end time
    - Output: True if the event is created successfully, False otherwise.
    Example call: `create_event('Tom', 'meeting with the staff in Room 12 to discuss the project', '2024-05-17 10:00:00', '2024-05-17 11:00:00')`: Returns True
    """
    
    agent.stats.add_tool_call("create_event")

    testbed_path = os.path.join(agent.run_path, 'testbed')
    path = testbed_path + '/calendar'
    os.makedirs(path, exist_ok=True)
    try:
        calendar_file = path+'/{}.ics'.format(user)
        if not os.path.exists(calendar_file):
            calendar = Calendar()
            calendar.add('prodid', '-//My Calendar Product//mxm.dk//')
            calendar.add('version', '2.0')
        else:
            calendar = Calendar.from_ical(open(calendar_file, 'rb').read())

        event = Event()
        event.add('summary', summary)
        event.add('dtstart', datetime.strptime(time_start, '%Y-%m-%d %H:%M:%S'))
        event.add('dtend', datetime.strptime(time_end, '%Y-%m-%d %H:%M:%S'))
        event.add('dtstamp', datetime.now())
        event.add('description', 'This is a test event')
        event.add('location', 'Online')

        calendar.add_component(event)

        with open(calendar_file, 'wb') as f:
            f.write(calendar.to_ical())
        print(f"Successfully create a new event to {user}'s calendar.")
        return True
    except Exception as e:
        print('!!!', e)
        print(f"Failed to create a new event to {user}'s calendar.")
        return False


def delete_event(agent: ag.Agent, user, summary):
    """delete_event(user, summary)
    Delete an event from a user's calendar given the event summary.
    - Input:
        1. user: the user name
        2. summary: the event summary
    - Output: True if the event is deleted successfully, False otherwise.
    Example call: `delete_event('Sarah', 'lunch')`: Returns True
    """
    agent.stats.add_tool_call("delete_event")
    testbed_path = os.path.join(agent.run_path, 'testbed')
    return calendar_delete_event.delete_event(user, summary, testbed_path)


def list_events(agent: ag.Agent, username):
    """list_events(username)
    List all events from a user's calendar.
    - Input: username: the user name
    - Output: a string containing information for all events.
    Example call:
        `list_events('Mike')`: Returns "Summary: Meeting\nStart Time: 2024-05-13 09:00:00\nEnd Time: 2024-05-13 10:00:00\nDescription: Team meeting\nLocation: Office
    """
    agent.stats.add_tool_call("list_events")
    testbed_path = os.path.join(agent.run_path, 'testbed')
    return calendar_list_events.list_events(username, testbed_path)


# tools for Email App
def list_emails(agent: ag.Agent, username):
    """list_emails(username)
    List all emails in a user's inbox.
    - Input: username: the user name
    - Output: a string containing information for all emails.
    Example call:
        `list_emails('Sam')`: Returns "Email ID: meeting.eml\nFrom: Alice@emaildomain.com\nTo: Sam@example.com\nSubject: Meeting\nContent: Team meeting at 3pm...
    """
    agent.stats.add_tool_call("list_emails")
    testbed_path = os.path.join(agent.run_path, 'testbed')
    return email_list_emails.list_emails(username, testbed_path)


def read_email(agent: ag.Agent, username, email_id):
    """read_email(username, email_id)
    Read a user's email by the given Email ID.
    - Input:
        1. username: the user name
        2. email_id: the email's unique ID
    - Output: a string containing the email information.
    Example call:
        `read_email('Anna', 'reminder.eml')` Returns "From: Sam@example.com\nTo: Anna123@hotmail.com\nSubject: Reminder\nContent: Remember the due date tomorrow...\n"
    """
    agent.stats.add_tool_call("read_email")
    testbed_path = os.path.join(agent.run_path, 'testbed')
    return email_read_email.read_email(username, email_id, testbed_path)


def send_email(agent: ag.Agent, sender, recipient, subject, content):
    """send_email(sender, recipient, subject, content)
    Send an email from the sender to the recipient. The email's file name is {subject}.eml.
    - Input:
        1. sender: the sender's email address
        2. recipient: the recipient's email address
        3. subject: the email subject. The email's file name is the same as the subject.
        4. content: the email content
    - Output: "Successfully sent email to {recipient}." if the email is sent successfully, an error message otherwise.
    - Example call:
        `send_email('Alice@example.com', 'Bob@domain.com', 'Meeting', 'Hello, Bob!')`: Returns 'Successfully sent email to Bob.'
    """
    agent.stats.add_tool_call("send_email")
    testbed_path = os.path.join(agent.run_path, 'testbed')
    return email_send_email.send_email(sender, recipient, subject, content, testbed_path)


# tools for Excel App
def excel_convert_to_pdf(agent: ag.Agent, excel_file_path, pdf_file_path):
    """excel_convert_to_pdf(excel_file_path, pdf_file_path)
    Convert an Excel file to a PDF file.
    - Input:
        1. excel_file_path: the path to the Excel file
        2. pdf_file_path: the path to the PDF file
    - Output: True if the conversion is successful, False otherwise.
    Example call: `excel_convert_to_pdf(os.path.join(data_path, 'test.xlsx'), os.path.join(data_path, 'test.pdf'))`: Returns True
    """
    agent.stats.add_tool_call("excel_convert_to_pdf")
    if not os.path.exists(excel_file_path):
        return f"The excel file path: {excel_file_path} is not correct"
    return excel_app.excel_convert_to_pdf.excel_convert_to_pdf(excel_file_path, pdf_file_path)


def excel_create_new_file(agent: ag.Agent, file_path):
    """excel_create_new_file(file_path)
    Create a new Excel file.
    - Input: file_path: the path to the new Excel file
    - Output: True if the file is created successfully, False otherwise.
    Example call: `excel_create_new_file(os.path.join(data_path, 'test.xlsx'))`: Returns True
    """
    agent.stats.add_tool_call("excel_create_new_file")
    return excel_app.excel_create_new_file.excel_create_new_file(file_path)


def excel_delete_cell(agent: ag.Agent, file_path, row_idx, column_idx, sheet_name=None):
    """excel_delete_cell(file_path, row_idx, column_idx, sheet_name=None)
    Delete the content of a cell in an Excel file.
    - Input:
        1. file_path: the path to the Excel file
        2. row_idx: the row index of the cell
        3. column_idx: the column index of the cell
        4. sheet_name: the name of the sheet (optional). If not provided, the active sheet will be used.
    - Output: True if the cell content is deleted successfully, False otherwise.
    Example call: `excel_delete_cell(os.path.join(data_path, 'test.xlsx'), 2, 1)`: Returns True
    """
    agent.stats.add_tool_call("excel_delete_cell")
    if not os.path.exists(file_path):
        return f"The excel file path: {file_path} is not correct"
    return excel_app.excel_delete_cell.excel_set_cell(file_path, '', row_idx, column_idx, sheet_name)


def excel_read_file(agent: ag.Agent, file_path, sheet_name=None):
    """excel_read_file(file_path, sheet_name=None)
    Read the content of an Excel file.
    - Input:
        1. file_path: the path to the Excel file
        2. sheet_name: the name of the sheet (optional). If not provided, the active sheet will be used.
    - Output: a string containing the spreadsheet entries in "({row_idx}, {col_idx}): {value}" format.
    Example call:
        `excel_read_file(os.path.join(data_path, 'test.xlsx'))`: Returns "(1, 1): Order 1\t(1, 2): 123\n(2, 1): Order 2\t(2, 2): 456\n"
    """
    agent.stats.add_tool_call("excel_read_file")
    if not os.path.exists(file_path):
        return f"The excel file path: {file_path} is not correct"
    return excel_app.excel_read_file.excel_read_file(file_path, sheet_name)


def excel_set_cell(agent: ag.Agent, file_path, text, row_idx, column_idx, sheet_name=None):
    """excel_set_cell(file_path, text, row_idx, column_idx, sheet_name=None)
    Write text to a cell in an Excel file.
    - Input:
        1. file_path: the path to the Excel file
        2. text: the text to write, which must be a string.
        3. row_idx: the row index of the cell
        4. column_idx: the column index of the cell
        5. sheet_name: the name of the sheet (optional). If not provided, the active sheet will be used.
    - Output: True if the text is written to the cell successfully, False otherwise.
    Example call: `excel_set_cell(os.path.join(data_path, 'test.xlsx'), 'Hello, World!', 1, 1)`: Returns True
    """
    agent.stats.add_tool_call("excel_set_cell")
    if not os.path.exists(file_path):
        return f"The excel file path: {file_path} is not correct"
    return excel_app.excel_set_cell.excel_set_cell(file_path, text, row_idx, column_idx, sheet_name)


# tools for OCR App
def ocr_recognize_text(agent: ag.Agent, file_path):
    """ocr_recognize_text(image_path)
    Recognize text from an image using Optical Character Recognition (OCR).
    - Input: file_path: the path to the image file
    - Output: the recognized text from the image.
    Example call: `ocr_recognize_text(os.path.join(data_path, 'image.jpg'))`: Returns "ABC DEF"
    """
    agent.stats.add_tool_call("ocr_recognize_text")
    if not os.path.exists(file_path):
        return f"The image file path: {file_path} is not correct"
    return ocr_app.ocr_recognize_file.ocr_recognize_file(file_path)


# tools for PDF App
def image_convert_to_pdf(agent: ag.Agent, image_file_path, pdf_file_path):
    """image_convert_to_pdf(image_file_path, pdf_file_path)
    Convert an image file to a PDF file.
    - Input:
        1. image_file_path: the path to the image file
        2. pdf_file_path: the path to the PDF file
    - Output: True if the conversion is successful, False otherwise.
    Example call: `image_convert_to_pdf(os.path.join(data_path, 'image.jpg'), os.path.join(data_path, 'test.pdf'))`: Returns True
    """
    agent.stats.add_tool_call("image_convert_to_pdf")
    if not os.path.exists(image_file_path):
        return f"The image file path: {image_file_path} is not correct"
    return pdf_app.image_convert_to_pdf.image_convert_to_pdf(image_file_path, pdf_file_path)

def pdf_convert_to_image(agent: ag.Agent, pdf_file_path, image_file_path):
    """pdf_convert_to_image(pdf_file_path, image_file_path)
    Convert a PDF file to an image file.
    - Input:
        1. pdf_file_path: the path to the PDF file
        2. image_file_path: the path to the image file
    - Output: True if the conversion is successful, False otherwise.
    Example call: `pdf_convert_to_image(os.path.join(data_path, 'test.pdf'), os.path.join(data_path, 'image.jpg'))`: Returns True
    """
    agent.stats.add_tool_call("pdf_convert_to_image")
    if not os.path.exists(pdf_file_path):
        return f"The pdf file path: {pdf_file_path} is not correct"
    return pdf_app.pdf_convert_to_image.pdf_convert_to_image(pdf_file_path, image_file_path)

def pdf_convert_to_word(agent: ag.Agent, pdf_file_path, word_file_path):
    """pdf_convert_to_word(pdf_file_path, word_file_path)
    Convert a PDF file to a Word file.
    - Input:
        1. pdf_file_path: the path to the PDF file
        2. word_file_path: the path to the Word file
    - Output: True if the conversion is successful, False otherwise.
    Example call: `pdf_convert_to_word(os.path.join(data_path, 'test.odf'), os.path.join(data_path, 'test.docx'))`: Returns True
    """
    agent.stats.add_tool_call("pdf_convert_to_word")
    if not os.path.exists(pdf_file_path):
        return f"The pdf file path: {pdf_file_path} is not correct"
    return pdf_app.pdf_convert_to_word.pdf_convert_to_word(pdf_file_path, word_file_path)

def pdf_read_file(agent: ag.Agent, file_path):
    """pdf_read_file(file_path)
    Read the content of a PDF file.
    - Input: file_path: the path to the PDF file
    - Output: the text content of the PDF file.
    Example call: `pdf_read_file(os.path.join(data_path, 'test.pdf'))`: Returns "Test"
    """
    agent.stats.add_tool_call("pdf_read_file")
    if not os.path.exists(file_path):
        return f"The pdf file path: {file_path} is not correct"
    return pdf_app.pdf_read_file.read_pdf_to_string(file_path)


# tools for Word App
def word_convert_to_pdf(agent: ag.Agent, word_file_path, pdf_file_path):
    """word_convert_to_pdf(word_file_path, pdf_file_path)
    Convert a Word file to a PDF file.
    - Input:
        1. word_file_path: the path to the Word file
        2. pdf_file_path: the path to the PDF file
    - Output: True if the conversion is successful, False otherwise.
    Example call: `word_convert_to_pdf(os.path.join(data_path, 'test.docx'), os.path.join(data_path, 'test.pdf'))`: Returns True
    """
    agent.stats.add_tool_call("word_convert_to_pdf")
    if not os.path.exists(word_file_path):
        return f"The word file path: {word_file_path} is not correct"
    return word_app.word_convert_to_pdf.word_convert_to_pdf(word_file_path, pdf_file_path)


def word_create_new_file(agent: ag.Agent, file_path):
    """word_create_new_file(file_path)
    Create a new Word file.
    - Input: file_path: the path to the new Word file
    - Output: True if the file is created successfully, False otherwise.
    Example call: `word_create_new_file(os.path.join(data_path, 'test.docx'))`: Returns True
    """
    agent.stats.add_tool_call("word_create_new_file")
    return word_app.word_create_new_file.word_create_new_file(file_path)


def word_read_file(agent: ag.Agent, file_path):
    """word_read_file(file_path)
    Read the content of a Word file.
    - Input: file_path: the path to the Word file
    - Output: the text content of the Word file.
    Example call: `word_read_file(os.path.join(data_path, 'test.docx'))`: Returns "Document contents here."
    """
    agent.stats.add_tool_call("word_read_file")
    if not os.path.exists(file_path):
        return f"The word file path: {file_path} is not correct"
    return word_app.word_read_file.word_read_file_into_string(file_path)


def word_write_to_file(agent: ag.Agent, file_path, contents):
    """word_write_to_file(file_path, contents)
    Write text to a Word file.
    - Input:
        1. file_path: the path to the Word file
        2. text: the text to write
    - Output: True if the text is written to the file successfully, False otherwise.
    Example call: `word_write_to_file(os.path.join(data_path, 'test.docx'), 'New content')`: Returns True
    """
    agent.stats.add_tool_call("word_write_to_file")
    return word_app.word_write_to_file.word_write_to_file(file_path, contents, style='pure-text')