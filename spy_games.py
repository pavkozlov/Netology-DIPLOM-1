import json
import requests
from urllib.parse import urlencode
import time
import sys

TOKEN = '42f5a9dabd0bba3cb830af3f01c806c36b5b067c86247ae32e7252bdbf205ee0fe50633a7b9cb991f0632'
PARAMS = {
    'v': 5.92,
    'access_token': TOKEN
}


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
        self.params = PARAMS
        self.id = self.get_id(slug)
        self.group_list = self.get_self_group_list()
        self.friends_list = self.get_friends_list()
        self.params['user_id'] = self.id

    def send_request(self, method, params):
        res = requests.get(f'https://api.vk.com/method/{method}', params=params)
        try:
            res.json()['error']
            print('Ограничение по запросам. Ждём...')
            time.sleep(2)
            print('Работаем!')
            return requests.get(f'https://api.vk.com/method/{method}', params=params)
        except KeyError:
            return res

    def get_id(self, slug):
        params = self.params
        params['user_ids'] = slug
        if str(slug).isdigit():
            return slug
        else:
            get_response = self.send_request('users.get', params).json()['response'][0]['id']
            return get_response

    def get_self_group_list(self):
        params = self.params
        params['user_id'] = self.id
        get_response = self.send_request('groups.get', params).json()['response']['items']
        return get_response

    def get_friends_list(self):
        get_response = self.send_request('friends.get', self.params).json()['response']['items']
        return ','.join(str(i) for i in get_response)

    def return_not_unique_groups(self, group_id, user_ids):
        params = self.params
        params['group_id'] = group_id
        params['user_ids'] = user_ids
        if params.get('user_id'):
            del params['user_id']
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
            get_response = self.send_request('groups.getById', params).json()['response'][0]
            data = {'name': get_response['name'], 'gid': get_response['id'],
                    'members_count': get_response['members_count']}
            my_list.append(data)
        with open(f'{self.id}-groups.json', 'a', encoding='utf-8') as file:
            json.dump(my_list, file, ensure_ascii=False, indent=3)


if __name__ == '__main__':
    get_access_token_link()
    if len(sys.argv) > 1:
        user = User(sys.argv)
        user.get_spy_result()
    else:
        test = User(19541420)
        test.get_spy_result()
