from config import config
import bs4
from bs4 import BeautifulSoup as bs
import requests

import logging
logging.basicConfig(level = logging.INFO) #Basic log




class NewsPage:
    def __init__(self, news_site_id, url):
        self._config = config()['news_sites'][news_site_id] #Gets the yaml map
        self._queries = self._config['queries'] #get a list of queries
        self._html = None #Response parsed
        self._url = url
        
        self._request_page(url)
    
    def _request_page(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status() #Raises an error if the status is not 200
            self._html = bs(response.text,'lxml') #Parsing response into a soup
        except Exception as e:
            self._html = bs4.BeautifulSoup('')
            logging.info('Request Error')
            logging.info(e)
            logging.info('\n')

    def _select(self, query_string):
        return self._html.select(query_string)

    def _find_by_class(self, query_string):
        return self._html.find(query_string['tag'], class_=query_string['class_'])
        #return self._html.find(query_string.tag, attrs={'class': query_string.class_})
    def _find_all(self, query_string):
        return self._html.find_all(query_string)



class HomePage(NewsPage):
    def __init__(self, news_site_id,url):
        super().__init__(news_site_id,url)
    
    @property
    def header_links(self):
        queries = self._queries['homepage_header_links']
        header = self._find_by_class(queries).find_all(queries['all'])
        links = [section.a.get('href') for section in header]
        return links
    @property
    def article_links(self):
        link_list = []
        for link in self._select(self._queries['homepage_article_links']):
            if link and link.has_attr('href'):
                link_list.append(link)
        return [link['href'] for link in link_list]
    @property
    def article_links2(self):
        try:
                featured_article = self.find('div', attrs={'class': 'featured-article__container'}).a 
                featured_article_link = featured_article.get('href')
        except:
            print('No class: featured-article__container')
        #Gets rest of the links
        articles_list = self.find('ul', attrs={'class':'article-list'})
        links = [li.a.get('href') for li in articles_list if li.a is not None]
        try:
            links.insert(0,featured_article_link)
        except:
            pass
        return links       

class SectionPage(HomePage):
    def __init__(self, news_site_id, url):
        super().__init__(news_site_id, url)


class ArticlePage(NewsPage):
    def __init__(self, news_site_uid, url):
        super().__init__(news_site_uid, url)

    @property
    def prefix(self):
        result = self._select(self._queries['article_prefix'])
        return result[0].text if len(result) else ''
    @property
    def title(self):
        result = self._select(self._queries['article_title'])
        return result[0].text if len(result) else ''
    @property
    def summary(self):
        result = self._select(self._queries['article_summary'])
        return result[0].text if len(result) else ''
    @property
    def body(self):
        result = self._select(self._queries['article_body'])
        return result[0].text if len(result) else ''
    @property
    def author(self):
        result = self._select(self._queries['article_author'])
        return result[0].text if len(result) else 'anonymus'
    @property
    def url(self):
        return self._url
