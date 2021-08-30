from io import StringIO

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

import nltk

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag

from collections import Counter
import string
import inspect

stop_words = set(stopwords.words('english'))

class Page:
    def __init__(self, page_number, true_page_number, org_content, content, tagged_content, counter_content, proper_nouns, key_words, index, part, chapter):
        self.page_number = page_number
        self.true_page_number = true_page_number
        self.org_content = org_content
        self.content = content
        self.tagged_content = tagged_content
        self.counter_content = counter_content
        self.proper_nouns = proper_nouns
        self.key_words = key_words
        self.index = index
        self.part = part
        self.chapter = chapter

class Part:
    def __init__(self, start_page, end_page, name, chapters):
        self.start_page = start_page
        self.end_page = end_page
        self.name = name
        self.chapters = chapters

class Chapter:
    def __init__(self, start_page, end_page, name, pages):
        self.start_page = start_page
        self.end_page = end_page
        self.name = name
        self.pages = pages


def parse_toc(file_path, maxlevel):
    fp = open(file_path, 'rb')
    parser = PDFParser(fp)
    doc = PDFDocument(parser)

    outlines = doc.get_outlines()
    toc_dict = {}
    toc_part_list = []
    toc_chapter_list = []
    for (level, title, dest, a, se) in outlines:
        if level <= maxlevel:
            title_words = title.replace('\n', '').split()
            title = ' '.join(title_words)
            ###  Dictionary
            if level == 1:
                toc_dict.update({title:{}})
                current_title = title
            elif level == 2:
                toc_dict[current_title].update({title:{}})
            ### list
            if level == 1:
                toc_part_list.append(title)
                current_title = title
            elif level == 2:
                toc_chapter_list.append(title)
    # print(toc)
    # input("Press enter to continue...")
    return toc_dict, toc_part_list, toc_chapter_list


def convert_pdf_to_string(file_path, toc_dict, toc_part_list, toc_chapter_list):
    output_string = StringIO()
    # output_string = ''
    with open(file_path, 'rb') as in_file:
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        count = 1
        chapter = 0
        part = 0
        index = False
        pages = {}
        chapters = {}
        parts = {}
        part_end_page = 0
        chapter_end_page = 0
        current_part = ''
        current_chapter = ''
        last_chapter = ''
        last_part = ''
        for i, page in enumerate(PDFPage.create_pages(doc)):
            page_number =i+1
            interpreter.process_page(page)
            org_content = page_cleanup(output_string.getvalue())
            output_string.seek(0)
            output_string.truncate(0)

            content, tagged_content, counter_content = content_cleanup(org_content)
            index_change, chapter_change, true_page_number = content_analysis(content)

            # for value in toc_dict:
            #     if value in org_content and value is not current_part:
            #         part+=1
            #         current_part = value
            #         part_start_page = count
            #         part_obj = Part(part_start_page, part_end_page, current_part, '')
            #         parts.update({last_part:part_obj})
            #         print("New Part: ", value)
            #         print("--Page number: ", count)
            #         break
            #
            #     for second_value in toc_dict[value]:
            #         if second_value in org_content and second_value is not current_chapter:
            #             chapter+=1
            #             current_chapter = second_value
            #             chapter_start_page = count
            #             chapter_obj = Chapter(part_start_page, part_end_page, current_chapter, '')
            #             chapters.update({count:chapter_obj})
            #             print("--New Chapter: ", second_value)
            #             print("----Page number: ", count)
            #             break

            

            page_obj = Page(count, true_page_number, org_content, content, tagged_content, counter_content, '', '', index, part, chapter)
            pages.update({count:page_obj})

            if current_part in toc_part_list:
                print("TEST")
                print(current_part)
                print("PREVIOUS")
                print(toc_part_list[toc_part_list.index(current_part)-1])
                print("NEXT")
                print(toc_part_list[toc_part_list.index(current_part)+1])

            if current_chapter in toc_chapter_list:
                print("TEST 2")
                print(current_chapter)
                print("PREVIOUS")
                print(toc_chapter_list[toc_chapter_list.index(current_chapter)-1])
                print("NEXT")
                print(toc_chapter_list[toc_chapter_list.index(current_chapter)+1])

            if current_part != last_part and last_part !='':
                print("Current Part:", current_part)
                print("Previous Part: ", last_part)
            #     parts[last_part].end_page = count-1
            #     parts[last_part].chapters = chapters
            #     print("--Name: ",parts[last_part].name)
            #     print("--Start: ", parts[last_part].start_page)
            #     print("--End: ", parts[last_part].end_page)
            #     chapters = {}
            #
            if current_chapter != last_chapter and last_chapter != '':
                print("Current Chapter: ", current_chapter)
                print("Previous Chapter: ", last_chapter)
            #     chapters[last_chapter].end_page  = count-1
            #     chapters[last_chapter].pages = pages
            #
            #     print("--Name: ",chapters[last_part].name)
            #     print("--Start: ", chapters[last_part].start_page)
            #     print("--End: ", chapters[last_part].end_page)
            #     pages = {}

            if current_part != last_part and last_part == '':
                print("Current Part:", current_part)
                print("Previous Part: ", last_part)
                last_part = current_part
            if current_chapter != last_chapter and last_chapter == '':
                print("Current Chapter: ", current_chapter)
                print("Previous Chapter: ", last_chapter)
                last_chapter = current_chapter

            last_chapter = current_chapter
            count +=1
            input("Press enter to continue...")
    return(output_string.getvalue(), pages)


def content_cleanup(content):
    punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''

    word_tokens = word_tokenize(content)

    filtered_content = [word for word in word_tokens if not word.lower() in stop_words]
    filtered_content = [word.lower() for word in filtered_content if not word in punctuations]
    tagged_content = pos_tag(filtered_content)
    counter_content = Counter(tagged_content)

    # counter_content= Counter([j for i,j in pos_tag(filtered_content)])

    # print(counter_content)

    return filtered_content, tagged_content, counter_content


def content_analysis(content):
    index = False
    chapter = False
    true_page_number = 0

    try:
        if 'index' in content:
            index = True

        if 'chapter' in content:
            chapter = True

        return index, chapter, true_page_number
    except:
        return index, chapter, true_page_number


def page_cleanup(f_read):
    initial_text = []
    text = []
    initial_text = f_read.split("\n")

    for item in initial_text:
        item = item.strip()
        if item == '':
            item = '\n'

        text.append(''.join(item))

    return ' '.join(text)
