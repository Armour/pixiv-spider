#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Chong Guo
# @Date:   2017-03-12 23:59:59

import requests

login_url = r'https://www.pixiv.net/login.php'
data = {
    'mode': 'login',
    'return_to': '/',
    'pixiv_id': '493377211',
    'pass': 'qw123456',
    'skip': '1'
}

s = requests.Session()
res = s.post(login_url, data=data)
print(res.status_code)
print(res.text)
