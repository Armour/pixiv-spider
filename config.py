#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Config file for pixiv spider."""

__author__ = 'Chong Guo'
__copyright__ = 'Copyright 2018, Chong Guo'
__license__ = 'MIT'
__email__ = 'armourcy@email.com'


class RankingType():
    DAY = 'day'
    WEEK = 'week'
    MONTH = 'month'
    DAY_MALE = 'day_male'
    DAY_FEMALE = 'day_female'
    WEEK_ORIGIONAL = 'week_origional'
    WEEK_ROOKIE = 'week_rookie'
    DAY_MANGA = 'day_manga'

class ContentType():
    ILLUST = 'illust'
    MANGA = 'manga'

DEFAULT_DOWNLOAD_TOP_RANKING_COUNT = 10
DEFAULT_DOWNLOAD_RECOMMENDED_COUNT = 10
DEFAULT_DOWNLOAD_EACH_USER_COUNT = 5
