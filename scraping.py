import re
import json
from config import *
from requests import Session
from abc import ABC, abstractmethod
from database import DataBaseController


# Subsystems
# ==========================================================================
# ==========================================================================


class Scraping(ABC):

    @abstractmethod
    def scraping(self):
        pass


class ScrapingLikePost(Scraping):

    def __init__(self, session: Session, post_url, cookie):
        self.session = session
        self.post_url = post_url
        self.cookie = cookie

    def scraping(self):
        response = self.session.get(f'{INSTAGRAM_URL}/p/{self.post_url}/?__a=1')
        json_response = json.loads(response.text)
        id = json_response['graphql']['shortcode_media']['id']
        like_url = f'{INSTAGRAM_URL}/web/likes/{id}/like/'
        self.session.headers.update({'X-CSRFToken': self.cookie['csrftoken'],})
        result = self.session.post(like_url)
        print(result)
        print('Like successful.')


class ScrapingGetUserProfile(Scraping):

    def __init__(self, session: Session, username: str):
        self.session = session
        self.username = username

    def scraping(self):
        response = self.session.get(f'{INSTAGRAM_URL}/{self.username}')
        extract = re.search(r'window._sharedData = (.+);</script>', str(response.text))
        response = json.loads(extract.group(1))
        result = response['entry_data']['ProfilePage'][0]['graphql']['user']
        return result


class ScrapingUserFollowers(Scraping):

    def __init__(self, session: Session, ds_user_id):
        self.session = session
        self.ds_user_id = ds_user_id
  
    def scraping(self):
        followers_list = []

        query_hash = '56066f031e6239f35a904ac20c9f37d9'
        variables = {
            "id":self.ds_user_id,
            "include_reel":False,
            "fetch_mutual":False,
            "first":50
        }
        query_route = f'{INSTAGRAM_URL}/graphql/query/'
        response = self.session.get(query_route, params={'query_hash': query_hash, 'variables': json.dumps(variables)})
        response = json.loads(response.text)
        for edge in response['data']['user']['edge_followed_by']['edges']:
            followers_list.append(edge['node'])

        while response['data']['user']['edge_followed_by']['page_info']['has_next_page']:
            variables['after'] = response['data']['user']['edge_followed_by']['page_info']['end_cursor']


            response = self.session.get(query_route, params={'query_hash': query_hash, 'variables': json.dumps(variables)})
            while response.status_code != 200:
                response = self.session.get(query_route, params={'query_hash': query_hash, 'variables': json.dumps(variables)})

            response = json.loads(response.text)

            for edge in response['data']['user']['edge_followed_by']['edges']:
                followers_list.append(edge['node'])

        print(followers_list)

      

class ScrapingUserFollowing(Scraping):
    def __init__(self, session: Session, ds_user_id):
        self.session = session
        self.ds_user_id = ds_user_id
  
    def scraping(self):
        follows_list = []

        query_hash = 'c56ee0ae1f89cdbd1c89e2bc6b8f3d18'
        variables = {
            "id":self.ds_user_id,
            "include_reel":False,
            "fetch_mutual":False,
            "first":50
        }

        query_route = f'{INSTAGRAM_URL}/graphql/query/'
        response = self.session.get(query_route, params={'query_hash': query_hash, 'variables': json.dumps(variables)})
        while response.status_code != 200:
            response = self.session.get(query_route, params={'query_hash': query_hash, 'variables': json.dumps(variables)})

        response = json.loads(response.text)

        for edge in response['data']['user']['edge_follow']['edges']:
            follows_list.append(edge['node'])

        while response['data']['user']['edge_follow']['page_info']['has_next_page']:
            variables['after'] = response['data']['user']['edge_follow']['page_info']['end_cursor']

            response = self.session.get(query_route, params={'query_hash': query_hash, 'variables': json.dumps(variables)})
            while response.status_code != 200:
                response = self.session.get(query_route, params={'query_hash': query_hash, 'variables': json.dumps(variables)})

            response = json.loads(response.text)

            for edge in response['data']['user']['edge_follow']['edges']:
                follows_list.append(edge['node'])

        print(follows_list)


class ScrapingUser(Scraping):
    def __init__(self, data_base_file_name: str, table_name: str, session: Session, tag_name: str):
        self.data_base_file_name = data_base_file_name
        self.session = session
        self.tag_name = tag_name
        self.table_name = table_name
        self.db = DataBaseController(self.data_base_file_name)

    def scraping(self, url = None):
        if url:
            scraping_url = url
            print(scraping_url)
            print('URL NEXT ......')
        else:
            scraping_url = f'{INSTAGRAM_URL}/explore/tags/{self.tag_name}/?__a=1'

        hashtag_response = self.session.get(scraping_url)
        json_hashtag_response = json.loads(hashtag_response.text)
        next_max_id = json_hashtag_response['data']['recent']['next_max_id']

        section = json_hashtag_response['data']['recent']['sections']

        for item_section in section:
            medias = item_section['layout_content']['medias']
            for media in medias:
                user = media['media']['user']
                pk = user['pk']
                username = user['username']
                full_name = user['full_name']
                profile_pic_url = user['profile_pic_url']
                self.db.processor(table_name=self.table_name, pk=pk, username=username, full_name=full_name, profile_pic_url=profile_pic_url)

        while True:
            self.scraping(url=f'{INSTAGRAM_URL}/explore/tags/{self.tag_name}/?__a=1&max_id={next_max_id}')
