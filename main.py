import os
import json
import requests
from datetime import datetime
from scraping import (
    ScrapingUser, 
    ScrapingUserFollowers, 
    ScrapingUserFollowing,
    ScrapingGetUserProfile
    )
from config import *


# Facade
# ==========================================================================
# ==========================================================================


class InstagramScrapingManager:

    def __init__(self, **kwargs):
        self.link = kwargs['link']
        self.username = kwargs['username']
        self.password = kwargs['password']
        self.login_url = kwargs['login_url']
        self.session = requests.Session()
        self.login_check()

        ds_user_id = ScrapingGetUserProfile(self.session, kwargs['username_for_show_follows']).scraping()['id']

        self.scraping_user_followers = ScrapingUserFollowers(self.session, ds_user_id)
        self.scraping_user_followings = ScrapingUserFollowing(self.session, ds_user_id)
        
        self.scraping_user = ScrapingUser(kwargs['data_base_file_name'], 'users', self.session, kwargs['tag_name'])

    def start_scraping(self):
        self.scraping_user_followers.scraping()
        print('''
        ###################################################
        ###################################################''')
        print('\n\n')

        self.scraping_user_followings.scraping()
        print('''
        ###################################################
        ###################################################''')
        print('\n\n')

        self.scraping_user.scraping()
        
    def login(self):
        time = int(datetime.now().timestamp())
        response = requests.get(self.link)
        csrf = response.cookies.get_dict()['ig_did']
        payload = {
            'username': self.username,
            'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{time}:{self.password}',
            'queryParams': {},
            'optIntoOneTap': 'false'
            }
        login_header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": LOGIN_LINK,
            "x-csrftoken": csrf
            }
        login = self.session.post(self.login_url, data=payload, headers=login_header)
        return login

    def login_check(self):

        if os.path.getsize('cookie.txt') == 0:
            login = self.login()
            login_json = json.loads(login.text)
            print(login_json)
            cookies = login.cookies
            cookie_jar = cookies.get_dict()
            cookie_json = json.dumps(cookie_jar) 
            file_cookies = open('cookie.txt', 'w')
            file_cookies.write(cookie_json)
            file_cookies.close()

        else:
            print('**************************************')
            cookie_file = open('cookie.txt', 'r')
            cookie = cookie_file.read()
            cookie = json.loads(cookie)
            self.session.cookies.update(cookie)


# Client
# ==========================================================================
# ==========================================================================


def client_code(scraping_manager: InstagramScrapingManager):
    scraping_manager.start_scraping()


if __name__ == '__main__':

    client_code(InstagramScrapingManager(
        username=USERNAME_FOR_LOGIN,
        password=PASSWORD_FOR_LOGIN, 
        link=LOGIN_LINK, 
        login_url=LOGIN_URL,
        data_base_file_name=DATA_BASE_FILE_NAME,
        tag_name=TAG_NAME,
        username_for_show_follows=USERNAME_FOR_SHOW_FOLLOWS
        ))
