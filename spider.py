#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Chong Guo
# @Date:   2017-03-12 23:59:09

import os

from pixivpy3 import AppPixivAPI
from config import RankingType, DEFAULT_DOWNLOAD_COUNT
from datetime import datetime


class PixivSpider:
    def __init__(self):
        """
        Init PixivSpider
        """
        self.api = AppPixivAPI()
        self.directory = "download"

    def create_download_folder(self):
        """
        Setup image download directory
        """
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def get_top_ranking_illusts(self,
                                count=DEFAULT_DOWNLOAD_COUNT,
                                ranking_type=RankingType.DAY,
                                date=datetime.today().strftime("%Y-%m-%d")):
        """
        Download top ranking illusts
        :count: the number of illusts that we want to download
        :ranking_type: ranking type
        """
        json_result = self.api.illust_ranking(ranking_type, date=date)
        count = min(count, len(json_result.illusts))

        for illust in json_result.illusts[:count]:
            image_url = illust.meta_single_page.get('original_image_url',
                                                    illust.image_urls.large)
            print("Found %s: %s" % (illust.title, image_url))
            url_basename = os.path.basename(image_url)
            extension = os.path.splitext(url_basename)[1]
            name = "illust_id_%d_%s%s" % (illust.id, illust.title, extension)
            if not os.path.exists(self.directory + '/' + name):
                print("Download %s: %s" % (illust.title, image_url))
                self.api.download(image_url, path=self.directory, name=name)
            else:
                print("Already downloaded: %s: %s" % (illust.title, image_url))


if __name__ == '__main__':
    spider = PixivSpider()
    spider.create_download_folder()
    spider.get_top_ranking_illusts()
