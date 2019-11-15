#!/usr/bin/python
#

import datetime
import re
import shutil
import urllib.request
from io import StringIO

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage

url = 'https://www.trin.cam.ac.uk/wp-content/uploads/Hall-Menu-cur.pdf'
pdf_name = 'trin_menu.pdf'
month = dict(Jan=1, Feb=2, Mar=3, Apr=4, May=5, Jun=6, Jul=7, Aug=8, Sep=9, Oct=10, Nov=11, Dec=12)


def download_file():
    with urllib.request.urlopen(url) as response, open(pdf_name, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)


def extract_text_from_pdf(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos = set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching,
                                  check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()
    return text


def parse_text():
    raw = extract_text_from_pdf(pdf_name)

    days = re.split('LUNCH|DINNER', raw)  # Split raw on meals
    days = list(map(lambda s: s.split('\n'), days))  # Split text into lines
    days = [list(filter(lambda s: not (s.isspace() or s == ''), d)) for d in days]  # Remove empty lines

    begin_date = days[0][1]  # Gets first date of the week

    days = [list(filter(lambda s: s.split()[0] != s.split()[0].upper(), d)) for d in days]
    # Remove entries like MONDAY, TUESDAY, DISHES MAY CONTAIN...
    days.pop(0)  # Remove first, empty sublist

    days = [list(map(str.rstrip, d)) for d in days]  # Strip trailing whitespace

    # Use leading whitespace to merge entries
    # Also use ( and ) to merge notes
    for meal in days:
        i = 0
        while i < len(meal):
            if meal[i][0].isspace() or (i > 0 and meal[i - 1][0] == '(' and meal[i - 1][-1] != ')'):
                meal[i - 1] += ' ' + meal.pop(i).lstrip()
                i -= 1
            i += 1

    begin_date = begin_date.split()

    dd = int(begin_date[1][0:-2])
    mm = int(month[begin_date[2]])
    yy = datetime.datetime.now().year + (1 if datetime.datetime.now().month == 12 and mm == '1' else 0)

    return datetime.datetime(year=yy, month=mm, day=dd), days


if __name__ == '__main__':
    download_file()
    parse_text()
