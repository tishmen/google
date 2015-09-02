from django.db import models


class Scraper(models.Model):

    class Meta:
        unique_together = ('keyword', 'domain')

    keyword = models.CharField(max_length=100)
    domain = models.CharField(max_length=100)

    def __str__(self):
        return self.keyword


class Result(models.Model):

    scraper = models.ForeignKey('Scraper')
    result_count = models.IntegerField(default=0)
    link_count = models.IntegerField(default=0)
    links = models.ManyToManyField('Link', blank=True)
    domain_in_links = models.BooleanField(default=False)
    traceback = models.TextField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'results for {}'.format(self.scraper.keyword)


class Link(models.Model):

    url = models.URLField(max_length=1000, unique=True)

    def __str__(self):
        return self.url
