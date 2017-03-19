#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Chong Guo
# @Date:   2017-03-12 23:59:09

import os
import json

from pixivpy3 import AppPixivAPI, PixivError
from config import ContentType, RankingType, DEFAULT_DOWNLOAD_COUNT_IN_TOTAL, DEFAULT_DOWNLOAD_COUNT_EACH_USER
from datetime import datetime
from sets import Set


class PixivSpider:
    def __init__(self):
        """
        Init PixivSpider
        """
        self.api = AppPixivAPI()
        self.directory = 'download'
        if not os.path.exists('info.json'):
            self.data = {'illusts': []}
            self.count = 0
            print("Create new info.json file")
        else:
            with open('info.json', 'r') as f:
                self.data = json.load(f)
                self.count = len(self.data['illusts'])
                print("Load existing info.json file")
                print("Existed illusts count: %d" % self.count)
        self.file = open('info.json', 'w')
        self.illusts_names = Set()
        for illust in self.data['illusts']:
            self.illusts_names.add(illust['name'])

    def exit(self):
        """
        Stop spider and print logs
        """
        json.dump(self.data, self.file, indent=2)
        self.file.close()
        print("Finish! Total downloaded illusts number: %d" % self.count)

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
            image_url = illust.meta_single_page.get('original_image_url', illust.image_urls.large)
            print(u"👀  Found illust: %s (%s)" % (illust.title, image_url))
            url_basename = os.path.basename(image_url)
            extension = os.path.splitext(url_basename)[1]
            name = "%d_%s%s" % (illust.id, illust.title, extension)
            name = name.replace('/', ':')
            if name not in self.illusts_names:
                self.count += 1
                self.data['illusts'].append({
                    'id': self.count,
                    'name': name,
                    'illust_id': illust.id,
                    'illustrator_id': illust.user.id,
                    'source_url': image_url
                })
                self.illusts_names.add(name)
                name = "%d_" % self.count + name
                try:
                    self.api.download(image_url, path=self.directory, name=name)
                except PixivError:
                    print(u"😢  PixivError!!! Skip this illusts")
                    continue
                print(u"✅  Download illust: %s (%s)" % (illust.title, image_url))
            else:
                print(u"✨  Already download: %s: %s" % (illust.title, image_url))

    def get_top_ranking_illusts(self,
                                count=DEFAULT_DOWNLOAD_COUNT_IN_TOTAL,
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
            try:
                json_result = self.api.illust_ranking(**next_qs)
            except TypeError:
                break
            illusts += json_result.illusts

        if download:
            count = min(count, len(illusts))
            self.download_illusts(illusts=illusts[:count])
        return illusts[:count]

    def get_recommended_illusts(self,
                                count=DEFAULT_DOWNLOAD_COUNT_IN_TOTAL,
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
            try:
                json_result = self.api.illust_ranking(**next_qs)
            except TypeError:
                break
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
                                count=DEFAULT_DOWNLOAD_COUNT_EACH_USER,
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
                try:
                    json_result = self.api.illust_ranking(**next_qs)
                except TypeError:
                    break
                illusts += json_result.illusts

            if download:
                count = min(count, len(illusts))
                self.download_illusts(illusts=illusts[:count])
            ret[user_id] = illusts[:count]
        return ret


if __name__ == '__main__':
    spider = PixivSpider()
    spider.create_download_folder()
    top_ranking_illusts = spider.get_top_ranking_illusts(download=True, count=20)
    recommended_illusts = spider.get_recommended_illusts(download=True, count=20)
    user_ids = spider.get_user_ids_from_illusts(top_ranking_illusts + recommended_illusts)
    spider.get_illusts_by_user_ids(user_ids=user_ids, download=True, count=20)
    spider.exit()
