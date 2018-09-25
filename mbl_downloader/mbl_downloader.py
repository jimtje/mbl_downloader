# -*- coding: utf-8 -*-

"""Main module."""

import trio
import asks
import bs4
import sys
import time



class MBLDownloader(object):
    """


    """
    auth_url = 'http://mblservices.org/amember/login'

    def __init__(self, username, password):
        """


        :param username:
        :param password:
        """
        self.username = username
        self.password = password
        self.login_cookie = None
        self.php_cookie = None
        self.api_session = None
        self.expiry = None
        asks.init('trio')
        self._authorize()


    @property
    def authorized(self):
        """

        :return:
        """
        if self.login_cookie is None:
            return False
        else:
            return True

    async def _authorize(self):
        """

        :return:
        """
        login_data = {
            'amember_login': self.username,
            'amember_pass': self.password,
            'login_attempt_id': str(time.time()).split('.')[0]
        }
        r = await asks.post(self.auth_url, data=login_data)
        async with r.headers['Content-Type'] as ct:
            if ct == 'text/html; charset=utf-8':
                result_soup = bs4.BeautifulSoup(r.text)
                self.php_cookie = r.history[0].cookies[0]
                self.login_cookie = r.history[0].cookies[1]
                self.api_session = asks.Session(persist_cookies=True)
                self.expiry = result_soup.find('ul', attrs={
                    'id': 'member-subscriptions'
                }).text.strip().replace('\n', '').replace('  ', '')
            else:
                raise Exception

    async def dl_file(self, download_link):
        if self.authorized:
            _data = {'link': download_link, 'premium_acc': 'on'}
            _url = 'https://mblservices.org/amember/downloader/downloader/app/index.php'
            _cookies = {self.php_cookie.name:self.php_cookie.value, self.login_cookie.name:self.login_cookie.value}
            r = await self.api_session.post(_url, data=_data, cookies=_cookies)
            try:
                _soup = bs4.BeautifulSoup(r.text)
                _link = _soup.find('input', attrs={'name': 'link'})['value']
                _path = _soup.find('input', attrs={'name': 'path'})['value']
                _host = _soup.find('input', attrs={'name': 'host'})['value']
                _referer = _soup.find('input', attrs={'name': 'referer'})['value']
                _filename = _soup.find('input', attrs={'name': 'filename'})['value']
                _data2 = {'link': _link, 'path': _path, 'host': _host, 'filename': _filename, 'referer': _referer}
                _res = await self.api_session.post(_url, data=_data2, cookies=_cookies)
                _soup2 = bs4.BeautifulSoup(_res.text)
                _file_name = _soup2.find('a').contents[0]
                _dl = _soup2.find('a')['download']
                return await self.api_session.get(_dl, cookies=_cookies, stream=True)
            except:
                raise











