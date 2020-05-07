import requests 
import argparse

import logging
logging.basicConfig(level = logging.INFO) #Basic log
logger = logging.getLogger(__name__) #Gets the logger

import news_page_objects as news

from bs4 import BeautifulSoup as bs
from config import config

import re
is_well_formed_link = re.compile(r'^https?://.+/.+$') #https://mypage.com/hello-world
is_root_path = re.compile(r'^/.+$') #/my-text

from requests.exceptions import HTTPError
from urllib3.exceptions import MaxRetryError

import datetime
import csv



#url = 'https://www.pagina12.com.ar/'

def main(news_site_id):
    url = config()['news_sites'][news_site_id]['url']
    logging.info(f'Starting to scrap {url}')
    homepage = news.HomePage(news_site_id, url)

    logging.info(f'Getting header links')
    header_links = [_build_link(url,link) for link in homepage.header_links] 

    logging.info(f'Getting news pages links')
    sections = [news.SectionPage(news_site_id, section) for section in header_links]
    links = [section.article_links for section in sections]
    flat_links = [_build_link(url,item)  for sublist in links for item in sublist]

    logging.info('Fetching Articles')
    #articles = [news.ArticlePage(news_site_id,article) for article in flat_links]
    # _save_articles(news_site_id, flat_links)
    articles = [_fetch_article(news_site_id, url, article) for article in flat_links]
    articles = [article for article in articles if article]

    logging.info(f'Saving articles')
    _save_articles(news_site_id, articles)
    logging.info(f'Articles saved')
    #article_page = news.ArticlePage(news_site_id, flat_links[0])
    # print(f'Body:{article_page.body}')
    # print(f'Prefix: {article_page.prefix}')
    # print(f'Title: {article_page.title}')
    # print(f'Summary: {article_page.summary}')
    # print(f'Author: {article_page.author}')

def _build_link(url,link):
    if is_well_formed_link.match(link):
        return link
    elif is_root_path.match(link):
        return f'{url}{link}'
    else:
        return f'{url}/{link}'

def _fetch_article(news_site_id, url,link):
    logger.info(f'Starting to fetch article at {link}')
    article = None
    try:
        article = news.ArticlePage(news_site_id, _build_link(url,link))
    except (HTTPError, MaxRetryError) as e:
        logger.warning('Error while fetching article', exc_info = False)
    if article and not article.body:
        logger.warning('Invalid article. There is no body in it')
        return None
    return article        

def _save_articles(news_site_id,articles):
    now_date = datetime.datetime.now().strftime('%Y_%m_%d')
    out_file_name = f'{news_site_id}_{now_date}_articles.csv'

    csv_headers = list(filter(lambda property: not property.startswith('_'),dir(articles[0])))
    with open(out_file_name, mode = 'w+') as f:
        writer = csv.writer(f)
        writer.writerow(csv_headers)

        for article in articles:
            row = [str(getattr(article,prop)) for prop in csv_headers]
            writer.writerow(row)

if  __name__ == '__main__':
    parser = argparse.ArgumentParser()
    news_site_choices = list(config()['news_sites'].keys()) #config returns a map, keys returns an iterator which we transform into a list
    parser.add_argument('news_site', 
                        help='News site to scrap',
                        type = str,
                        choices = news_site_choices)
    args = parser.parse_args() #We parse the arguments into strings
    main(args.news_site) #