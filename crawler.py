#!/usr/bin/env python3

import argparse
import sys
import os
from urllib import request
from datetime import date

from bs4 import BeautifulSoup


BASE_URL = 'http://www.pyimagesearch.com/'
DEFAULT_FROM_YEAR = 2014
MONTHS_COUNT = 12
THIS_YEAR = date.today().year
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'

def save_page(name, url):
    """
    Write the article to file.
    """

    if not os.path.exists('output/articles'):
        try:
            os.mkdir('output/articles')
        except Exception as e:
            print('Error occured!', str(e))
            print('Aricle isn\'t saved:', name)
            return False

    if os.path.exists('output/articles/{0}.html'.format(name)):
        return True

    with request.urlopen(url) as resp:
        print('Saving article:', name)
        with open('output/articles/' + name + '.html', 'w') as file:
            file.write(str(resp.read(), 'utf-8'))
            return True

    return False

def crawl(year, month, have_to_save):
    """
    Crawl articles for the given year-month.
    Save the whole articles if have_to_save is true.
    Return an array of dictionaries.
    """

    print('Crawling year: {0}, month: {1}'.format(year, month))
    articles = []
    req = request.Request(BASE_URL + str(year) + '/' + str(month))
    req.add_header('User-Agent', USER_AGENT)
    try:
        resp = request.urlopen(req)
        parsed = BeautifulSoup(resp, 'html.parser')
    except Exception as e:
        return articles

    for article in parsed.find_all('article'):
        name = article.header.h2.a['title']
        url = article.header.h2.a['href']
        if have_to_save:
           if save_page(name, url):
               url = 'output/{0}.html'.format(name)

        articles.append({ 'name': name, 'url': url })

    # Check if is any pagination in the page.
    if parsed.find('div', class_='pagination') is not None:
        print('Ooops, it looks like there are more page for this month.')
        print('Page handling currently unsupported, so please contact me if you need this function.')

    return articles

# Parse the arguments.
parser = argparse.ArgumentParser(description='Crawl the articles\' names and URLs.')
parser.add_argument('output_file', help='Name of the output file.')
parser.add_argument('--offline', action='store_true', help='If used, the articles will be saved for offline reading.')
parser.add_argument('--from_year', type=int, default=DEFAULT_FROM_YEAR, help='The year from you want to crawl articles.')
args = parser.parse_args()

# Some minor validation.
if args.from_year > THIS_YEAR:
    print('Error! The given year is in the future.')
    sys.exit(1)

if not os.path.exists('output'):
    try:
        os.mkdir('output')
    except Exception as e:
        print('Error occured!', str(e))
        sys.exit(1)

# Now iterate over the years and months and write it into the file.
with open('output/' + args.output_file + '.html', 'w') as file:
    file.write('<html>\r\n')
    file.write('<body>\r\n')
    file.write('<h1><a href="http://www.pyimagesearch.com/">PyImageSearch articles</a></h1>\r\n')
    for year in range(args.from_year, THIS_YEAR + 1):
        for month in range(1, MONTHS_COUNT + 1):
            result = crawl(year, month, args.offline)
            if len(result) > 0:
                file.write('<h2>{0}.{1}</h2>\r\n'.format(year, month))
                for article in result:
                    file.write('<p><a href="{1}">{0}</a></p>\r\n'.format(article['name'], article['url']))
                file.write('\r\n')