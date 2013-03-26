from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
from utils import cronlog
from pom import scrape
import datetime

class Command(BaseCommand):
    args = '<modules to scrape>'
    help = 'Scrapes data and stores in memcached with a timestamp'

    def handle(self, *args, **options):
        for mod_name in args:
            try:
                mod = getattr(scrape, mod_name)
            except AttributeError:
                self.stderr.write(cronlog.fmt("pom.scrape.%s does not exisn" % mod_name))
                continue
            try:
                data = mod.scrape_all()
            except:
                self.stderr.write(cronlog.fmt("pom.scrape.%s failed to scrape" % mod_name))
                continue
            cache.set('pom.'+mod_name, (data, datetime.datetime.now()))
            self.stdout.write(cronlog.fmt("pom.scrape.%s scraped successfully" % mod_name))