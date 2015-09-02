import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode, urlparse, parse_qs

log = logging.getLogger('google')


class GoogleException(Exception):

    pass


class GoogleScraper(object):

    def __init__(self):
        self.result_count = 0
        self.link_count = 0
        self.links = []

    def construct_url(self, keyword, **kwargs):
        kwargs['q'] = [keyword]
        query_string = urlencode(kwargs, doseq=True)
        return 'http://www.google.com/search?' + query_string

    def get_page(self, url):
        response = requests.get(url)
        if not response == 200:
            raise GoogleException('Blocked by Google')
        return BeautifulSoup(response.content, 'html.parser')

    def get_result_count(self, page):
        try:
            stats = page.find(id='resultStats').string
            self.result_count = int(
                ''.join(filter(lambda x: x.isdigit(), stats))
            )
            log.debug('result count {}'.format(self.result_count))
        except TypeError:
            raise GoogleException('No results found')

    def get_links(self, page):
        links = []
        for link in page.select('.g > .r a'):
            try:
                query = urlparse(link['href']).query
                query_parsed = parse_qs(query)
                links.append(query_parsed['q'][0])
            except KeyError:
                links.append(link['href'])
        self.links.extend(links)
        log.debug('link count {}'.format(len(links)))

    def get_next_url(self, page):
        try:
            next_ = page.select_one('td[style="text-align:left"] a')['href']
            return 'https://www.google.com' + next_
        except TypeError:
            log.debug('last page')
            return None

    def domain_in_links(self, domain):
        for link in self.links:
            netloc = urlparse(link).netloc
            if domain in netloc:
                log.debug('domain in links')
                return True
        log.debug('domain not in links')
        return False
