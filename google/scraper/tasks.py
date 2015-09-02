import logging
import traceback

from celery import shared_task

from scraper.google import GoogleScraper
from scraper.models import Link, Result

log = logging.getLogger('google')


@shared_task(bind=True)
def scrape_task(self, scraper_obj):
    try:
        scraper = GoogleScraper()
        url = scraper.construct_url(scraper_obj.keyword)
        while True:
            page = scraper.get_page(url)
            if not scraper.result_count:
                scraper.get_result_count(page)
            scraper.get_links(page)
            next_url = scraper.get_next_url(page)
            if not next_url:
                break
            url = next_url

        links = []
        for l in scraper.links:
            link, _ = Link.objects.get_or_create(**l)
            links.append(link)
        result = Result(
            scraper=scraper_obj,
            result_count=scraper.result_count,
            link_count=len(scraper.links),
            links=links,
            domain_in_links=scraper.domain_in_links(scraper_obj.domain),
        )
        result.save()
    except Exception as e:
        log.error('Traceback: {}'.format(traceback.format_exc()))
        result = Result(scraper=scraper_obj, traceback=e)
        result.save()
