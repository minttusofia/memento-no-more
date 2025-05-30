# %%
import os
import shutil
import json

testbed_dir = "testbed"
results = {}

def clear_testbed():
    if os.path.exists(testbed_dir):
        shutil.rmtree("testbed")
    os.makedirs("testbed")

def print_results():
    print(json.dumps(results, indent=4))

# %%
# --------- CALENDAR APP ---------
app_results = {}
results["caledar"] = app_results

# %%
# fixes:
#  - change absolute file paths to relative ones

from tasks.t_OfficeBench.OfficeBench.apps.calendar_app.calendar_create_event import create_event

clear_testbed()
app_results["create_event"] = create_event("Alice", "Meeting with Bob", "2025-03-26 16:00:00", "2025-03-26 17:00:00")

# %%
# fixes:
#  - pass file contents rather than the file name to `Calendar.from_ical`
#  - change "subcomponent" to "subcomponents"

from tasks.t_OfficeBench.OfficeBench.apps.calendar_app.calendar_delete_event import delete_event


clear_testbed()
create_event("Alice", "Meeting with Bob", "2025-03-26 16:00:00", "2025-03-26 17:00:00")
app_results["delete_event"] = delete_event("Alice", "Meeting with Bob")

# %%
# fixes:
#  - change absolute file paths to relative ones

from tasks.t_OfficeBench.OfficeBench.apps.calendar_app.calendar_list_events import list_events

clear_testbed()
create_event("Alice", "Meeting with Bob", "2025-03-26 16:00:00", "2025-03-26 17:00:00")
create_event("Alice", "Gym", "2025-03-26 07:00:00", "2025-03-26 0:08:00")
events = list_events("Alice")
app_results["list_events"] = bool(events)

# %%
# --------- EMAIL APP ---------
app_results = {}
results["email"] = app_results

# %%
# fixes:
#  - change absolute file paths to relative ones

from tasks.t_OfficeBench.OfficeBench.apps.email_app.email_send_email import send_email

clear_testbed()
app_results["send_email"] = bool(send_email("Alice", "Bob", "Meeting tomorrow", "Hi, Bob! \n\nAre you up for a meeting tomorrow at 16?"))

# %%
# fixes:
#  - change absolute file paths to relative ones

from tasks.t_OfficeBench.OfficeBench.apps.email_app.email_read_email import read_email

clear_testbed()
send_email("Alice", "Bob", "Meeting tomorrow", "Hi, Bob! \n\nAre you up for a meeting tomorrow at 16?")
app_results["read_email"] = bool(read_email("Alice", "Meeting tomorrow"))

# %%
# fixes:
#  - change absolute file paths to relative ones

from tasks.t_OfficeBench.OfficeBench.apps.email_app.email_list_emails import list_emails

clear_testbed()
send_email("Alice", "Bob", "Meeting tomorrow", "Hi, Bob! \n\nAre you up for a meeting tomorrow at 16?")
send_email("Bob", "Alice", "Re: Meeting tomorrow", "Hi, Alice! \n\nSure, see you tomorrow at 16:00.")
app_results["list_emails"] = bool(list_emails("Alice"))

# %%
# --------- EXCEL APP ---------
app_results = {}
results["excel"] = app_results

# %%
# fixes: none

from tasks.t_OfficeBench.OfficeBench.apps.excel_app.excel_create_new_file import excel_create_new_file

clear_testbed()
app_results["excel_create_new_file"] = excel_create_new_file("testbed/attendance.xlsx")

# %%
# fixes: none

from tasks.t_OfficeBench.OfficeBench.apps.excel_app.excel_set_cell import excel_set_cell

clear_testbed()
app_results["excel_set_cell"] = excel_set_cell("testbed/attendance.xlsx", "1", "3", "2")

# %%
# this function is missing, instead a copy of excel_set_cell is defined in its place

# from tasks.t_OfficeBench.OfficeBench.apps.excel_app.excel_delete_cell import excel_delete_cell

# app_results["excel_delete_cell"] = False


# %%
# fixes: none

from tasks.t_OfficeBench.OfficeBench.apps.excel_app.excel_read_file import excel_read_file

clear_testbed()
excel_set_cell("testbed/attendance.xlsx", "present", "1", "2")
excel_set_cell("testbed/attendance.xlsx", "Alice", "1", "1")
excel_set_cell("testbed/attendance.xlsx", "absent", "2", "2")
excel_set_cell("testbed/attendance.xlsx", "Bob", "2", "1")
app_results["excel_set_cell"] = bool(excel_read_file("testbed/attendance.xlsx"))

# %%
# fixes:
#  - change "libreoffice" command to "soffice"

from tasks.t_OfficeBench.OfficeBench.apps.excel_app.excel_convert_to_pdf import excel_convert_to_pdf

clear_testbed()
excel_set_cell("testbed/attendance.xlsx", "present", "1", "2")
excel_set_cell("testbed/attendance.xlsx", "Alice", "1", "1")
excel_set_cell("testbed/attendance.xlsx", "absent", "2", "2")
excel_set_cell("testbed/attendance.xlsx", "Bob", "2", "1")
excel_convert_to_pdf("testbed/attendance.xlsx", "testbed/attendance.pdf")
app_results["excel_convert_to_pdf"] = os.path.isfile("testbed/attendance.pdf")

# %%
# --------- OCR APP ---------
app_results = {}
results["OCR"] = app_results

#  %%
# fixes: none

from tasks.t_OfficeBench.OfficeBench.apps.ocr_app.ocr_recognize_file import ocr_recognize_file

clear_testbed()
text = ocr_recognize_file("test_materials/image_with_text.png")
app_results["ocr_recognize_file"] = bool(text)


