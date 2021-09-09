import PyPDF2
import func_pdf_reader
import csv
import codecs
import time
import pickle
import os

start_time = time.time()
read_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'files'))
write_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'pdf_to_text'))
to_read = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'files\\files.txt'))

def read_folder(file_name):
    # TODO:
    # 1. Automate read files from folder
    # Works for 1 file in files.txt
    with open(file_name) as f:
        # f.readlines()
        file = ''.join(f.readlines()).strip()
    return file

def read_file(file_name):
    pdffileobj=open(file_name,'rb')
    reader = PyPDF2.PdfFileReader(pdffileobj)
    num_of_pages = reader.numPages
    print("File: ", file_name)
    print('Number of pages: ' + str(num_of_pages))

    toc_dict, toc_part_list, toc_chapter_list = func_pdf_reader.parse_toc(file_name,2)
    str_text, page_obj = func_pdf_reader.convert_pdf_to_string(file_name, toc_dict, toc_part_list, toc_chapter_list)

    print("Length of Dictionary: " + str(len(page_obj)))

    return page_obj

def write_file_codec(file_name, text):
    with codecs.open(file_name, 'w', encoding='utf-8') as f:
        f.write(text)

def write_file_dict(file_name, text):
    with open(file_name, 'wb') as f:
        pickle.dump(text, f, pickle.HIGHEST_PROTOCOL)

str_text = read_file(read_path+read_folder(to_read))



# write_file(write_path+'\\test_redo.txt', str_text)
# write_file_dict(write_path+'\\test_dict.txt', str_text)

print("My program took", time.time() - start_time, "to run")
