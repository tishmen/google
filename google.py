import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode, urlparse, parse_qs


class Google(object):

    def __init__(self):
        self.result_count = 0
        self.link_count = 0
        self.links = []

    def construct_url(self, keyword, **kwargs):
        self.keyword = keyword
        kwargs['q'] = [keyword]
        query_string = urlencode(kwargs, doseq=True)
        return 'http://www.google.com/search?' + query_string

    def get_page(self, url):
        response = requests.get(url)
        print('response {} for {}'.format(response.status_code, url))
        return BeautifulSoup(response.content, 'html.parser')

    def get_result_count(self, page):
        try:
            stats = page.find(id='resultStats').string
            self.result_count = int(
                ''.join(filter(lambda x: x.isdigit(), stats))
            )
            print('result count: {}'.format(self.result_count))
        except TypeError:
            print('no result count')
            pass

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
        print('got {} links'.format(len(links)))

    def get_next_url(self, page):
        try:
            next_ = page.select_one('td[style="text-align:left"] a')['href']
            return 'https://www.google.com' + next_
        except TypeError:
            print('no more pages')
            return None

    def domain_in_links(self, domain):
        for link in self.links:
            netloc = urlparse(link).netloc
            if domain in netloc:
                print('domain in links')
                return True
        print('domain not in links')
        return False

    def get_results(self):
        return {
            'keyword': self.keyword,
            'result_count': self.result_count,
            'link_count': len(self.links),
            'links': self.links
        }

###############################################################################
# TEST
###############################################################################

KEYWORD = 'test'
DOMAIN = 'test.com'

if __name__ == '__main__':
    g = Google()
    url = g.construct_url(KEYWORD)
    while True:
        page = g.get_page(url)
        if not g.result_count:
            g.get_result_count(page)
        g.get_links(page)
        next_url = g.get_next_url(page)
        if not next_url:
            break
        url = next_url
    print(g.get_results())
    print(g.domain_in_links(DOMAIN))