# %%
# --------- PDF APP ---------
app_results = {}
results["PDF"] = app_results

# %%
# fixes: none

from tasks.t_OfficeBench.OfficeBench.apps.pdf_app.pdf_convert_to_image import pdf_convert_to_image

clear_testbed()
excel_set_cell("testbed/attendance.xlsx", "present", "1", "2")
excel_set_cell("testbed/attendance.xlsx", "Alice", "1", "1")
excel_set_cell("testbed/attendance.xlsx", "absent", "2", "2")
excel_set_cell("testbed/attendance.xlsx", "Bob", "2", "1")
excel_convert_to_pdf("testbed/attendance.xlsx", "testbed/attendance.pdf")
status = pdf_convert_to_image("testbed/attendance.pdf", "testbed/attendance.png")
app_results["pdf_convert_to_image"] = status == "Success"

# %%
# fixes: none

from tasks.t_OfficeBench.OfficeBench.apps.pdf_app.image_convert_to_pdf import image_convert_to_pdf

clear_testbed()
excel_set_cell("testbed/attendance.xlsx", "present", "1", "2")
excel_set_cell("testbed/attendance.xlsx", "Alice", "1", "1")
excel_set_cell("testbed/attendance.xlsx", "absent", "2", "2")
excel_set_cell("testbed/attendance.xlsx", "Bob", "2", "1")
excel_convert_to_pdf("testbed/attendance.xlsx", "testbed/attendance.pdf")
pdf_convert_to_image("testbed/attendance.pdf", "testbed/attendance.png")
status = image_convert_to_pdf("testbed/attendance.png", "testbed/attendance_scan.pdf")
app_results["image_convert_to_pdf"] = status == "Success"

# %%
# fixes: none

from tasks.t_OfficeBench.OfficeBench.apps.pdf_app.pdf_convert_to_word import pdf_convert_to_word

clear_testbed()
excel_set_cell("testbed/attendance.xlsx", "present", "1", "2")
excel_set_cell("testbed/attendance.xlsx", "Alice", "1", "1")
excel_set_cell("testbed/attendance.xlsx", "absent", "2", "2")
excel_set_cell("testbed/attendance.xlsx", "Bob", "2", "1")
excel_convert_to_pdf("testbed/attendance.xlsx", "testbed/attendance.pdf")
status = pdf_convert_to_word("testbed/attendance.pdf", "testbed/attendance.docx")
app_results["pdf_convert_to_word"] = status == "Success"

# %%
# fixes: none

from tasks.t_OfficeBench.OfficeBench.apps.pdf_app.pdf_read_file import read_pdf_to_string

clear_testbed()
excel_set_cell("testbed/attendance.xlsx", "present", "1", "2")
excel_set_cell("testbed/attendance.xlsx", "Alice", "1", "1")
excel_set_cell("testbed/attendance.xlsx", "absent", "2", "2")
excel_set_cell("testbed/attendance.xlsx", "Bob", "2", "1")
excel_convert_to_pdf("testbed/attendance.xlsx", "testbed/attendance.pdf")
text = read_pdf_to_string("testbed/attendance.pdf")
app_results["read_pdf_to_string"] = bool(text)
# print(text)

# %%
# --------- SHELL APP ---------
# this tool is not implemented in python
# we can use our own shell execution tool if needed

# %%
# --------- WORD APP ---------
app_results = {}
results["word"] = app_results

# %%
# fixes: none

from tasks.t_OfficeBench.OfficeBench.apps.word_app.word_create_new_file import word_create_new_file

clear_testbed()
app_results["word_create_new_file"] = word_create_new_file("testbed/Meeting_agenda.docx")
app_results["word_create_new_file"]


# %%
# fixes: none

from tasks.t_OfficeBench.OfficeBench.apps.word_app.word_write_to_file import word_write_to_file

clear_testbed()
word_create_new_file("testbed/Meeting_agenda.docx")
word_write_to_file("testbed/Meeting_agenda.docx", "Meeting with Bob", "title")
word_write_to_file("testbed/Meeting_agenda.docx", "Room 404, 26th of March, 2025", "subtitle")
app_results["word_write_to_file"] = word_write_to_file("testbed/Meeting_agenda.docx", "Bob is a great employee, he deserves a raise.")


# %%
# fixes: none

from tasks.t_OfficeBench.OfficeBench.apps.word_app.word_read_file import word_read_file_into_string

clear_testbed()
word_create_new_file("testbed/Meeting_agenda.docx")
word_write_to_file("testbed/Meeting_agenda.docx", "Meeting with Bob", "title")
word_write_to_file("testbed/Meeting_agenda.docx", "Room 404, 26th of March, 2025", "subtitle")
word_write_to_file("testbed/Meeting_agenda.docx", "Bob is a great employee, he deserves a raise.")
text = word_read_file_into_string("testbed/Meeting_agenda.docx")
app_results["word_read_file"] = bool(text)

# %%
# fixes: fix implementation for mac version using "soffice"

from tasks.t_OfficeBench.OfficeBench.apps.word_app.word_convert_to_pdf import word_convert_to_pdf

clear_testbed()
word_create_new_file("testbed/Meeting_agenda.docx")
word_write_to_file("testbed/Meeting_agenda.docx", "Meeting with Bob", "title")
word_write_to_file("testbed/Meeting_agenda.docx", "Room 404, 26th of March, 2025", "subtitle")
word_write_to_file("testbed/Meeting_agenda.docx", "Bob is a great employee, he deserves a raise.")
app_results["word_convert_to_pdf"] = word_convert_to_pdf("testbed/Meeting_agenda.docx", "testbed/Meeting_agenda.pdf")


# %%
clear_testbed()
print_results()

