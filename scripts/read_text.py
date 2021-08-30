import codecs

def read_file(file_name):
    with codecs.open(file_name, 'r', encoding='utf-8') as f_read:
        count = 0
        text = []

        for line in f_read:
            line = line.splitlines()
            if line == ['']:
                line = '\n'
            text.append(' '.join(line))

        return text

def write_file(file_name, text):
    str = ''
    with codecs.open(file_name, 'w', encoding='utf-8') as f_write:
        f_write.write(str.join(text))



text = read_file(r'C:\Users\Anni\Desktop\Mythology_Scripts\pdf_to_text\\test.txt')
write_file(r'C:\Users\Anni\Desktop\Mythology_Scripts\pdf_to_text\\test2.txt', text)
