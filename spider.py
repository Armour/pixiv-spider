#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Chong Guo
# @Date:   2017-03-12 23:59:09

import os

from pixivpy3 import AppPixivAPI
from config import ContentType, RankingType, DEFAULT_DOWNLOAD_COUNT
from datetime import datetime


class PixivSpider:
    def __init__(self):
        """
        Init PixivSpider
        """
        self.api = AppPixivAPI()
        self.directory = "download"
        self.count = 0

    def clear(self):
        print("Finish! Total download illusts number: %d" % self.count)

    def create_download_folder(self):
        """
        Setup image download directory
        """
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def download_illusts(self, illusts=None):
        """
        Download illusts
        """
        for illust in illusts:
            image_url = illust.meta_single_page.get('original_image_url',
                                                    illust.image_urls.large)
            print(u"👀  Found illust: %s (%s)" % (illust.title, image_url))
            url_basename = os.path.basename(image_url)
            extension = os.path.splitext(url_basename)[1]
            name = "illust_id_%d_%s%s" % (illust.id, illust.title, extension)
            name = name.replace("/", ":")
            if not os.path.exists(self.directory + '/' + name):
                print(u"✅  Download illust: %s (%s)" % (illust.title, image_url))
                self.api.download(image_url, path=self.directory, name=name)
            else:
                print(u"✨  Already download: %s: %s" % (illust.title, image_url))

            self.count += 1

    def get_top_ranking_illusts(self,
                                count=DEFAULT_DOWNLOAD_COUNT,
                                ranking_type=RankingType.DAY,
                                date=datetime.today().strftime("%Y-%m-%d"),
                                download=False):
        """
        Get top ranking illusts
        :count: the number of illusts that we want to download
        :ranking_type: ranking type
        :date: date
        :download: download flag
        """
        json_result = self.api.illust_ranking(ranking_type, date=date)
        illusts = json_result.illusts
        while len(json_result) != 0 and len(illusts) < count:
            next_qs = self.api.parse_qs(json_result.next_url)
            if next_qs is None:
                break
            json_result = self.api.illust_ranking(**next_qs)
            illusts += json_result.illusts

        if download:
            count = min(count, len(illusts))
            self.download_illusts(illusts=illusts[:count])
        return illusts[:count]

    def get_recommended_illusts(self,
                                count=DEFAULT_DOWNLOAD_COUNT,
                                content_type=ContentType.ILLUST,
                                download=False):
        """
        Get recommended illusts
        :count: the number of illusts that we want to download
        :content_type: content type
        :download: download flag
        """
        json_result = self.api.illust_recommended(content_type)
        illusts = json_result.illusts
        while len(json_result) != 0 and len(illusts) < count:
            next_qs = self.api.parse_qs(json_result.next_url)
            if next_qs is None:
                break
            json_result = self.api.illust_ranking(**next_qs)
            illusts += json_result.illusts

        if download:
            count = min(count, len(illusts))
            self.download_illusts(illusts=illusts[:count])
        return illusts[:count]

    def get_user_ids_from_illusts(self, illusts):
        """
        Get user ids by illusts
        """
        user_ids = []
        for illust in illusts:
            user_ids.append(illust.user.id)
        return user_ids

    def get_illusts_by_user_ids(self,
                                user_ids,
                                count=DEFAULT_DOWNLOAD_COUNT,
                                content_type=ContentType.ILLUST,
                                download=False):
        """
        Get illusts by user id
        """
        ret = {}
        for user_id in user_ids:
            json_result = self.api.user_illusts(user_id=user_id, type=content_type)
            illusts = json_result.illusts
            while len(json_result) != 0 and len(illusts) < count:
                next_qs = self.api.parse_qs(json_result.next_url)
                if next_qs is None:
                    break
                json_result = self.api.illust_ranking(**next_qs)
                illusts += json_result.illusts

            if download:
                count = min(count, len(illusts))
                self.download_illusts(illusts=illusts[:count])
            ret[user_id] = illusts[:count]
        return ret


if __name__ == '__main__':
    spider = PixivSpider()
    spider.create_download_folder()
    top_ranking_illusts = spider.get_top_ranking_illusts(download=True, count=1)
    recommended_illusts = spider.get_recommended_illusts(download=True, count=1)
    user_ids = spider.get_user_ids_from_illusts(top_ranking_illusts + recommended_illusts)
    more_illusts = spider.get_illusts_by_user_ids(user_ids=user_ids, download=True, count=1)
    spider.clear()
