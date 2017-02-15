#!/bin/python
#-*-coding:utf-8-*-
from crawl import Crawler
import asyncio

class Scaner:

    def __init__(self, host):
        self.host = host

    def crawl(self):

        loop = asyncio.get_event_loop()
        crawler = Crawler([self.host], max_tasks=100)
        loop.run_until_complete(crawler.crawl())
        print('Finished {0} urls in {1:.3f} secs'.format(len(crawler.done),
                                                         crawler.t1 - crawler.t0))
        crawler.close()

        loop.close()