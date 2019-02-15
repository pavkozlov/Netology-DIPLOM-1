import json

import requests
from urllib.parse import urlencode
import time

TOKEN = '4b2ec088cb1369e042a4c055e0ae9708e3188bf85379dd727fc5edf0d39bffb90498cfc705f6ff5a23d9f'


def get_access_token_link():
    app_id = 6854739
    auth_url = 'https://oauth.vk.com/authorize'
    auth_data = {
        'client_id': app_id,
        'display': 'page',
        'scope': 'status, friends',
        'response_type': 'token',
        'v': '5.92',
        'redirect_uri': ''
    }
    url = '?'.join((auth_url, urlencode(auth_data)))
    print(url)


class User:
    def __init__(self, slug):
        self.params = {
            'v': 5.92,
            'access_token': TOKEN
        }
        self.id = self.get_id(slug)
        self.group_list = self.get_self_group_list()
        self.friends_list = self.get_friends_list()
        self.params['user_id'] = self.id

    def send_request(self, method, params):
        return requests.get(f'https://api.vk.com/method/{method}', params=params)

    def get_id(self, slug):
        params = self.params
        params['user_ids'] = slug
        if str(slug).isdigit():
            return slug
        else:

            try:
                get_response = self.send_request('users.get', params).json()['response'][0]['id']
            except KeyError:
                time.sleep(2)
                get_response = self.send_request('users.get', params).json()['response'][0]['id']
            return get_response

    def get_self_group_list(self):
        params = self.params
        params['user_id'] = self.id
        try:
            get_response = self.send_request('groups.get', params).json()['response']['items']
        except KeyError:
            time.sleep(2)
            get_response = self.send_request('groups.get', params).json()['response']['items']
        return get_response

    def get_friends_list(self):
        try:
            get_response = self.send_request('friends.get', self.params).json()['response']['items']
        except KeyError:
            time.sleep(2)
            get_response = self.send_request('friends.get', self.params).json()['response']['items']
        return ','.join(str(i) for i in get_response)

    def return_not_unique_groups(self, group_id, user_ids):
        params = self.params
        params['group_id'] = group_id
        params['user_ids'] = user_ids
        if params.get('user_id'):
            del params['user_id']
        try:
            dict_list = self.send_request('groups.isMember', params).json()['response']
        except KeyError:
            time.sleep(2)
            dict_list = self.send_request('groups.isMember', params).json()['response']
        not_unique = []
        for element in dict_list:
            if element['member'] == 1:
                not_unique.append(group_id)
        return list(set(not_unique))

    def check_all_groups(self):
        res = []
        for group in self.group_list:
            res += self.return_not_unique_groups(group, self.friends_list)
        result = set(self.group_list) - (set(res))
        return list(result)

    def get_spy_result(self):
        my_list = list()
        for i in self.check_all_groups():
            params = self.params
            params['group_ids'] = i
            params['fields'] = 'members_count'
            try:
                get_response = self.send_request('groups.getById', params).json()['response'][0]
            except KeyError:
                time.sleep(2)
                get_response = self.send_request('groups.getById', params).json()['response'][0]
            data = {'name': get_response['name'], 'gid': get_response['id'],
                    'members_count': get_response['members_count']}
            my_list.append(data)
        with open(f'{self.id}-groups.json', 'a', encoding='utf-8') as file:

            json.dump(my_list, file, ensure_ascii=False, indent=3)


# get_access_token_link()
test = User(19541420)
test2 = User('eshmargunov')

test2.get_spy_result()
test.get_spy_result()
